from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import (get_correct_index, get_options_list, get_question_name,
                get_quiz_index, update_quiz_index)


async def new_quiz(message):
    '''Create new quiz and ask quastion'''
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_question(message, user_id):
    """Generate varian of answer and send to user"""
    current_question_index = await get_quiz_index(user_id)
    correct_index = await get_correct_index(current_question_index)

    opts = await get_options_list(current_question_index)
    opts = opts.split(',')

    kb = generate_options_keyboard(opts, opts[correct_index])

    question = await get_question_name(current_question_index)
    await message.answer(f"➡️ {question}", reply_markup=kb)


def generate_options_keyboard(answer_options, right_answer):
    """Generate keyboard wtih callback functions"""
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        index_option = answer_options.index(option)
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer/{index_option}" if option == right_answer else f"wrong_answer/{index_option}")
        )

    builder.adjust(1)
    return builder.as_markup()
