from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Union, Optional, Dict


@dataclass
class StateContext:
    """State context for storing bot states.

    This class holds information about the current state of a conversation,
    associated data, callback function and chat ID.

    Attributes:
        current_state (Enum): Current state of the conversation
        callback (Callable | None): Callback function or its name
        chat_id (int | str): ID of the chat
    """
    current_state: Optional[Enum] = None
    callback: Optional[Callable[..., Any]] = None
    chat_id: Optional[Union[int, str]] = None


class BaseStorage(ABC):
    """
    This is base class for Storage classes like MemoryStateStorage and RedisStateStorage
    """

    @abstractmethod
    def set_state(self, key: Union[str, int], state: Union[str, Enum]) -> None:
        """
        use this method to set state for a key
        """
        raise NotImplementedError

    @abstractmethod
    def get_state(self, key: Union[str, int], default: Optional[Any] = None) -> Optional[str]:
        """
        use this method to get current state of a key

        return default if not found
        """
        raise NotImplementedError

    @abstractmethod
    def delete_state(self, key: Union[str, int], default: Optional[Any] = None) -> Optional[str]:
        """
        use this method to delete and get current state of a key
        
        return default if not found
        """
        raise NotImplementedError
    
    @abstractmethod
    def set_data(self, key: Union[str, int], data: Dict[Any, Any]) -> None:
        """
        use this method to set data for a key
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_data(self, key: Union[str, int]) -> Dict[Any, Any]:
        """
        use this method to get current data of a key
        """
        raise NotImplementedError
    
    def update_data(self, key: int, data: Dict[Any, Any]) -> None:
        """
        use thid method to update current data of a key
        """
        raise NotImplementedError
    
    @abstractmethod
    def clear_data(self, key: Union[str, int]) -> None:
        """
        use this method to clear current data of a key
        """
        raise NotImplementedError
