import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import random
import config as cfg
import markups as nav
from db import Datebase
from telethon import TelegramClient, events, utils

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
db = Datebase('db.db')


@dp.message_handler(commands=['start'], commands_prefix="/")
async def cmd(message):
    if message.chat.type == "private":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button_add = KeyboardButton(text='Добавить бота')
        button_commands = KeyboardButton(text='Команды')
        keyboard.add(button_add, button_commands)
        if not db.admin_exists(message.from_user.id):
            db.add_admin(message.from_user.id)
            await message.answer("Привет!\nЯ бот-менеджер для вашего чата\nВсе команды вы можетередактировать просто написав мне в лс\nЧто бы добавить меня нажм на кнопку 'Добавить меня':)", reply_markup=keyboard)
        await message.answer("С возращением\nсамое время посмотреть свои чаты)", reply_markup=keyboard)


def check_sub_chanel(chat_member):
    return chat_member['status'] != 'left'


@dp.message_handler(content_types=['new_chat_members'])
async def user_joined(message: types.Message):
    await message.answer(cfg.HELLO_MESSAGE, reply_markup=nav.chanelMenu)


@dp.message_handler(commands=['r'], commands_prefix="/")
async def stat(message: types.Message):
    if str(message.from_user.id) == cfg.ADMIN_ID:
        print(message.text)
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
                    await message.bot.send_message(message.chat.id, 'Чат успешно добавлен')
                db.del_code(message.from_user.id)


@dp.message_handler(commands=['admins'], commands_prefix="/")
async def setup(message: types.Message):
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for admins in chat_admins:
        userId = admins.user.id
        await message.answer(text="{}".format(userId))


@dp.message_handler(commands=['mute'], commands_prefix="/")
async def mute(message: types.Message):
    if str(message.from_user.id) == cfg.ADMIN_ID:
        if not message.reply_to_message:
            await message.reply('Эта команда должна быть ответом на сообщение')
            return
        mute_sec = int(message.text[6:])
        db.add_mute(message.reply_to_message.from_user.id, message.chat.id, mute_sec)
        await message.bot.delete_message(cfg.CHAT_ID, message.reply_to_message.message_id)
        await message.reply_to_message.reply(f"Пользователь был замучен на {mute_sec}")
    else:
        await non_root(message)


def generate_button(chats):
    chats = chats[0][0].split(', ')
    buttons = []
    for i in chats[1:]:  # получаем имя группы
        i = i.split()
        buttons.append(types.InlineKeyboardButton(text=i[1], callback_data=i[0]))
    return buttons


@dp.message_handler()
async def mess_handler(message: types.Message):
    if message.chat.type != "private":
        if not db.user_exists(message.from_user.id, message.chat.id):
            db.add_user(message.from_user.id, message.chat.id)

        if not db.mute(message.from_user.id, message.chat.id):
            if check_sub_chanel(await bot.get_chat_member(chat_id=cfg.CHANEL_ID, user_id=message.from_user.id)):
                text = message.text.lower().split()
                if len(set(text).intersection(cfg.WORDS)) != 0:
                    await message.delete()
            else:
                await message.answer("Чтобы отправлять подпишитесь на канал", reply_markup=nav.chanelMenu)
                await message.delete()
        else:
            await message.delete()
    else:
        if message.text == 'Добавить бота':
            buttons = [
                types.InlineKeyboardButton(text="Перейти", callback_data="gen_code")
            ]
            print(buttons)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(*buttons)
            await message.bot.send_message(text="Заглушка", chat_id=message.chat.id, reply_markup=keyboard)
        elif message.text == 'Команды':
            keyboard = types.InlineKeyboardMarkup()
            a = generate_button(db.admin_chat(message.from_user.id))
            keyboard.add(*a)
            await message.bot.send_message(text="Заглушка 1", chat_id=message.chat.id, reply_markup=keyboard)


@dp.callback_query_handler()
async def callbacks_num(call: types.CallbackQuery):
    if call.data == 'gen_code':
        code = random.randint(100, 999)
        while db.check_code(code) != 0:
            code = random.randint(100, 999)
        db.add_code(call.from_user.id, code)
        await call.message.edit_text(f"Код: {code}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
