import asyncio

from aiostep import aiogram_dialect, wait_for

from aiogram import Dispatcher, Bot, filters, types


dp = Dispatcher()
dp.message.outer_middleware(aiogram_dialect.Listen())


@dp.message(filters.CommandStart())
async def start(message: types.Message):
    await message.reply("Please type something:")
    try:
        response = await wait_for(message.from_user.id, timeout=10)
    except TimeoutError:
        await message.reply("You took too long to answer.")
    else:
        await message.reply(f"You typed: {response.text}")


async def main():
    bot = Bot(token="6716817630:AAGCmzgl_YPmzms4Q3S8KJ_ewzxWzB0Uyss")
    await dp.start_polling(bot)


asyncio.run(main())
