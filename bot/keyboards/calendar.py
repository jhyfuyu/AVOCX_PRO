import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.types import ChatMemberUpdated
from database.controller import DBController
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext

# Функция для создания инлайн клавиатуры
def create_base_calendar(current_date):
    previous_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)

    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"< {str(previous_date)[:10]}", callback_data=f"prev:{previous_date}"), types.InlineKeyboardButton(text=current_date.strftime("%Y-%m-%d"), callback_data="current"), types.InlineKeyboardButton(text=f"{str(next_date)[:10]} >", callback_data=f"next:{next_date}")],
            [types.InlineKeyboardButton(text='Развернуть календарь', callback_data='all_calendar')],
            [types.InlineKeyboardButton(text='Назад', callback_data='back')]
        ]
    )
    return keyboard