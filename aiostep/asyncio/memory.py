from copy import deepcopy
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

from cachebox import BaseCacheImpl, Cache, TTLCache

from ..storage.base import StateContext
from .base import BaseAsyncStorage


class AsyncMemoryStateStorage(BaseAsyncStorage):
    """In-memory storage implementation for managing bot states.

    This class provides an in-memory storage solution for managing bot states
    and their associated data. Suitable for development or small applications
    where persistence isn't required.

    Args:
        cache (dict | None): Optional dictionary to use as storage. If None,
            an empty dictionary will be used.
    """

    def __init__(
        self,
        cache: Optional[Union[BaseCacheImpl, dict]] = None,
        ex: Optional[float] = None,
    ) -> None:
        """Initialize the memory storage.

        Args:
            cache (dict | None, optional): Initial cache dictionary. Defaults to None.
            ex (float | None): expiry time for objects. pass in seconds.
        """
        if cache:
            self.cache = cache
        elif ex:
            self.cache = TTLCache(0, ex)
        else:
            self.cache = Cache(0)

    def _get_key(self, user_id: Union[int, str]) -> str:
        """Generate Cache key for a user.

        Args:
            user_id (int | str): ID of the user

        Returns:
            str: Cache key
        """
        return f"state:{user_id}"

    def _get_data_key(self, user_id: Union[int, str]) -> str:
        """Generate Cache key for a user.

        Args:
            user_id (int | str): ID of the user

        Returns:
            str: Cache key
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

        state_key = self._get_key(user_id)

        self.cache[state_key] = StateContext(
            current_state=state, callback=callback, chat_id=chat_id
        )

    async def get_state(
        self, user_id: Union[int, str], default: Optional[Any] = None
    ) -> Optional[StateContext]:
        """Get the state context for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist.
                Defaults to None.

        Returns:
            StateContext | None: The state context or default value
        """
        state_key = self._get_key(user_id)
        return self.cache.get(state_key, default)

    async def delete_state(
        self, user_id: Union[int, str], default: Optional[Any] = None
    ) -> Optional[StateContext]:
        """Delete the state for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist.
                Defaults to None.

        Returns:
            StateContext | None: The deleted state context or default value
        """
        state_key = self._get_key(user_id)
        return self.cache.pop(state_key, default)

    async def set_data(
        self, user_id: Union[int, str], data: Optional[Dict[Any, Any]] = None, **kwargs
    ) -> None:
        """Set data for a user.

        This method completely replaces any existing data.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to store
        """
        if data is not None and not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_payload = {}
        if data:
            data_payload.update(data)
        if kwargs:
            data_payload.update(kwargs)

        if not data_payload:
            raise ValueError("No data passed.")

        data_key = self._get_data_key(user_id)

        self.cache[data_key] = deepcopy(data_payload)

    async def get_data(
        self, user_id: Union[int, str], default: Optional[Any] = None
    ) -> Optional[Dict[Any, Any]]:
        """Get data for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if data doesn't exist.
                Defaults to None.

        Returns:
            dict[str, Any] | None: The stored data or None if not found
        """
        data_key = self._get_data_key(user_id)

        data_context = self.cache.get(data_key)
        return deepcopy(data_context) if data_context else default

    async def update_data(
        self, user_id: Union[int, str], data: Optional[Dict[Any, Any]] = None, **kwargs
    ) -> None:
        """Update data for a user.

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
        if data is not None and not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_payload = {}
        if data:
            data_payload.update(data)
        if kwargs:
            data_payload.update(kwargs)

        if not data_payload:
            raise ValueError("No data passed.")

        data_key = self._get_data_key(user_id)

        data_context: dict = self.cache.get(data_key)
        if data_context is None:
            self.cache[data_key] = deepcopy(data_payload)
        else:
            data_context.update(deepcopy(data_payload))

    async def delete_data(
        self, user_id: Union[int, str], default: Optional[Any] = None
    ) -> Optional[Dict[Any, Any]]:
        """Clear and get all data for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if data doesn't exist.
                Defaults to None.

        Returns:
            Dict | None: The deleted data or default value
        """
        data_key = self._get_data_key(user_id)
        return self.cache.pop(data_key, default)
