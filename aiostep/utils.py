from enum import Enum

from .asyncio import BaseAsyncStorage
from .storage import BaseStorage
from aiogram import types
from aiogram.filters import Filter


class IsState(Filter):
    """
    A filter to validate the current state of a user using aiostep's state management.

    This filter checks if the user's current state matches the given `state`. It uses the `state_manager` 
    to retrieve the user's state and validates it against the provided `state`.

    Args:
        state (str | Enum): The target state to match. If an `Enum` is provided, its `name` will be used.
        state_manager (BaseStorage | BaseAsyncStorage): 
            An instance of aiostep's asynchronous state manager for retrieving and validating user states.

    Methods:
        __call__(event): Processes an input event and validates the user's current state.
            - event (types.Message | types.CallbackQuery): The input event to validate.
            - Returns (bool): True if the user's state matches the target state, False otherwise.
    """

    def __init__(self, state: str | Enum, state_manager: BaseStorage | BaseAsyncStorage) -> None:
        self.state = state.name if isinstance(state, Enum) else state
        self.state_manager = state_manager
        if isinstance(state_manager, BaseStorage):
            self.sync = True
        else:
            self.sync = False

    async def __call__(
        self,
        event: types.Message | types.CallbackQuery
    ) -> bool:
        if self.sync:
            current_state = self.state_manager.get_state(event.from_user.id)
        else:
            current_state = await self.state_manager.get_state(event.from_user.id)
        if not current_state:
            return False

        chat_id = event.message.chat.id if isinstance(event, types.CallbackQuery) else event.chat.id

        return (current_state.current_state == self.state) and (current_state.chat_id == chat_id)
