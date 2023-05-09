from config import TOKEN
import emoji
import sqlite3

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from cards import create_image

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
# Функция старта бота с проверкой на то, регистрировался ли до этого пользователь или нет
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    ID = message.from_user['id']

    con = sqlite3.connect("ID_VSH.db")
    cur = con.cursor()
    a = list(map(lambda x: x[0], cur.execute(f"SELECT ID from user_ids").fetchall()))
    con.commit()

    if str(ID) not in a:
        keyboard.add(types.InlineKeyboardButton(text="Учитель", callback_data="teacher"))
        keyboard.add(types.InlineKeyboardButton(text="Ученик", callback_data="student"))
        await message.answer(
            f"<strong>Выберете тип учетной записи</strong> {emoji.emojize(':arrow_down:', language='alias')}",
            reply_markup=keyboard, parse_mode="HTML")
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu"))
        await message.answer(f"""<strong>Вы уже зарегистрированы</strong>""",
                             parse_mode="HTML", reply_markup=keyboard)


@dp.callback_query_handler(text="teacher")
# Функция регистрации аккаунта, как учителя
async def teacher(call: types.CallbackQuery):
    ID = call.from_user['id']
    await call.message.edit_reply_markup()
    await call.message.delete()
    con = sqlite3.connect("ID_VSH.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO user_ids VALUES(?, ?, ?, ?)", (ID, 'teacher', '', ''))
    con.commit()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu"))
    await call.message.answer(f"<strong>Вы зарегистрировались как учитель"
                              f" {emoji.emojize(':check_mark_button:', language='alias')}</strong>", parse_mode="HTML",
                              reply_markup=keyboard)


@dp.callback_query_handler(text="student")
# Функция регистрации аккаунта, как ученика
async def student(call: types.CallbackQuery):
    ID = call.from_user['id']
    await call.message.edit_reply_markup()
    await call.message.delete()
    con = sqlite3.connect("ID_VSH.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO user_ids VALUES(?, ?, ?, ?)", (ID, 'student', '', ''))
    con.commit()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu"))
    await call.message.answer(f"<strong>Вы зарегистрировались как ученик"
                              f" {emoji.emojize(':check_mark_button:', language='alias')}</strong>", parse_mode="HTML",
                              reply_markup=keyboard)


