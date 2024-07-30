# aiostep

aiostep is a powerful extension library for aiogram, designed to simplify and enhance the process of building Telegram bots in Python. It introduces intuitive methods for direct user interactions and streamlined conversation flow management.

# Key Features
1. Direct User Interactions
  - aiostep allows you to easily implement direct question-answer flows in your bot without complex handler chains. You can wait for a user's response within a single function, making your code more readable and maintainable.
2. Simplified Next Step Registration
  - With aiostep, you can effortlessly manage conversation flows by registering next steps. This feature allows you to create complex, multi-step interactions without cluttering your main handler functions.
3. Seamless Integration with aiogram
  - aiostep is designed to work harmoniously with aiogram. It enhances aiogram's capabilities without replacing its core functionality.

# Installation
To use aiostep in your project, simply install it with the following command:
```bash
pip install -U aiostep
```

# Quick Start
### Middleware Integration
1. To use aiostep, add the Listen middleware to your dispatcher:
```python
from aiogram import Dispatcher
from aiostep import Listen

dp = Dispatcher()
dp.message.outer_middleware(Listen())
```
2. Use wait_for to directly interact with users:
```python
import aiostep

@dp.message(filters.Command("echo"))
async def echo_handler(message: Message):
    await message.reply("Please type something:")
    try:
        response = await aiostep.wait_for(message.from_user.id, timeout=25)
    except TimeoutError:
        await message.reply('You took too long to answer.')
    else:
        await message.reply(f"You typed: {response.text}")
```
3. Use register_next_step for complex conversation flows:
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

async def confirm_details(msg: Message, name: str = None):
    try:
        age = int(msg.text)
    except ValueError:
        await msg.reply("Please send a valid age!")
        await register_next_step(msg.from_user.id, confirm_details, kwargs={"name": name})
        return

    await msg.reply(f"Your name is {name} and you are {age} years old. Thank you!")
```
