from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Union, Optional, Dict


class BaseAsyncStorage(ABC):
    """
    This is base class for Storage classes like MemoryStateStorage and RedisStateStorage
    """

    @abstractmethod
    async def set_state(self, key: Union[str, int], state: Union[str, Enum]) -> None:
        """
        use this method to set state for a key
        """
        raise NotImplementedError

    @abstractmethod
    async def get_state(self, key: Union[str, int], default: Optional[Any] = None) -> Optional[str]:
        """
        use this method to get current state of a key

        return default if not found
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_state(self, key: Union[str, int], default: Optional[Any] = None) -> Optional[str]:
        """
        use this method to delete and get current state of a key
        
        return default if not found
        """
        raise NotImplementedError
    
    @abstractmethod
    async def set_data(self, key: Union[str, int], data: Dict[Any, Any]) -> None:
        """
        use this method to set data for a key
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_data(self, key: Union[str, int]) -> Dict[Any, Any]:
        """
        use this method to get current data of a key
        """
        raise NotImplementedError

    @abstractmethod
    async def update_data(self, key: int, data: Dict[Any, Any]) -> None:
        """
        use thid method to update current data of a key
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete_data(self, key: Union[str, int], default: Optional[Any] = None) -> Optional[Dict[Any, Any]]:
        """
        use this method to clear and get current data of a key
        """
        raise NotImplementedError
