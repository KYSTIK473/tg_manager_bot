from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config as cfg

btnUrlChanek = InlineKeyboardButton(text='Канал', url=cfg.CHANEL_URL)
chanelMenu = InlineKeyboardMarkup(row_width=1)
chanelMenu.insert(btnUrlChanek)