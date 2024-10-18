from enum import Enum
from typing import Callable
from copy import deepcopy
from cachebox import BaseCacheImpl

from .base import BaseStorage, StateContext


class MemoryStateStorage(BaseStorage):
    """In-memory storage implementation for managing bot states.

    This class provides an in-memory storage solution for managing bot states
    and their associated data. Suitable for development or small applications
    where persistence isn't required.

    Args:
        cache (dict | None): Optional dictionary to use as storage. If None,
            an empty dictionary will be used.
    """

    def __init__(self, cache: BaseCacheImpl | dict | None = None) -> None:
        """Initialize the memory storage.

        Args:
            cache (dict | None, optional): Initial cache dictionary. Defaults to None.
        """
        self.cache = cache if cache is not None else {}
    
    async def set_state(self, user_id: int, state: str | Enum, callback: Callable | None = None, chat_id: int | str = None) -> None:
        """Set the state for a user.

        Args:
            user_id (int | str): ID of the user
            state (str | Enum): State to set
            callback (Callable | None, optional): Callback function. Defaults to None.
            chat_id (int | str, optional): Chat ID. Defaults to None.
        """
        if chat_id is None:
            chat_id = user_id
        self.cache[user_id] = StateContext(
            current_state=state,
            callback=callback,
            chat_id=chat_id
        )
    
    async def get_state(self, user_id: int, default: str | None = None) -> StateContext:
        """Get the state context for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist. 
                Defaults to None.

        Returns:
            StateContext | None: The state context or default value
        """
        return self.cache.get(user_id, default)
    
    async def delete_state(self, user_id: int, default: str | None = None) -> StateContext:
        """Delete the state for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist. 
                Defaults to None.

        Returns:
            StateContext | None: The deleted state context or default value
        """
        return self.cache.pop(user_id, default)
    
    async def set_data(self, user_id: int, data: dict[str, object]) -> None:
        """Set data for a user's state.

        This method completely replaces any existing data.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to store
        """
        state_context = self.cache.get(user_id)
        if state_context is None:
            state_context = StateContext()
            self.cache[user_id] = state_context
        state_context.data = deepcopy(data)
    
    async def get_data(self, user_id: int) -> dict[str, object] | None:
        """Get data for a user's state.

        Args:
            user_id (int | str): ID of the user

        Returns:
            dict[str, Any] | None: The stored data or None if not found
        """
        state_context = self.cache.get(user_id)
        return deepcopy(state_context.data) if state_context else None
    
    async def update_data(self, user_id: int, data: dict[str, object]) -> None:
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
        state_context = self.cache.get(user_id)
        if state_context is None:
            state_context = StateContext()
            self.cache[user_id] = state_context
        
        if state_context.data is None:
            state_context.data = {}
        
        state_context.data.update(deepcopy(data))
    
    async def clear_data(self, user_id: int) -> None:
        """Clear all data for a user's state.

        Args:
            user_id (int | str): ID of the user
        """
        state_context = self.cache.get(user_id)
        if state_context:
            state_context.data = None
