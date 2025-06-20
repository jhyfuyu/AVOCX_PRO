import pandas as pd
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
import asyncio


def read_csv_to_dict_pandas(filename):
    df = pd.read_csv(filename)
    return df.to_dict('records')


async def scanning_text(message: types.Message, user: str, flag: int):
    on_main = types.InlineKeyboardButton(text='На главную', callback_data='on_main_menu')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [on_main]
        ]
    )

    if flag == 0:
        await message.answer(f"Пользователь: {user}\nРезультат: не обнаружен в базах мошенников, но всё равно будьте внимательны и всё проверяйте.", reply_markup=keyboard)
    elif flag == 1:
        await message.answer(f"Пользователь: {user}\nРезультат: 🚨 Внимание!!!\nПользователь -- мошенник, не контактируйте с ним, он Вас обманет. Факт мошенничества найден в базах!.", reply_markup=keyboard)


async def check_user_data(message: types.Message, userid: str, path: str) -> str:
    data = read_csv_to_dict_pandas(path)
    is_dangerous: bool = False
    userid = None

    if message.forward_from:
        # Получаем ID канала из сообщения
        userid = message.forward_from.id
    else:
        userid = message.text

    for i in data:
        if str(i['id']) == userid:
            is_dangerous = data['is_dangerous']

    if is_dangerous:
        await scanning_text(message, userid, 1)
    else:
        await scanning_text(message, userid, 0)
