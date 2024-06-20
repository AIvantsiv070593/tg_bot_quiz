import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from db import create_table, load_quiz_question, drop_table_answer
from handler import router

logging.basicConfig(level=logging.INFO)

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

bot = Bot(token=API_TOKEN)

dp = Dispatcher()
dp.include_router(router)

with open('question.json', encoding="utf-8") as f:
    quiz_data = json.load(f)


async def main():
    """Start bot"""
    await drop_table_answer()
    await create_table()

    for question in quiz_data:
        await load_quiz_question(
            quiz_data.index(question),
            question['question'],
            ','.join(question['options']),
            question['correct_option'])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
