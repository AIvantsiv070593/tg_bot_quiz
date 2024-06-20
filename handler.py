from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db import (get_correct_index, get_options_list,
                get_quiz_index, update_quiz_index, get_questions_number,
                update_user_answer, get_answers_number, clear_last_user_result)
from interact import (get_question, get_quiz_index, new_quiz,
                      update_quiz_index)


router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handler for 'start' msg? show start game btn"""
    await clear_last_user_result(message.from_user.id)

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))

    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True))


# Хендлей на команду /stat
@router.message(F.text == "Статистика последней игры")
@router.message(Command("stat"))
async def cmd_stat(message: types.Message):
    '''Hanlder for push start btn, asked quastion'''
    questions_number = await get_questions_number()
    user_id = message.from_user.id
    count_right_answer = await get_answers_number(user_id, True)
    count_wrong_answer = await get_answers_number(user_id, False)
    await message.answer("Статистика последней игры.\n" +
                         f"➡️ Всего вопросов: {questions_number}\n" +
                         f"✅ Правильных ответов: {count_right_answer}\n" +
                         f"❌ Не правильных ответов: {count_wrong_answer}")


# Хэндлер на команду /quiz
@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    '''Hanlder for stat of quiz'''
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


# Callback на верный ответ
@router.callback_query(F.data.split('/')[0] == 'right_answer')
async def right_answer(callback: types.CallbackQuery):
    '''Calback  for write answer'''
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    answer_list = await get_options_list(current_question_index)
    answer_list = answer_list.split(',')
    user_answer = answer_list[int(callback.data.split('/')[1])]

    await save_user_answer(callback, user_answer, current_question_index, True)
    await callback.message.answer("✅ Верно!")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    questions_number = await get_questions_number()
    if current_question_index < questions_number:
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            "💁‍♂️ Это был последний вопрос.\nКвиз завершен!")


# Callback на НЕ верный ответ
@router.callback_query(F.data.split('/')[0] == 'wrong_answer')
async def wrong_answer(callback: types.CallbackQuery):
    '''Calback  for wrong answer'''
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    answer_list = await get_options_list(current_question_index)
    answer_list = answer_list.split(',')
    user_answer = answer_list[int(callback.data.split('/')[1])]

    await save_user_answer(
        callback, user_answer, current_question_index, False)

    correct_option = await get_correct_index(current_question_index)

    await callback.message.answer(
        f"❌ Неправильно.\n\nПравильный ответ:\n{answer_list[correct_option]}")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    questions_number = await get_questions_number()

    if current_question_index < questions_number:
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            "💁‍♂️ Это был последний вопрос.\nКвиз завершен!")


async def save_user_answer(callback,
                           user_answer,
                           current_question_index,
                           is_right):
    '''Showing user answer in chst and save it in file'''
    await callback.bot.send_message(
        callback.from_user.id, f'Ваш ответ: {user_answer}')

    await update_user_answer(user_answer,
                             current_question_index,
                             callback.from_user.id,
                             is_right)
