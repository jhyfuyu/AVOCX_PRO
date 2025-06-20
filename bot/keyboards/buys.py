import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter


async def process_buys(message: types.Message, bot, message_id=None, flag=1, parameters=[False, False, False, False, False, False, False, False, False]):
    words = {
        'date': 'Дата',
        'place': 'Место',
        'price': 'Цена',
        'creative': 'Креативы',
        'format': 'Формат',
        'admin': 'Админ',
        'link': 'Ссылка',
        'theme': 'Тематика',
        'back': 'Назад',
    }

    for (key, value) in enumerate(parameters):
        if value != False and value != '':
            words_key = list(words.keys())[key]
            words[words_key] = words[words_key] + '✅'
    print(words)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text=words['date'], callback_data='date'), 
     types.InlineKeyboardButton(text=words['place'], callback_data='place')],
    [types.InlineKeyboardButton(text=words['price'], callback_data='price'), 
     types.InlineKeyboardButton(text=words['format'], callback_data='format')],
    [types.InlineKeyboardButton(text=words['creative'], callback_data='select_creative'), 
     types.InlineKeyboardButton(text=words['admin'], callback_data='admin')],
    [types.InlineKeyboardButton(text=words['link'], callback_data='link'), 
     types.InlineKeyboardButton(text=words['theme'], callback_data='theme')],
    [types.InlineKeyboardButton(text=words['back'], callback_data='on_main_menu'), 
     types.InlineKeyboardButton(text='💫 Создать', callback_data='create_buy')]])
    
    # Редактируем предыдущее сообщение
    if flag == 0:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text="Отлично! Теперь заполните все необходимые данные чтобы лучше всё проанализировать и не упустить детали\n\n", 
            reply_markup=keyboard
            )
    elif flag == 1:
        await message.answer("Отлично! Теперь заполните все необходимые данные чтобы лучше всё проанализировать и не упустить детали\n\n", reply_markup=keyboard)


async def process_price(message: types.Message) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await message.edit_text("Внимательно!\nНапишите цену размещения по примеру\n\nПримеры:\n— Для фиксированной цены в рублях напишите «750»\n— Для цены за 1000 просмотров (по cpm*) напишите «750цпм», «750cpm»\n\nCPM - цена за тысячу просмотров\n! Цена по CPM рассчитывается за 24 часа !", reply_markup=keyboard)



async def buys_main_menu(callback: types.CallbackQuery) -> None:
    create = types.InlineKeyboardButton(text='Создать', callback_data='create')
    my_buys = types.InlineKeyboardButton(text='Мои закупы', callback_data='my_buys')
    creatives = types.InlineKeyboardButton(text='Креативы', callback_data='creatives')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [create], [my_buys], [creatives], [back]
        ]
    )
    await callback.message.edit_text(f'Давайте заливать трафик!\nКанал: {callback.data[4:]}\n- За неделю вы закупили на 0 руб.\n- Оплачено 0 руб. / Ожидают оплаты 0 руб.\n- За неделю подписалось: 0 / отписалось: 0', reply_markup=keyboard)


async def show_buttons(message, page: int, bot, buttons, flag=0):
    start_index = page * 4
    end_index = start_index + 4
    forward = types.InlineKeyboardButton(text='Вперед ➡️', callback_data=f'page_{page + 1}')
    back = types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'page_{page - 1}')
    creative = types.InlineKeyboardButton(text='+ Добавить креатив', callback_data="add_creative")
    keyboard_buttons = [[types.InlineKeyboardButton(text=f'{button_text[:10]}...', callback_data=f'creo_{buttons.index(button_text)}')] for button_text in buttons[start_index:end_index]] + [[creative], [back, forward]]

    # Создаем инлайн-клавиатуру
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=keyboard_buttons
    )

    await message.edit_text("Вот все добавленные креативы\n\nТут их можно - добавить и выбрать\nОбозначение (Крео1) - номер по порядку добавления для быстрого анализа", reply_markup=keyboard)


async def check_before_create(message: types.Message, data: dict, creative: str) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='💫 Создать', callback_data="final_create_buy")],
            [types.InlineKeyboardButton(text='Назад', callback_data="back")]
        ]
    )
    await message.edit_text(f"📨 Проверьте данные\n\n- Дата и время: {data['date']}\n- Название: {data['place']}\n- Цена: {data['price']}\n- Формат: {data['format']}\n- Креатив: {creative}\n- Админ: {data['admin']}\n- Ссылка: {data['link']}\n - Тематика: {data['theme']}\n\nНажмите «Далее», я создам готовый пост для отправки на размещение!", reply_markup=keyboard)


async def message_about_created(message: types.Message, data: dict, creative: str, link: str) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Подписаться', url=link)],
            [types.InlineKeyboardButton(text='Вернуться на главную', callback_data="on_main_menu")]
        ]
    )
    await message.edit_text(f"Закуп создан ботом @AVOCX\nДата и время: {data['date']}\n- Название: {data['place']}\n- Цена: {data['price']}  | Формат: {data['format']}\nРекламный пост ниже 👇")
    await message.answer(creative, reply_markup=keyboard)