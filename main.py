import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import random

import config
import config as cfg
import markups as nav
from db import Datebase

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
db = Datebase('db.db')

current_chat = ''


@dp.message_handler(commands=['start'], commands_prefix="/")
async def cmd(message):
    if message.chat.type == "private":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button_add = KeyboardButton(text='Добавить бота')
        button_commands = KeyboardButton(text='Мои чаты')
        keyboard.add(button_add, button_commands)
        if not db.admin_exists(message.from_user.id):
            db.add_admin(message.from_user.id)
            await message.answer(
                "Привет!\nЯ бот-менеджер для вашего чата\nВсе команды вы можетередактировать просто написав мне в лс\nЧто бы добавить меня нажм на кнопку 'Добавить меня':)",
                reply_markup=keyboard)
        else:
            await message.answer("С возращением\nсамое время посмотреть свои чаты)", reply_markup=keyboard)


@dp.message_handler(commands=['help'], commands_prefix="/")
async def help(message: types.Message, edit=0):
    buttons = [
        types.InlineKeyboardButton(text="Как редактировать комманды чата", callback_data="how_red")
    ]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*buttons)
    if edit == 0:
        await bot.send_message(message.chat.id, 'Выберите что вас интерисует', reply_markup=keyboard)
    else:
        await message.edit_text('Выберите что вас интерисует', reply_markup=keyboard)


def check_sub_chanel(chat_member):
    return chat_member['status'] != 'left'


def non_root(msg):
    return bot.send_message(msg.chat.id, 'Не админ')


@dp.message_handler(content_types=['new_chat_members'])
async def user_joined(message: types.Message):
    if n := db.get_chat(message.chat.id, 'hello_message')[0][0]:
        await message.answer(n)


@dp.message_handler(commands=['hello'], commands_prefix="/")
async def user_joined(message: types.Message):
    if message.chat.type == "private":
        if current_chat != '':
            id = current_chat
        else:
            await bot.send_message(message.chat.id, 'Не выбран чат')
            return
    else:
        id = message.chat.id
    db.set_defult(id, message.text[6:])
    await bot.send_message(message.chat.id, 'Новое приветсвенное сообщение назнаенно')


