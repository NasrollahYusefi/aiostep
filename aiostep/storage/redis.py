try:
    import json
    from enum import Enum
    from typing import Callable
    from redis.asyncio.client import Redis
    from redis.typing import ExpiryT

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
        def __init__(self, cache: Redis, ex: ExpiryT | None = None) -> None:
            """Initialize the Redis storage.

            Args:
                cache (Redis): Redis client instance
                ex (ExpiryT | None, optional): Expiration time for all keys. 
                    Defaults to None.
            """
            self.cache = cache
            self.ex = ex
        
        def _get_key(self, user_id: int | str) -> str:
            """Generate Redis key for a user.

            Args:
                user_id (int | str): ID of the user

            Returns:
                str: Redis key
            """
            return f"state:{user_id}"

        async def set_state(
            self, 
            user_id: int | str, 
            state: str | Enum, 
            callback: Callable | None = None, 
            chat_id: int | str = None,
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

            state_context = StateContext(
                current_state=state,
                callback=callback_name,
                chat_id=chat_id
            )
            
            state_data = {
                "current_state": state_context.current_state,
                "data": state_context.data,
                "chat_id": state_context.chat_id,
                "callback": callback_name
            }
            
            await self.cache.set(
                self._get_key(user_id),
                json.dumps(state_data),
                ex=self.ex
            )
        
        async def get_state(self, user_id: int | str, default: Any = None) -> StateContext | None:
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
        
        async def delete_state(self, user_id: int | str, default: Any = None) -> StateContext | None:
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
            user_id: int | str, 
            data: dict[str, Any],
        ) -> None:
            """Set data for a user's state.

            This method completely replaces any existing data.

            Args:
                user_id (int | str): ID of the user
                data (dict[str, Any]): Data to store
            """
            state_key = self._get_key(user_id)
            current_data = await self.cache.get(state_key)
            
            if current_data:
                state_data = json.loads(current_data)
                state_data["data"] = data
            else:
                state_data = {
                    "current_state": None,
                    "data": data,
                    "chat_id": None,
                    "callback": None
                }
            
            await self.cache.set(
                state_key,
                json.dumps(state_data),
                ex=self.ex
            )
        
        async def get_data(self, user_id: int | str) -> dict[str, Any] | None:
            """Get data for a user's state.

            Args:
                user_id (int | str): ID of the user

            Returns:
                dict[str, Any] | None: The stored data or None if not found
            """
            data = await self.cache.get(self._get_key(user_id))
            if not data:
                return None
                
            state_data = json.loads(data)
            return state_data.get("data")
        
        async def update_data(self, user_id: int | str, data: dict[str, Any]) -> None:
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
            state_key = self._get_key(user_id)
            current_data = await self.cache.get(state_key)
            
            if current_data:
                state_data = json.loads(current_data)
                if state_data.get("data", None) is None:
                    state_data["data"] = {}
                state_data["data"].update(data)
            else:
                state_data = {
                    "current_state": None,
                    "data": data,
                    "chat_id": None,
                    "callback": None
                }
            
            await self.cache.set(
                state_key,
                json.dumps(state_data),
                ex=self.ex
            )
        
        async def clear_data(self, user_id: int | str) -> None:
            """Clear all data for a user's state.

            Args:
                user_id (int | str): ID of the user
            """
            state_key = self._get_key(user_id)
            current_data = await self.cache.get(state_key)
            
            if current_data:
                state_data = json.loads(current_data)
                state_data["data"] = None
                await self.cache.set(state_key, json.dumps(state_data), ex=self.ex)

except ImportError:
    class RedisStateStorage:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Redis package is not installed. "
                "To use RedisStateStorage, install package with redis support: "
                "pip install aiostep[redis]"
            )
