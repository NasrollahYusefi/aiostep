import asyncio
import typing

try:
    from aiogram import BaseMiddleware, types
    aiogram_installed = True
except ImportError:
    class BaseMiddleware:
        pass
    aiogram_installed = False

from ..functions import MetaStore, root


class Listen(BaseMiddleware):
    """
    aiogram middleware to listen for steps.

    supported handlers:
        - `MessageHandler`
        - `CallbackQueryHandler`
        - `ChatJoinRequestHandler`
        - `ChatMemberUpdatedHandler`
        - `EditedMessageHandler`

    Example::

        dp = Dispatcher()
        dp.message.outer_middleware(aiostep.Listen())
    """

    def __init__(
        self,
        store: typing.Optional[MetaStore] = None
    ) -> None:
        if not aiogram_installed:
            raise ImportError(
                "aiogram package is not installed. "
                "install package: "
                "pip install aiogram"
            )
        self.store = store or root

    async def __call__(
        self,
        handler: typing.Callable[[types.TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: types.TelegramObject,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        fn = None

        try:
            fn = await self.store.pop_item(event.from_user.id)
        except (KeyError, AttributeError):
            try:
                chat_id = event.message.chat.id if isinstance(event, types.CallbackQuery) else event.chat.id
                fn = await self.store.pop_item(chat_id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(event)
                return
            await fn(event)
            return

        return await handler(event, data)
