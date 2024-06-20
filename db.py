import os

import aiosqlite

DB_NAME = os.environ.get('DB_NAME')


async def create_table():
    """Create all needed DB if not exist"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                FOREIGN KEY (question_index)  REFERENCES  quiz_question (question_id))''')
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_question (
                question_id INTEGER PRIMARY KEY,
                question_name TEXT,
                options TEXT,
                correct_option INTEGER)''')
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_answer (
                answer_name TEXT,
                question_index INTEGER,
                user_id INTEGER,
                is_right BOOL,
                UNIQUE (user_id, question_index) ON CONFLICT REPLACE,
                FOREIGN KEY (question_index)  REFERENCES  quiz_question (question_id))''')
        await db.commit()


async def load_quiz_question(question_index, question_name, options, correct_option):
    """Load question to DB"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO quiz_question (question_id, question_name, options, correct_option) VALUES (?, ?, ?, ?)',
            (question_index, question_name, options, correct_option))
        await db.commit()


async def update_quiz_index(user_id, index):
    """Update quiz state for user"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()


async def get_quiz_index(user_id):
    """Get quiz state for user"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_correct_index(question_id):
    """Get correct answer id for question"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного вопроса
        async with db.execute('SELECT correct_option FROM quiz_question WHERE question_id = (?)', (question_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_options_list(question_id):
    """Get Answer list for question"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT options FROM quiz_question WHERE question_id = (?)', (question_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_question_name(question_id):
    """Get text of question"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_name FROM quiz_question WHERE question_id = (?)', (question_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_questions_number():
    """Get number of all quastions"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем общее число вопросов
        async with db.execute('SELECT COUNT(*) FROM quiz_question') as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_user_answer(answer_name, question_index, user_id, is_right):
    """Add user answer in DB"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id и question_index уже существует
        await db.execute(
            'INSERT OR REPLACE INTO quiz_answer (answer_name, question_index, user_id, is_right) VALUES (?, ?, ?, ?)', (answer_name, question_index, user_id, is_right))
        # Сохраняем изменения
        await db.commit()


async def get_answers_number(user_id, is_right):
    """Get number of answer right or false"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного вопроса
        async with db.execute('SELECT COUNT(*) FROM quiz_answer WHERE user_id = (?) AND is_right = (?)', (user_id, is_right, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def clear_last_user_result(user_id):
    """Clear all user answer"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_answer WHERE user_id = (?)', (user_id, ))
        await db.commit()


async def drop_table_answer():
    """Drop answer table"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DROP TABLE quiz_answer ')
        await db.commit()