import asyncio
import typing

try:
    from telebot import types, SkipHandler
    from telebot.async_telebot import BaseMiddleware
    telebot_installed = True
except ImportError:
    class BaseMiddleware:
        pass

    telebot_installed = False

from ..functions import MetaStore, root


class Listen(BaseMiddleware):
    """
    telebot middleware to listen for steps.

    supported update types:
        - `message`
        - `callback_query`
        - `chat_join_request`
        - `chat_member`
        - `edited_message`

    Example::

        bot = TeleBot()
        bot.setup_middleware(Listen(update_types=["message", "callback_query"]))
    """
    def __init__(
        self,
        update_types: typing.Optional[typing.List[str]] = None,
        store: typing.Optional[MetaStore] = None
    ):
        if not telebot_installed:
            raise ImportError(
                "pyTelegramBotAPI package is not installed. "
                "install package: "
                "pip install pyTelegramBotAPI"
            )
        self.store = store or root
        self.update_sensitive = True
        self.update_types = update_types or ["message"]

    async def pre_process_message(self, message: "types.Message", data):
        fn = None

        try:
            fn = await self.store.pop_item(message.from_user.id)
        except (KeyError, AttributeError):
            try:
                fn = await self.store.pop_item(message.chat.id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(message)
                return SkipHandler()
            await fn(message)
            return SkipHandler()

    async def post_process_message(self, message: "types.Message", data, exception):
        pass

    async def pre_process_callback_query(self, call: "types.CallbackQuery", data):
        fn = None

        try:
            fn = await self.store.pop_item(call.from_user.id)
        except (KeyError, AttributeError):
            try:
                fn = await self.store.pop_item(call.message.chat.id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(call)
                return SkipHandler()
            await fn(call)
            return SkipHandler()

    async def post_process_callback_query(self, call: "types.CallbackQuery", data, exception):
        pass

    async def pre_process_edited_message(self, message: "types.Message", data):
        fn = None

        try:
            fn = await self.store.pop_item(message.from_user.id)
        except (KeyError, AttributeError):
            try:
                fn = await self.store.pop_item(message.chat.id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(message)
                return SkipHandler()
            await fn(message)
            return SkipHandler()

    async def post_process_edited_message(self, message: "types.Message", data, exception):
        pass

    async def pre_process_chat_join_request(self, join_request: "types.ChatJoinRequest", data):
        fn = None

        try:
            fn = await self.store.pop_item(join_request.from_user.id)
        except (KeyError, AttributeError):
            try:
                fn = await self.store.pop_item(join_request.chat.id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(join_request)
                return SkipHandler()
            await fn(join_request)
            return SkipHandler()

    async def post_process_chat_join_request(self, join_request: "types.ChatJoinRequest", data, exception):
        pass

    async def pre_process_chat_member(self, status: "types.ChatMemberUpdated", data):
        fn = None

        try:
            fn = await self.store.pop_item(status.from_user.id)
        except (KeyError, AttributeError):
            try:
                fn = await self.store.pop_item(status.chat.id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(status)
                return SkipHandler()
            await fn(status)
            return SkipHandler()

    async def post_process_chat_member(self, status: "types.ChatMemberUpdated", data, exception):
        pass
