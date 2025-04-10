import asyncio
import typing

try:
    from telethon import TelegramClient, events
    telethon_installed = True
except ImportError:
    telethon_installed = False

from ..functions import MetaStore, root


def Listen(
    app: "TelegramClient",
    store: typing.Optional[MetaStore] = None,
    event: typing.Any = None,
    **kwargs
) -> None:
    """
    telethon listen client for steps.

    supported events:
        - `NewMessage`
        - `CallbackQuery`
        - `MessageEdited`

    Example::

        app = TelegramClient()
        aiostep.telethon_dialect.listen(app)
    """
    if not telethon_installed:
        raise ImportError(
            "telethon package is not installed. "
            "install package: "
            "pip install telethon"
        )
    store = store or root
    event = event or events.NewMessage

    async def _listen_wrapper(_event):
        fn = None

        try:
            fn = await store.pop_item(_event.sender_id)
        except (KeyError, AttributeError):
            try:
                fn = await store.pop_item(_event.chat_id)
            except (KeyError, AttributeError):
                pass

        if fn is not None:
            if isinstance(fn, asyncio.Future):
                fn.set_result(_event)
                return

            await fn(_event)
            return

    app.add_event_handler(_listen_wrapper, event(**kwargs))