@dp.message_handler(commands=['r'], commands_prefix="/")
async def stat(message: types.Message):
    if str(message.from_user.id) == cfg.ADMIN_ID:
        if message.text[3] == '+':
            photo = InputFile("kitajskaja-partija-gorditsja-toboj-memy-3-360x270.jpg")
        else:
            photo = InputFile("cLE2ARVjhXo.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        await non_root(message)


@dp.message_handler(commands=['setup'], commands_prefix="/")
async def setup(message: types.Message):
    if message.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
        if message.chat.type != "private":
            code = message.text[7::]
            if int(code) == db.get_code(message.from_user.id)[0]:
                try:
                    chats = db.admin_chat(message.from_user.id)[0][0]
                    if str(message.chat.id) not in chats.split(', '):
                        chats = chats + f', {message.chat.id} {message.chat.title}'
                        db.update_admin_chat(chats, message.from_user.id)
                        await message.bot.send_message(message.chat.id, 'Чат успешно добавлен')
                    else:
                        await message.bot.send_message(message.chat.id, 'Вы уже добавили этот чат')
                except AttributeError:
                    chats = f"{message.chat.id} {message.chat.title}"
                    db.update_admin_chat(chats, message.from_user.id)
                    if not db.chat_exists(chats):
                        db.add_chat(chats.split()[0], chats.split()[1])
                        db.set_defult(chats.split()[0], config.defoult_settings)
                    await message.bot.send_message(message.chat.id, 'Чат успешно добавлен')
                db.del_code(message.from_user.id)


def update(message, n_s):
    new_date = message.text[n_s:]
    if current_chat == '':
        return ['chat']
    if new_date[0] == '1' or new_date[0] == '0':
        if new_date[2::] == 'al' or new_date[2:] == 'ad':
            title = db.get_chat(current_chat, ['title'])
            db.set_defult(current_chat, {message.text[1:5]: new_date})
            return ['ok', new_date, title]

    else:
        return ['arg']


@dp.message_handler(commands=['admins'], commands_prefix="/")
async def admins(message: types.Message):
    admin_data = db.get_chat(message.chat.id, ['admins'])[0][0]
    if admin_data[0] == '1':
        if admin_data[2:] == 'ad':
            if message.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
                chat_admins = await bot.get_chat_administrators(message.chat.id)
                for admins in chat_admins:
                    userId = admins.user.id
                    await message.answer(text="{}".format(userId))
        else:
            chat_admins = await bot.get_chat_administrators(message.chat.id)
            for admins in chat_admins:
                userId = admins.user.id
                await message.answer(text="{}".format(userId))


@dp.message_handler(commands=['mute'], commands_prefix="/")
async def mute_check(message: types.Message):
    if message.chat.type != "private":
        mute_data = db.get_chat(message.chat.id, ['mute'])[0][0]
        if mute_data[0] == '1':
            if mute_data[2:] == 'ad':
                if message.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
                    if not message.reply_to_message:
                        await message.reply('Эта команда должна быть ответом на сообщение')
                        return
                    mute_sec = int(message.text[6:])
                    db.add_mute(message.reply_to_message.from_user.id, message.chat.id, mute_sec)
                    await message.bot.delete_message(message.chat.id, message.reply_to_message.message_id)
                    await message.bot.send_message(message.chat.id, f"Пользователь был замучен на {mute_sec}")
                else:
                    await non_root(message)
            else:
                if not message.reply_to_message:
                    await message.reply('Эта команда должна быть ответом на сообщение')
                    return
                mute_sec = int(message.text[6:])
                db.add_mute(message.reply_to_message.from_user.id, message.chat.id, mute_sec)
                await message.bot.delete_message(message.chat.id, message.reply_to_message.message_id)
                await message.bot.send_message(message.chat.id, f"Пользователь был замучен на {mute_sec}")
    else:
        a = update(message, 6)
        if a[0] == 'chat':
            await bot.send_message(message.chat.id, 'Не выбран чат')
            return
        if a[0] == 'ok':
            await bot.send_message(message.chat.id, f'Чат {a[2]}\n'
                                                    f'/mute {a[1]}')
        else:
            await bot.send_message(message.chat.id, 'Неверные аргументы')
            return


def generate_button(chats):
    chats = chats[0][0].split(', ')
    buttons = []
    for i in chats:  # получаем имя группы
        i = i.split()
        buttons.append(types.InlineKeyboardButton(text=i[1], callback_data=f'id_{i[0]}'))
    return buttons


@dp.message_handler()
async def mess_handler(message: types.Message):
    if message.chat.type != "private":
        if not db.user_exists(message.from_user.id, message.chat.id):
            db.add_user(message.from_user.id, message.chat.id)

        if not db.mute(message.from_user.id, message.chat.id):
            text = message.text.lower().split()
            if len(set(text).intersection(cfg.WORDS)) != 0:
                await message.delete()
            """if check_sub_chanel(await bot.get_chat_member(chat_id=cfg.CHANEL_ID, user_id=message.from_user.id)):
                text = message.text.lower().split()
                if len(set(text).intersection(cfg.WORDS)) != 0:
                    await message.delete()
            else:
                await message.answer("Чтобы отправлять подпишитесь на канал", reply_markup=nav.chanelMenu)
                await message.delete()"""

        else:
            await message.delete()
    else:
        if message.text == 'Добавить бота':
            buttons = [
                types.InlineKeyboardButton(text="Перейти", callback_data="gen_code")
            ]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(*buttons)
            await message.bot.send_message(text="Для создания админ панели управления ботом, добавте его в чат,"
                                                "выдайте права администратора.\n После этого нажимайте на кнопку "
                                                "перейти, появляется код, который надо ввести в чат с командой /setup {код}\n"
                                                "Если появилось сообщение об успешном добавлении, то вы всё сделали "
                                                "правильно)",
                                           chat_id=message.chat.id,
                                           reply_markup=keyboard)
        elif message.text == 'Мои чаты':
            keyboard = types.InlineKeyboardMarkup()
            a = generate_button(db.admin_chat(message.from_user.id))
            keyboard.add(*a)
            await message.bot.send_message(text="Ваши чаты\nВыберите чат что бы посмотреть настройки\n\n /help  "
                                                "помощь по командам",
                                           chat_id=message.chat.id, reply_markup=keyboard)


@dp.callback_query_handler()
async def callbacks_num(call: types.CallbackQuery):
    global current_chat
    if call.data == 'gen_code':
        code = random.randint(100, 999)
        while db.check_code(code) != 0:
            code = random.randint(100, 999)
        db.add_code(call.from_user.id, code)
        st = '{код}'
        await call.message.edit_text(f"/setup {st}\nКод: {code}")
    elif call.data[0:3] == 'id_':
        current_chat = call.data[3:]
        settings = db.get_chat(current_chat, cfg.all_command)
        msg = ''
        for i, j in enumerate(cfg.all_command):
            msg = msg + f'По команде /{j} значение {settings[i]}\n'
        await bot.send_message(call.message.chat.id, msg)
    elif call.data == 'how_red':
        buttons = [
            types.InlineKeyboardButton(text="Назад", callback_data='help')
        ]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*buttons)
        await call.message.edit_text(f"Для редактирования команд чата перейдите из главного меню в 'Мои чаты'"
                                     f"Далее из списка предложанных выберите нужный вам чат"
                                     f"После этого вам будет выведин список ваших настроект"
                                     f"Введите команду из этих настроек и пердайте новые значений"
                                     f"Пример для /admin", reply_markup=keyboard)
    elif call.data == 'help':
        await help(call.message, 1)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
