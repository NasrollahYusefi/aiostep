import os
from qsave.asyncio import AsyncQuickSave

from enum import Enum
from typing import Callable, Any, Union, Dict, Optional
from copy import deepcopy

from .base import BaseAsyncStorage
from ..storage.base import StateContext


class AsyncFileStateStorage(BaseAsyncStorage):
    """File-based storage implementation for managing bot states.

    This class provides a file-based storage solution for managing bot states
    and their associated data. Suitable for applications where persistence
    across sessions or restarts is required.

    Args:
        path (str | os.PathLike): Path to the file used for storing states and data.
    """

    def __init__(self, path: Union[str, os.PathLike], **kwargs) -> None:
        """Initialize the file storage.

        Args:
            path (str | os.PathLike): File path to store states and data persistently.
        """
        self.cache = AsyncQuickSave(path=path, **kwargs)

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

        callback_name = callback.__name__ if callback else None

        state_data = {
            "current_state": state,
            "chat_id": chat_id,
            "callback": callback_name
        }
        state_key = self._get_key(user_id)

        async with self.cache.session() as session:
            session[state_key] = state_data

    async def get_state(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[StateContext]:
        """Get the state context for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if state doesn't exist. 
                Defaults to None.

        Returns:
            StateContext | None: The state context or default value
        """
        async with self.cache.session(commit_on_expire=False) as session:
            data = session.get(self._get_key(user_id))

        if not data:
            return default

        return StateContext(**data)

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

        async with self.cache.session() as session:
            data = session.pop(state_key)

        if not data:
            return default

        return StateContext(**data)

    async def set_data(
        self, 
        user_id: Union[int, str], 
        data: Dict[Any, Any],
    ) -> None:
        """Set data for a user.

        This method completely replaces any existing data.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to store
        """
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_key = self._get_data_key(user_id)

        async with self.cache.session() as session:
            session[data_key] = data

    async def get_data(self, user_id: Union[int, str]) -> Optional[Dict[Any, Any]]:
        """Get data for a user.

        Args:
            user_id (int | str): ID of the user

        Returns:
            dict[str, Any] | None: The stored data or None if not found
        """
        async with self.cache.session(commit_on_expire=False) as session:
            data = session.get(self._get_data_key(user_id))

        if not data:
            return None

        return data

    async def update_data(self, user_id: Union[int, str], data: Dict[Any, Any]) -> None:
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
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dict, got {type(data)}")

        data_key = self._get_data_key(user_id)

        async with self.cache.session() as session:
            current_data = session.get(data_key)

            if current_data:
                current_data.update(data)
            else:
                state_data = deepcopy(data)
                session[data_key] = state_data

    async def delete_data(self, user_id: Union[int, str], default: Optional[Any] = None) -> Optional[Dict[Any, Any]]:
        """Clear and get all data for a user.

        Args:
            user_id (int | str): ID of the user
            default (Any, optional): Default value if data doesn't exist. 
                Defaults to None.

        Returns:
            Dict | None: The deleted data or default value
        """
        data_key = self._get_data_key(user_id)
        async with self.cache.session() as session:
            data = session.pop(data_key, default)

        return data
