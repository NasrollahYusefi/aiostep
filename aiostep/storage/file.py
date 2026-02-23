import os
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

from qsave import QuickSave

from .base import BaseStorage, StateContext


class FileStateStorage(BaseStorage):
    """File-based storage implementation for managing bot states.

    This class provides a file-based storage solution for managing bot states
    and their associated data. Suitable for applications where persistence
    across sessions or restarts is required.

    Args:
        path (str | os.PathLike): Path to the file used for storing states and data.
    """

    def __init__(
        self, path: Union[str, os.PathLike], ex: Optional[float] = None, **kwargs
    ) -> None:
        """Initialize the file storage.

        Args:
            path (str | os.PathLike): File path to store states and data persistently.
            ex (float | None): expiry time for objects. pass in seconds.
        """
        self.cache = QuickSave(path=path, **kwargs)
        self.ex = ex

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

    def set_state(
        self,
        user_id: Union[int, str],
        state: Union[str, Enum],
        callback: Optional[Callable[..., Any]] = None,
        chat_id: Optional[Union[int, str]] = None,
        ex: Optional[float] = None,
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
        ex = ex or self.ex

        state_data = {
            "current_state": state,
            "chat_id": chat_id,
            "callback": callback_name,
        }
        ex = ex or self.ex
        if ex:
            state_data["expire"] = time.time() + ex
        state_key = self._get_key(user_id)

        with self.cache.session() as session:
            session[state_key] = state_data

    def get_state(
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
        with self.cache.session(commit_on_expire=False) as session:
            data = session.get(self._get_key(user_id))

            if not data:
                return default
            expire = data.pop("expire", None)
            if expire and (expire < time.time()):
                session.pop(self._get_key(user_id))
                session.commit()
                return default

        return StateContext(**data)

    def delete_state(
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

        with self.cache.session() as session:
            data = session.pop(state_key)

        if not data:
            return default
        if data.get("expire") and (data.get("expire") < time.time()):
            return default

        return StateContext(**data)

    def set_data(
        self,
        user_id: Union[int, str],
        data: Optional[Dict[Any, Any]] = None,
        ex: Optional[float] = None,
        **kwargs,
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

        with self.cache.session() as session:
            ex = ex or self.ex
            new_data = {
                "data": data_payload,
            }
            if ex:
                new_data["ex"] = time.time() + ex
            session[data_key] = new_data

    def get_data(
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
        with self.cache.session(commit_on_expire=False) as session:
            data = session.get(self._get_data_key(user_id))

            if not data:
                return default
            if data.get("ex") and (data.get("ex") < time.time()):
                session.pop(self._get_data_key(user_id))
                session.commit()
                return default

        return data["data"]

    def update_data(
        self,
        user_id: Union[int, str],
        data: Optional[Dict[Any, Any]] = None,
        ex: Optional[float] = None,
        **kwargs,
    ) -> None:
        """Update data for a user.

        This method updates existing data with new values, similar to dict.update().
        Existing keys will be updated, and new keys will be added.

        Args:
            user_id (int | str): ID of the user
            data (dict[str, Any]): Data to update

        Example:
            >>> # Existing data: {"name": "John"}
            >>> storage.update_data(user_id, {"age": 25})
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

        with self.cache.session() as session:
            current_data = session.get(data_key)

            if current_data:
                current_data["data"].update(data_payload)
                if ex:
                    current_data["ex"] = time.time() + ex
            else:
                ex = ex or self.ex
                new_data = {
                    "data": data_payload,
                }
                if ex:
                    new_data["ex"] = time.time() + ex
                session[data_key] = new_data

    def delete_data(
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
        with self.cache.session() as session:
            data = session.pop(data_key, default)

        if isinstance(data, dict):
            if data.get("expire") and (data.get("expire") < time.time()):
                return default

        return data