@dp.callback_query_handler(text="main_menu")
# Функция вызова главного меню в зависимости от типа аккаунта
async def main_menu(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    ID = call.from_user['id']
    con = sqlite3.connect("ID_VSH.db")
    cur = con.cursor()
    a = cur.execute(f"SELECT type from user_ids where ID={ID}").fetchall()[0][0]
    con.commit()
    if a == 'teacher':
        keyboard.add(types.InlineKeyboardButton(text="Отослать карточки", callback_data="cards"))
        keyboard.add(types.InlineKeyboardButton(text="Создать класс", callback_data="class"))
        keyboard.add(types.InlineKeyboardButton(text="Посмотреть результаты", callback_data="show_res"))
        keyboard.add(types.InlineKeyboardButton(text="Персональный ключ", callback_data="pers_key"))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Пройти тест", callback_data="pass_test"))
        keyboard.add(types.InlineKeyboardButton(text="Вступить в класс", callback_data="enter_class"))
    await call.message.answer(f"""<strong>Меню</strong>""", parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query_handler(text="cards")
# Функция вывода инструкции для того, чтобы разослать карточки ученикам
async def cards(call: types.CallbackQuery):
    await call.message.answer(f"""Чтобы разослать карточки введите команду
/send и класс, которому достанутся задания.
Например: /send 10A""")


@dp.callback_query_handler(text="pers_key")
# Функция вывода индивидуального ключа учителя
async def cards(call: types.CallbackQuery):
    await call.message.answer(f"""{call.from_user.id}""")


@dp.callback_query_handler(text="show_res")
# Функция вывода инструкции для того, чтобы посмотреть результаты учеников
async def pass_test(call: types.CallbackQuery):
    await call.message.answer(f"""Чтобы посмотреть результаты введите команду
/results и класс, которому достанутся задания.
Например: /results 10A""")


@dp.callback_query_handler(text="pass_test")
# Функция прохождения теста учеником
async def pass_test(call: types.CallbackQuery):
    try:
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        name = cur.execute(f"""SELECT name_of_works from user_ids WHERE type = (?)
        and ID = (?)""", ('student', call.from_user.id)).fetchall()[0][0]
        con.commit()
        with open(f'data/card{name}.jpg', 'rb') as photo:
            await bot.send_photo(call.from_user.id, photo=photo,
                                 caption=f"""Вы проходите тест, который был скинут вам последним. 
    Для этого введите команду /answer.
    Например, /answer 11,12,21,22,31,33,41,51,52""")
    except Exception:
        await call.message.answer(f"""Похоже у вас пока что нет тестов или что то пошло не так""")


@dp.message_handler(commands=["results"])
# Функция вывода результатов учеников определенного класса
async def coord(message: types.Message):
    try:
        command = message.get_full_command()[1]
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        ids = []
        res = ''
        g = cur.execute(f"""SELECT members from classes WHERE teacher_id = (?)
               and name = (?)""", (message.from_user.id, command)).fetchall()[0][0].split(';')[:-1]
        for elem in g:
            f = elem.split(',')
            ids.append([f[0] + ' ' + f[1], f[-1]])
        for i in range(len(ids)):
            h = cur.execute(f"""SELECT result from user_ids WHERE ID = '{ids[i][-1]}'""").fetchall()[0][0]
            res += ids[i][0] + ' ' + str(h) + '\n'

        await message.answer(f"""{res}""")
        con.commit()
    except Exception:
        await message.answer(f"""Упс, возникли какие-то проблемы {emoji.emojize(':crying_cat:', language='alias')}
Проверьте пожалуйста правильность составленного вами запроса""")


@dp.message_handler(commands=["answer"])
# Функция принятия ответов ученика и их автоматическая проверка
async def coord(message: types.Message):
    try:
        cnt = 0
        command = message.get_full_command()[1].split(',')
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        name = cur.execute(f"""SELECT name_of_works from user_ids WHERE type = (?)
        and ID = (?)""", ('student', message.from_user.id)).fetchall()[0][0]
        s = cur.execute(f"""SELECT answers from classes WHERE photo = '{name}'""").fetchall()[0][0].split(',')
        con.commit()
        for i in range(9):
            if command[i] == s[i]:
                cnt += 1

        cur.execute(f"""UPDATE user_ids
                    SET result = (?) WHERE ID = (?) and type = (?)""",
                    (f'{cnt}/9', str(message.from_user.id), 'student'))
        con.commit()
        await message.answer(f"""Тест пройден""")
    except Exception:
        await message.answer(f"""Упс, возникли какие-то проблемы {emoji.emojize(':crying_cat:', language='alias')}
Проверьте пожалуйста правильность составленного вами запроса""")


@dp.message_handler(commands=["send"])
# Функция отправки карточек ученикам
async def coord(message: types.Message):
    try:
        # Добавление название фото теста и правильных ответов
        command = message.get_full_command()[1]
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        name = f'{message.from_user.id}{command}'
        ans = create_image(name)
        cur.execute(f"""UPDATE classes
            SET answers = (?) WHERE teacher_id = (?) and name = (?)""", (ans, message.from_user.id, command))
        cur.execute(f"""UPDATE classes
            SET photo = (?) WHERE teacher_id = (?) and name = (?)""", (name, message.from_user.id, command))

        # Удаление старых результатов после добавления нового теста
        ids = []
        g = cur.execute(f"""SELECT members from classes WHERE teacher_id = (?)
                       and name = (?)""", (message.from_user.id, command)).fetchall()[0][0].split(';')[:-1]
        for elem in g:
            f = elem.split(',')
            ids.append([f[0] + ' ' + f[1], f[-1]])
        print(ids)
        for elem in ids:
            cur.execute(f"""UPDATE user_ids SET result = (?) WHERE ID = (?)""", ('', elem[-1]))

        con.commit()
    except Exception:
        await message.answer(f"""Упс, возникли какие-то проблемы {emoji.emojize(':crying_cat:', language='alias')}
Проверьте пожалуйста правильность составленного вами запроса""")


@dp.callback_query_handler(text="class")
# Функция вывода инструкции о том, как создать класс
async def clas(call: types.CallbackQuery):
    await call.message.answer(f"""Чтобы создать класс введите команду
/create и укажите без пробела цифру и литеру класса. Например: /create 10A""")


@dp.message_handler(commands=["create"])
# Функция создания класса
async def coord(message: types.Message):
    try:
        # отвечает за создание классов, с проверкой на наличие у этого id класса с таким же названием
        flag = True
        command = message.get_full_command()[1]
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        g = cur.execute(f"""SELECT name from classes WHERE teacher_id = {message.from_user.id}""").fetchall()
        for elem in g:
            s = elem[0]
            if s == command:
                flag = False
                break
        if not flag:
            raise Exception
        cur.execute(f"INSERT INTO classes VALUES(?, ?, ?, ?, ?)",
                    (message.from_user.id, '', command, '', str(message.from_user.id) + command))
        con.commit()
        await message.answer(f"""Вы успешно создали класс""")
    except Exception:
        await message.answer(f"""Упс, возникли какие-то проблемы {emoji.emojize(':crying_cat:', language='alias')}
Проверьте пожалуйста правильность составленного вами запроса""")


@dp.callback_query_handler(text="enter_class")
# Функция вывода инструкции о том, как вступить в класс
async def enter_class(call: types.CallbackQuery):
    await call.message.answer(f"""Чтобы добавиться в класс учителя,
нужно ввести через ';' код учителя, вашу фамилию, ваше имя, класс, в который вы хотите вступить.
Например: /add 477754858;Иванов;Иван;10A""")


@dp.message_handler(commands=["add"])  # добавление ученика, с проверкой оригинальности id
# чтобы ученик, используя одно и то же id не смог зайти в один и тот же класс
async def coord(message: types.Message):
    try:
        command = message.get_full_command()[1].split(';')
        con = sqlite3.connect("ID_VSH.db")
        cur = con.cursor()
        g = cur.execute(f"""SELECT members from classes WHERE teacher_id = (?)
           and name = (?)""", (int(command[0]), command[-1])).fetchall()[0][0]

        for elem in g.split(';')[:-1]:
            if str(message.from_user.id) == elem.split(',')[2]:
                raise Exception
        a = g + command[1] + ',' + command[2] + ',' + str(message.from_user.id) + ';'
        cur.execute(f"""UPDATE classes
    SET members = (?) WHERE teacher_id = (?) and name = (?)""", (a, int(command[0]), command[-1]))

        cur.execute(f"""UPDATE user_ids
            SET name_of_works = '{command[0] + command[-1]}' WHERE ID = '{str(message.from_user.id)}'""")
        con.commit()
        await message.answer(f"""Вы успешно зарегистрировались""")
    except Exception:
        await message.answer(f"""Упс, возникли какие-то проблемы {emoji.emojize(':crying_cat:', language='alias')}
Проверьте пожалуйста правильность составленного вами запроса""")


if __name__ == '__main__':
    executor.start_polling(dp)
