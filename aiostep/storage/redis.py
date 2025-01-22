import json
from copy import deepcopy
from enum import Enum
from typing import Callable, Union, Any, Dict, Optional

try:
    from redis.asyncio.client import Redis
    from redis.typing import ExpiryT
    redis_installed = True
except ImportError:
    redis_installed = False

from typing import Any, Callable

from .base import BaseStorage, StateContext


class RedisStateStorage(BaseStorage):
    """Redis-based storage implementation for managing bot states.

    This class provides a Redis-backed storage solution for managing bot states
    and their associated data. Suitable for production use and distributed systems.

    Note:
        Requires redis package to be installed:
        pip install your-package[redis]

    Args:
        cache (Redis): Redis client instance
        ex (ExpiryT | None): Optional expiration time for all keys
    """
    def __init__(self, cache: "Redis", ex: "ExpiryT | None" = None) -> None:
        """Initialize the Redis storage.

        Args:
            cache (Redis): Redis client instance
            ex (ExpiryT | None, optional): Expiration time for all keys. 
                Defaults to None.
        """
        if not redis_installed:
            raise ImportError(
                "Redis package is not installed. "
                "To use RedisStateStorage, install package with redis support: "
                "pip install aiostep[redis]"
            )

        self.cache = cache
        self.ex = ex

    def _get_key(self, user_id: Union[int, str]) -> str:
        """Generate Redis key for a user.

        Args:
            user_id (int | str): ID of the user

        Returns:
            str: Redis key
        """
        return f"state:{user_id}"

    def _get_data_key(self, user_id: Union[int, str]) -> str:
        """Generate Redis key for a user.

        Args:
            user_id (int | str): ID of the user

        Returns:
            str: Redis key
        """
        return f"data:{user_id}"

    async def set_state(
        self, 
        user_id: Union[int, str], 
        state: Union[str, Enum], 
        callback: Optional[Callable[..., Any]] = None, 
        chat_id: Optional[Union[int, str]] = None,
    ) -> None:
        """Set the state for a user.

        Args:
            user_id (int | str): ID of the user
            state (str | Enum): State to set
            callback (Callable | None, optional): Callback function. Defaults to None.
            chat_id (int | str, optional): Chat ID. Defaults to None.
        """
        if chat_id is None:
            chat_id = user_id

        if isinstance(state, Enum):
            state = state.name

        callback_name = callback.__name__ if callback else None

        state_data = {
            "current_state": state,
            "chat_id": chat_id,
            "callback": callback_name
        }

        await self.cache.set(
            self._get_key(user_id),
            json.dumps(state_data),
            ex=self.ex
        )

    async def get_state(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[StateContext]:
        """Get the state context for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist. 
                Defaults to None.

        Returns:
            StateContext | None: The state context or default value
        """
        data = await self.cache.get(self._get_key(user_id))
        if not data:
            return default

        state_data = json.loads(data)
        return StateContext(**state_data)

    async def delete_state(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[StateContext]:
        """Delete the state for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist. 
                Defaults to None.

        Returns:
            StateContext | None: The deleted state context or default value
        """
        state_key = self._get_key(user_id)
        data = await self.cache.get(state_key)
        await self.cache.delete(state_key)

        if not data:
            return default

        state_data = json.loads(data)
        return StateContext(**state_data)

    async def set_data(
        self, 
        user_id: Union[int, str],
        data: Dict[Any, Any],
    ) -> None:
        """Set data for a user's state.

        This method completely replaces any existing data.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to store
        """
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_key = self._get_data_key(user_id)

        await self.cache.set(
            data_key,
            json.dumps(data),
            ex=self.ex
        )

    async def get_data(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[Dict[Any, Any]]:
        """Get data for a user's state.

        Args:
            user_id (int | str): ID of the user

        Returns:
            dict[str, Any] | None: The stored data or None if not found
        """
        data = await self.cache.get(self._get_data_key(user_id))
        if not data:
            return default

        state_data = json.loads(data)
        return state_data

    async def update_data(self, user_id: Union[int, str], data: Dict[Any, Any]) -> None:
        """Update data for a user's state.

        This method updates existing data with new values, similar to dict.update().
        Existing keys will be updated, and new keys will be added.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to update
        
        Example:
            >>> # Existing data: {"name": "John"}
            >>> await storage.update_data(user_id, {"age": 25})
            >>> # Result: {"name": "John", "age": 25}
        """
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_key = self._get_data_key(user_id)
        current_data = await self.cache.get(data_key)

        if current_data:
            try:
                state_data = json.loads(current_data)
                state_data.update(data)
            except json.JSONDecodeError:
                state_data = deepcopy(data)
        else:
            state_data = deepcopy(data)

        await self.cache.set(
            data_key,
            json.dumps(state_data),
            ex=self.ex
        )

    async def delete_data(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[Dict[Any, Any]]:
        """Clear and get all data for a user's state.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if data doesn't exist. 
                Defaults to None.

        Returns:
            Dict | None: The deleted data or default value
        """
        data_key = self._get_data_key(user_id)
        data = await self.cache.get(data_key)
        await self.cache.delete(data_key)

        if not data:
            return default

        data = json.loads(data)
        return data
