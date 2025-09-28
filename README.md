![PyPI Version](https://img.shields.io/pypi/v/aiostep)
![Python Version](https://img.shields.io/pypi/pyversions/aiostep)
![License](https://img.shields.io/pypi/l/aiostep)
![Total Downloads](https://static.pepy.tech/badge/aiostep)
![Downloads](https://img.shields.io/pypi/dm/aiostep)
[![Telegram](https://img.shields.io/badge/Telegram-Join%20Chat-blue?logo=telegram&style=flat-square)](https://t.me/aiostep_chat)


# Aiostep - Simple and Flexible State Management

Aiostep is a lightweight and flexible state management tool designed for Telegram bots and similar applications. It allows developers to track user states and manage transitions between them with ease. Whether you're building a multi-step form, handling complex user interactions, or simply need to store temporary user data, Aiostep makes it straightforward.

_We have a vibrant community of developers helping each other in our_ **[Telegram group](https://t.me/aiostep_chat)**. _Join us!_

_Stay tuned for library updates and new releases on our_ **[Telegram Channel](https://t.me/aiostep)**.

---

## Features

- **Simple API**: Intuitive methods for setting, getting, and deleting user states and associated data.
- **Customizable Storage**: Use in-memory storage or integrate with persistent options like Redis or file-based storage.
- **Direct User Interaction**: Easily ask questions and receive user responses directly within handlers, reducing boilerplate code.
- **Extendable**: Designed to integrate with existing frameworks such as aiogram.

---

## How It Works

### User Interaction Methods

Aiostep provides three primary methods for interacting with users and managing multi-step processes:

1. **`wait_for`**:
   - Use this method to wait for a specific user response within the current handler.
   - Simplifies user interaction by reducing the need for separate handlers.

2. **`register_next_step`**:
   - Allows registering the next handler explicitly for a user.
   - Useful for chaining steps in a process.

3. **States**:
   - Define user states to manage stages in a multi-step workflow.
   - States can include optional callbacks for seamless navigation between steps.

---

## Installation

To start using Aiostep, simply install it via pip.

```bash
pip install --upgrade aiostep
```

If you want use `RedisStateStorage`, you should install aiostep with redis support:
```bash
pip install --upgrade aiostep[redis]
```

---

## Usage

### Using `wait_for` and `register_next_step`
**Aiostep offers two primary methods for managing direct user interactions:**

#### 1. `wait_for`:
- This method allows you to wait for a user response directly within the current handler.
- Requires the `Listen` middleware to be set up for intercepting subsequent user messages.

**Example:**
```python
from aiostep import aiogram_dialect, wait_for

from aiogram import Dispatcher, filters
from aiogram.types import Message

dp = Dispatcher()
dp.message.outer_middleware(aiogram_dialect.Listen())

@dp.message(filters.CommandStart())
async def ask_question(message: Message):
    await message.reply("Please type something:")
    try:
        response = await wait_for(message.from_user.id, timeout=25)  # timeout is optional
    except TimeoutError:
        await message.reply("You took too long to answer.")
    else:
        await message.reply(f"You typed: {response.text}")
```
> [!NOTE]\
> The `timeout` parameter is optional; if not provided, the bot will wait indefinitely for a response.

#### 2. `register_next_step`
- Use this method to explicitly register the next handler for the user's response.
- Also requires the `Listen` middleware for processing follow-up messages.

**Example:**

```python
import aiostep
from aiostep import aiogram_dialect

from aiogram import Dispatcher, filters
from aiogram.types import Message

dp = Dispatcher()
dp.message.outer_middleware(aiogram_dialect.Listen())

@dp.message(filters.CommandStart())
async def ask_question(message: Message):
    await aiostep.register_next_step(message.chat.id, handle_answer)
    await message.reply("What's your name?")

async def handle_answer(message: Message):
    await message.reply(f"Hello, {message.text}!")
```

### Using States
**Aiostep supports managing user states to handle multi-step workflows. Unlike the previous methods, managing states does not require the `Listen` middleware.**


#### 1. Memory State Storage:
- This is an in-memory implementation suitable for temporary state storage.

**Example:**

```python
from aiostep import MemoryStateStorage
from aiostep.utils import IsState

from aiogram import Dispatcher, filters
from aiogram.types import Message

dp = Dispatcher()
state_manager = MemoryStateStorage()

@dp.message(filters.CommandStart())
async def start_process(message: Message):
    state_manager.set_state(
        user_id=message.from_user.id,
        state="STEP_ONE"
    )
    await message.reply("State set to STEP_ONE!")

@dp.message(IsState("STEP_ONE", state_manager))
async def handle_step_one(message: Message):
    await message.reply("You're in STEP_ONE.")
    state_manager.delete_state(
        user_id=message.from_user.id,
    )
```

**Returning to Previous State:**
```python
from aiogram import F

@dp.message(F.text == "Back")
async def go_back(message: Message):
    step = state_manager.get_state(message.from_user.id)
    if step and step.callback:
        await step.callback(message)
    else:
        await message.reply("No previous state found.")
```
> [!NOTE]\
> You should manually use getattr to find and call the back step handler if you use `RedisStateStorage` or `FileStateStorage`, because callbacks are saved as strings (function name)
>```python
>@dp.message_handler(F.text == "Back")
>async def go_back(message: Message):
>    step = state_manager.get_state(message.from_user.id)
>    if step and step.callback:
>        callback = getattr(step.callback)
>        await callback(message)
>    else:
>        await message.reply("No previous state found.")
>```

#### 2. Other Storage Options:
- File-based and Redis storage implementations are also available, providing similar functionality with persistent data storage.
- Simply replace MemoryStateStorage with FileStateStorage or RedisStateStorage when initializing the state manager.
> [!NOTE]\
> Methods in `MemoryStateStorage`, `FileStateStorage` and `RedisStateStorage` are synchronous.
> **If you want use asynchronous versions, use `aiostep.asyncio`:**
> ```python
> from aiostep.asyncio import AsyncMemoryStateStorage
> from aiostep.asyncio import AsyncFileStateStorage
> from aiostep.asyncio import AsyncRedisStateStorage
> ```

#### 3. Timeout States

To set a timeout (expiry) for the state storage, you can use the `ex` argument for both `RedisStateStorage` and `FileStateStorage`.
But for `MemoryStateStorage` you need to pass a TTLCache if you want set timeout.

Here's how you can set it up:

- **For `MemoryStateStorage`** (using `cachebox.TTLCache`):

    ```python
    from aiostep import MemoryStateStorage
    from cachebox import TTLCache  # cachetools.TTLCache also works

    # Create a TTLCache with a timeout of 200 seconds
    storage = MemoryStateStorage(TTLCache(0, 200))  # Timeout is 200 seconds
    ```

- **For `RedisStateStorage`** (using the `ex` argument for expiry time):

    ```python
    from aiostep import RedisStateStorage
    from aiostep import FileStateStorage

    # Create RedisStateStorage with a timeout of 200 seconds
    storage = RedisStateStorage(db=0, ex=200)  # Timeout (expiry) is 200 seconds
    storage = FileStateStorage("path.txt", ex=200)  # Same as RedisStateStorage
    ```
In both cases, the state will automatically expire after the specified time, and the data will be removed from the storage.

---

### Using Data

#### Setting Data

```python
state_manager.set_data(
    user_id=message.from_user.id,
    data={"key": "value"}
)
```

#### Getting Data

```python
data = state_manager.get_data(user_id=message.from_user.id)
await message.reply(f"Your data: {data}")
```

---

## Important Notes

1. **Callbacks**:
   - Callbacks can be any callable object, such as functions.
   - In `FileStateStorage` and `RedisStateStorage` they are stored as strings (e.g. function name).

3. **Storage Flexibility**:
   - The memory-based implementation is ideal for development and testing.
   - Persistent storage like Redis is recommended for production.

---

## Future Plans

- **Better Library Compatibility**: Enhanced support for other Telegram bot libraries such as `pyTelegramBotAPI` and `python-telegram-bot`, in addition to `aiogram`.
- **Improved Documentation**: Detailed guides and best practices.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

For more information or to contribute, visit our [GitHub repository](#).
