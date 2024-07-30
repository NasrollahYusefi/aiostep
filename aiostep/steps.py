import asyncio
import typing
import functools
import cachebox

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

_MT = typing.Union[asyncio.Future, typing.Callable]


class MetaStore:
    async def set_item(self, key: int, value: _MT) -> None:
        """
        Stores key-value.
        """
        raise NotImplementedError

    async def pop_item(self, key: int) -> _MT:
        """
        Gives stored key-value.

        raise KeyError if not found.
        """
        raise NotImplementedError

    async def clear(self) -> typing.AsyncGenerator[_MT, None]:
        """
        Gives and clears all stored key-value.
        """
        raise NotImplementedError


class _RootStore(MetaStore):
    def __init__(self) -> None:
        self.cache = cachebox.Cache(0)

    async def set_item(self, key: int, value: _MT) -> None:
        self.cache[key] = value

    async def pop_item(self, key: int) -> _MT:
        return self.cache.pop(key)

    async def clear(self) -> typing.AsyncGenerator[_MT, None]:
        for k in self.cache.keys():
            yield self.cache.pop(k)


root = _RootStore()


def change_root_store(store: MetaStore) -> None:
    """
    changes root store.
    """
    global root
    root = store


class Listen(BaseMiddleware):
    """
    aiogram middleware to listen for steps.

    supported handlers:
        - `MessageHandler`
        - `CallbackQueryHandler`
        - `ChatJoinRequestHandler`
        - `ChatMemberUpdatedHandler`
        - `ChosenInlineResultHandler`
        - `EditedMessageHandler`
        - `InlineQueryHandler`

    Example::

        dp = Dispatcher()
        dp.message.outer_middleware(aiostep.Listen(callback_query=False))
    """

    def __init__(self,
                 store: typing.Optional[MetaStore] = None,
                 callback_query: typing.Optional[bool] = None) -> None:
        self.store = store or root
        self.callback_query = callback_query

    async def __call__(
            self,
            handler: typing.Callable[[TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
            event: TelegramObject,
            data: typing.Dict[str, typing.Any]
    ) -> typing.Any:

        fn = None

        if self.callback_query:
            chat_id = event.message.chat.id
        else:
            chat_id = event.chat.id

        try:
            fn = await self.store.pop_item(event.from_user.id)
        except (KeyError, AttributeError):
            try:
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


async def register_next_step(
        user_id: int,
        _next: typing.Any,
        store: typing.Optional[MetaStore] = None,
        *,
        args: tuple = (),
        kwargs: dict = {},
) -> None:
    """
    register next step for user/chat.

    Example::

        async def ask_name(message: Message):
            await message.reply("What is your name?")
            await aiostep.register_next_step(message.from_user.id, ask_age)

        async def tell_name(msg: Message):
            await message.reply("Your name is: {msg.text}")
    """
    if args or kwargs:
        _next = functools.partial(_next, *args, **kwargs)

    await (store or root).set_item(user_id, _next)


async def unregister_steps(user_id: int, store: typing.Optional[MetaStore] = None) -> None:
    """
    unregister steps for `user_id`.

    if step is `asyncio.Future`, cancels that.
    """
    try:
        u = await (store or root).pop_item(user_id)
    except KeyError:
        return
    else:
        if isinstance(u, asyncio.Future):
            u.cancel("cancelled")


async def _wait_future(user_id: int, timeout: typing.Optional[float], store: MetaStore) -> Update:
    fn = asyncio.get_event_loop().create_future()

    await store.set_item(user_id, fn)

    try:
        return await asyncio.wait_for(fn, timeout)
    finally:
        await unregister_steps(user_id, store)


async def wait_for(
        user_id: int,
        timeout: typing.Optional[float] = None,
        store: typing.Optional[MetaStore] = None
) -> Update:
    """
    wait for update which comming from specific user_id.

    raise TimeoutError if timed out.

    Example::

        async def echo_handler(message: Message):
            await message.reply("Please type something:")
            try:
                response = await aiostep.wait_for(message.from_user.id, timeout=25)
            except TimeoutError:
                await message.reply('You took too long to answer.')
            else:
                await message.reply(f"You typed: {response.text}")
    """
    try:
        return await _wait_future(user_id, timeout, store or root)
    except asyncio.TimeoutError:
        raise TimeoutError


async def clear(store: typing.Optional[MetaStore] = None) -> None:
    """
    Clears all registered key-value's.
    """
    async for i in (store or root).clear():  # type: ignore
        if isinstance(i, asyncio.Future):
            i.cancel()
