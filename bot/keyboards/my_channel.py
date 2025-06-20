from aiogram import F
from aiogram import types
from aiogram import Dispatcher

dp = Dispatcher()

@dp.callback_query(lambda c: c.data.startswith('ch'))
async def payment_system(callback: types.CallbackQuery) -> None:
    await callback.answer(f'{callback[2:]}')

@dp.callback_query(F.data.in_(['back']))
async def payment_system(callback: types.CallbackQuery) -> None:
    await callback.message.delete()


async def reception_users(message: types.Message) -> None:
    pass
