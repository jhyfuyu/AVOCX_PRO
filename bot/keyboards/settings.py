import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter


async def settings_base(message: types.Message) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🌟 Подписка", callback_data="subscription"), types.InlineKeyboardButton(text="Язык: Russian", callback_data="language")],
        [types.InlineKeyboardButton(text="Часовой пояс: +3", callback_data="hours")],
        [types.InlineKeyboardButton(text="✅ Применить изменения", callback_data="save_settings")],
        [types.InlineKeyboardButton(text="Назад", callback_data="back"), types.InlineKeyboardButton(text="На главную", callback_data="on_main_menu")],
    ])
    await message.edit_text("⚙️ Настройки бота AVOCX\n\nЗдесь можно настроить работу с ботом, оплатить подписку, изменить часовой пояс и выбрать язык", reply_markup=keyboard)