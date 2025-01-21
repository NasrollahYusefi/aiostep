![PyPI Version](https://img.shields.io/pypi/v/aiostep)
![Python Version](https://img.shields.io/pypi/pyversions/aiostep)
![License](https://img.shields.io/pypi/l/aiostep)
![Total Downloads](https://static.pepy.tech/badge/aiostep)
![Downloads](https://img.shields.io/pypi/dm/aiostep)

# aiostep

**aiostep** is an extension library for [aiogram](https://github.com/aiogram/aiogram), designed to streamline building Telegram bots in Python. It simplifies user interactions by providing intuitive methods for handling conversations and state management.

---

## Key Features

- **Direct User Interaction**: Easily ask questions and receive user responses directly within handlers, reducing boilerplate code.
- **Step-Based Flow**: Seamlessly manage multi-step conversation flows with support for dynamic callbacks.
- **State Management**: Built-in state management with support for both in-memory and Redis-based storage options.

---

## Installation

To install the latest version of `aiostep`, run:

```bash
pip install -U aiostep
```

---

## Quick Start

### 1. Middleware Integration

To use `aiostep`, add the `Listen` middleware to your `Dispatcher` instance:

```python
from aiogram import Dispatcher
from aiostep import Listen

dp = Dispatcher()
dp.message.outer_middleware(Listen())
```

### 2. Direct Interaction Using `wait_for`

With `aiostep`, you can wait for a user's response directly within a handler using the `wait_for` function:

```python
import aiostep

@dp.message(filters.Command("echo"))
async def echo_handler(message: Message):
    await message.reply("Please type something:")
    try:
        response = await aiostep.wait_for(message.from_user.id, timeout=25)  # timeout is optional
    except TimeoutError:
        await message.reply("You took too long to answer.")
    else:
        await message.reply(f"You typed: {response.text}")
```

**Note**: The `timeout` parameter is optional; if not provided, the bot will wait indefinitely for a response.

### 3. Managing Multi-Step Flows with `register_next_step`

Easily manage multi-step conversation flows where the user's next input is handled by a different function:

```python
import aiostep

@dp.message(filters.CommandStart())
async def start(message: Message):
    await message.reply("What is your name?")
    await aiostep.register_next_step(message.from_user.id, ask_age)

async def ask_age(msg: Message):
    user_name = msg.text
    await msg.reply("How old are you?")
    await aiostep.register_next_step(msg.from_user.id, confirm_details, kwargs={"name": user_name})

async def confirm_details(msg: Message, name: str):
    try:
        age = int(msg.text)
    except ValueError:
        await msg.reply("Please provide a valid age!")
        await aiostep.register_next_step(msg.from_user.id, confirm_details, kwargs={"name": name})
    else:
        await msg.reply(f"Your name is {name} and you're {age} years old. Thanks!")
```

Again, the `timeout` parameter can be passed to `register_next_step` as an option to limit how long to wait for a user's response.

---

## State Management

A key feature of `aiostep` is state management, which allows you to store and retrieve user-specific data across sessions. You can choose between **in-memory** storage (ideal for quick setups) or **Redis** for distributed environments.

### Example Usage with Redis-Based Storage

To store and manage states in Redis, you need to initialize `RedisStateStorage` and integrate it with your bot:

```python
from redis.asyncio import Redis
from aiostep.storage import RedisStateStorage

redis_instance = Redis()
storage = RedisStateStorage(redis_instance)

# Setting a state for a user
await storage.set_state(user_id=12345, state="awaiting_input")

# Getting the current state for a user
state_context = await storage.get_state(user_id=12345)
print(state_context.current_state)

# Deleting the current state for a user
await storage.delete_state(user_id=12345)
```

### Example with In-Memory State Storage

For simpler setups where persistence is not required, use `MemoryStateStorage`:

```python
from aiostep.storage import MemoryStateStorage
from cachebox import TTLCache

storage = MemoryStateStorage(TTLCache(1000, 86400))

# Set a state
storage.set_state(user_id=12345, state="awaiting_input")

# Retrieve the state
state_context = storage.get_state(user_id=12345)
print(state_context.current_state)

# Delete the state
storage.delete_state(user_id=12345)
```

### Example Usage with Redis-Based Storage

To store and manage states in Redis, you need to initialize `RedisStateStorage` and integrate it with your bot:

```python
from aiostep.storage import FileStateStorage

# File can be .json or anything else
storage = FileStateStorage("path/to/file.json")

# Setting a state for a user
await storage.set_state(user_id=12345, state="awaiting_input")

# Getting the current state for a user
state_context = await storage.get_state(user_id=12345)
print(state_context.current_state)

# Deleting the current state for a user
await storage.delete_state(user_id=12345)
```

### Data Management with States

In addition to states, you can attach custom data to users' sessions. Here's an example of managing user data:

```python
# Set custom data
await storage.set_data(user_id=12345, data={"age": 30, "name": "Alice"})

# Get the stored data
user_data = await storage.get_data(user_id=12345)
print(user_data)  # Outputs: {'age': 30, 'name': 'Alice'}

# Update existing data
await storage.update_data(user_id=12345, data={"location": "Berlin"})

# Clear all data for the user
await storage.clear_data(user_id=12345)
```

---

## Advanced State Management

The state management system in `aiostep` allows you to define flexible workflows and manage conversation states efficiently. Here are a few additional features:

- **Custom State Objects**: You can define your own states using Python enums for better structure and clarity.
- **Dynamic Callbacks**: Store and invoke callback functions dynamically as part of the state context.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

By leveraging `aiostep`, you can significantly reduce complexity when building advanced Telegram bots with multiple conversation flows. Whether you're managing a simple Q&A session or a multi-step wizard, `aiostep` provides the tools to do it efficiently.

For any contributions, issues, or feedback, feel free to check out the repository and open a discussion or pull request!

---
