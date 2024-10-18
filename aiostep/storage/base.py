from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class StateContext:
    """State context for storing bot states and related data.

    This class holds information about the current state of a conversation,
    associated data, callback function and chat ID.

    Attributes:
        current_state (Enum): Current state of the conversation
        data (dict[str, object]): Associated data with the state
        callback (Callable | None): Callback function or its name
        chat_id (int | str): ID of the chat
    """
    current_state: Enum = None
    data: dict[str, object] = None
    callback: Callable | None = None
    chat_id: int | str = None


class BaseStorage(ABC):
    """
    This is base class for Storage classes like MemoryStateStorage and RedisStateStorage
    """

    @abstractmethod
    async def set_state(self, key: str | int, state: str | Enum) -> None:
        """
        use this method to set state for a key
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_state(self, key: str | int, default: object | None = None) -> Optional[str]:
        """
        use this method to get current state of a key

        return default if not found
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete_state(self, key: int, default: str | None = None) -> Optional[str]:
        """
        use this method to delete and get current state of a key
        
        return default if not found
        """
        raise NotImplementedError
    
    @abstractmethod
    async def set_data(self, key: str | int, data: dict[str, object]) -> None:
        """
        use this method to set data for a key
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_data(self, key: str | int) -> dict[str, object]:
        """
        use this method to get current data of a key
        """
        raise NotImplementedError
    
    async def update_data(self, user_id: int, data: dict[str, object]) -> None:
        """
        use thid method to update current data of a key
        """
        raise NotImplementedError
    
    @abstractmethod
    async def clear_data(self, key: str | int) -> None:
        """
        use this method to clear current data of a key
        """
        raise NotImplementedError
