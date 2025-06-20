import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    MEMBER,
    ADMINISTRATOR,
    KICKED
)
from aiogram.types import ChatMemberUpdated
from database.controller import DBController
from database.check_user import check_user_data
from keyboards.my_channel import *
from keyboards.buys import *
from keyboards.settings import *
from api import tg_stat_api
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from states import *
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.calendar import create_base_calendar
import os


TOKEN = "8075232394:AAGMxqUIIM9CvD_DioQWMdnxXWP5qbClacQ"

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
CHANNEL_ADMINS = {"ids": []} # Заменить на базу данных
db_controller = DBController("sqlite:///database/main.db")


async def main_menu(message: types.Message, flag=0) -> None:
    bot_id = (await bot.get_me()).id
    post = types.InlineKeyboardButton(text='Постинг', callback_data='post')
    scan = types.InlineKeyboardButton(text='Сканнинг', callback_data='scan')
    buys = types.InlineKeyboardButton(text='Закупы', callback_data='buys')
    calendar = types.InlineKeyboardButton(text='Календарь', callback_data='calendar')
    analysis = types.InlineKeyboardButton(text='Аналитика', callback_data='analysis')
    my_channels = types.InlineKeyboardButton(text='Мои каналы', callback_data='my_channels')
    auto_recept = types.InlineKeyboardButton(text='Автоприем', callback_data='auto_recept')
    security = types.InlineKeyboardButton(text='Защита', callback_data='security') 
    settings = types.InlineKeyboardButton(text='Настройки', callback_data='settings')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [post, scan], [buys, calendar],
            [analysis, my_channels], [auto_recept, security], 
            [settings]
        ]
    )
    # Проверяем, является ли сообщение пересланным
    if message.forward_from_chat:
        # Получаем ID канала
        channel_id = message.forward_from_chat.id
        administrators = await bot.get_chat_administrators(channel_id)
        admin_ids = []

        for admin in administrators:
            admin_ids.append((str(admin.user.id),))
        for admin in administrators:
            if admin.user.id == bot_id:
                if (str(channel_id),) not in db_controller.get_all_users(type='channel'):
                    db_controller.register_channel(message.forward_from_chat.full_name, channel_id, message.from_user.id)
                    # Исправить на эдит текст
                    await bot.send_message(message.from_user.id, text=f"Отлично!\n\nКанал {message.forward_from_chat.full_name} успешно добавлен в супербота!")
                else:
                    await message.answer("Ошибка: канал был добавлен в супербота ранее!")
    if flag != 0:
        await message.edit_text('Главное меню супербота @avocx\n\nФункции и описание можно изучить в официальном канале: @avocx_dev\nПоддержка: @avocx_support_bot', reply_markup=keyboard)
    else:
        await message.answer('Главное меню супербота @avocx\n\nФункции и описание можно изучить в официальном канале: @avocx_dev\nПоддержка: @avocx_support_bot', reply_markup=keyboard)


@dp.message(Command("start"))
async def start_message(message: types.Message) -> None:
    if db_controller.check_user(message.from_user.id) == []:
        db_controller.register_user(message.from_user.username, message.from_user.id)

    back = types.InlineKeyboardButton(text='Назад', callback_data='on_main_menu')
    add_channel = types.InlineKeyboardButton(text='Добавить канал', callback_data='add_channel_to_db')    

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[add_channel], [back]])
    await message.answer("Как добавить канал?\n\n1 этап\nДобавьте бота в канал подписчиком\nВыдайте права админа на:\n+ Добавление подписчиков\n+Управление сообщениями\n+Добавление администраторов\n\n2 этап\nПерешлите в бота любое сообщение из канала, он будет автоматически добавлен", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == 'add_channel_to_db')
async def process_channel_add(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Перешлите сюда сообщение из канала, в который бот добавлен админом")
    await state.set_state(Form.add_channel)
    

@dp.callback_query(F.data.in_(['buys']))
async def payment_system(callback: types.CallbackQuery) -> None:
    channels = [i[0] for i in db_controller.get_user_channels(callback.from_user.id)]
    network = types.InlineKeyboardButton(text='Сеть каналов', callback_data='network_ch')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [network], [types.InlineKeyboardButton(text=i, callback_data=f'buy_{i}') for i in channels], [back]
        ]
    )
    await callback.message.answer('Выбор площадки\nВыберите из списка для дальнейших действий', reply_markup=keyboard)


@dp.callback_query(F.data.in_(['analysis']))
async def payment_system(callback: types.CallbackQuery) -> None:
    channels = [i[0] for i in db_controller.get_user_channels(callback.from_user.id)]
    network = types.InlineKeyboardButton(text='Сеть каналов', callback_data='network_ch')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [network], [types.InlineKeyboardButton(text=i, callback_data=f'stat_{i}') for i in channels], [back]
        ]
    )
    await callback.message.answer(f'Аналитика за календарный месяц\nПо всем каналам:\n- - - - - - - - - - - - - - - - -\nВсего доход с рекламы: 0 руб.\nВсего расходов на закупы: 0 руб.\nВсего продано реклам: 0\nВсего куплено реклам: 0\n- - - - - - - - - - - - - - - - -\n Итого за месяц: 0 руб.', reply_markup=keyboard)


@dp.callback_query(F.data.in_(['my_channels']))
async def payment_system(callback: types.CallbackQuery) -> None:
    channels = [i[0] for i in db_controller.get_user_channels(callback.from_user.id)]
    net_ch = types.InlineKeyboardButton(text="Сеть каналов", callback_data='net_ch')
    add_channel = types.InlineKeyboardButton(text='+ Добавить канал', callback_data='add_ch_')
    back = types.InlineKeyboardButton(text='Назад', callback_data='on_main_menu')
    keyboard_buttons = [[net_ch], [add_channel]] + [[types.InlineKeyboardButton(text=i, callback_data=f'ch_{i}')] for i in channels] + [[back]]
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=keyboard_buttons
    )
    await callback.message.answer(f"Мои каналы\n{'; '.join(channels)}\n- Выберите канал для дальнейших действий", reply_markup=keyboard)

temprorary_data = {}

@dp.callback_query(lambda c: c.data == 'post')
async def posting_main(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Pro-постинг только в @AVOCX\nОтправьте сюда то, что хотите опубликовать")
    await state.set_state(AutoPosting.waiting_for_post_to_channel)
    await state.update_data(message_id=callback.message.message_id, flag=1)


@dp.callback_query(lambda c: c.data.startswith('buy'))
async def buys_main(callback: types.CallbackQuery) -> None:
    await buys_main_menu(callback)

@dp.callback_query(lambda c: c.data == 'create')
async def process_create_button(callback: types.CallbackQuery):
    temprorary_data[callback.from_user.id] = {
        'date': '',
        'place': '',
        'price': '',
        'creative': '',
        'format': '',
        'admin': '',
        'link': '',
        'theme': '',
        'back': '',
    }
    await process_buys(callback.message, bot, callback.message.message_id, flag=0)


@dp.callback_query(lambda c: c.data == 'creatives')
async def process_create_button(callback: types.CallbackQuery):
    creatives = db_controller.get_creatives(callback.from_user.id)
    buttons = [i[2] for i in creatives]
    await show_buttons(callback.message, 0, bot, buttons)

@dp.callback_query(lambda c: c.data == 'back_to_main')
async def process_create_button(callback: types.CallbackQuery):
    await process_buys(callback.message, bot, message_id=callback.message.message_id, flag=0)


@dp.callback_query(lambda c: c.data == 'add_creative')
async def process_creative_add(callback: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await callback.message.answer("Отправьте мне креатив\nЯ его добавлю в ваше хранилище, его можно будет использовать при закупке рекламы", reply_markup=keyboard)
    await state.set_state(CreativesPosts.waiting_for_send_post)


@dp.callback_query(F.data.in_(['final_add_creative']))
async def final_add_creative(callback: types.CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    db_controller.add_creative(callback.from_user.id, user_data['channel'])
    await callback.message.answer(f"Добавлен новый креатив\nНазвание: {user_data['channel'][:20]}")


@dp.callback_query(lambda c: c.data == 'date')
async def process_date_button(callback: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await callback.message.answer("Укажите дату:", reply_markup=keyboard)
    await state.set_state(Form.waiting_for_date)
    

@dp.callback_query(lambda c: c.data == 'price')
async def process_price_button(callback: types.CallbackQuery, state: FSMContext):
    await process_price(callback.message)
    print(callback.message.message_id)
    await state.set_state(Form.waiting_for_price)  # Устанавливаем состояние ожидания цены
    await state.update_data(message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == 'place')
async def process_place_button(callback: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await callback.message.edit_text("Укажите название канала или перешлите сообщение оттуда:", reply_markup=keyboard)
    await state.set_state(Form.waiting_for_channel)
    await state.update_data(message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == 'admin')
async def process_addmin(callback: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await callback.message.edit_text('👤 Укажите админа / менеджера.\nПерешли сюда любое его сообщение либо напиши юзернейм в формате @username', reply_markup=keyboard)
    await state.set_state(Form.waiting_for_admin)
    await state.update_data(message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == 'theme')
async def process_addmin(callback: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='back')]
    ])
    await callback.message.edit_text('Тематика площадки\n\nНапишите название тематики со своих слов, главное - понять потом\nПримеры: «Психо», «Литра», «Цитаты» и т.д.', reply_markup=keyboard)
    await state.set_state(Form.waiting_for_theme)
    await state.update_data(message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == 'format')
async def process_place_button(callback: types.CallbackQuery) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='1/24', callback_data='format_1/24'),
         types.InlineKeyboardButton(text='2/24', callback_data='format_2/24'),
         types.InlineKeyboardButton(text='1/48', callback_data='format_1/48'),
         types.InlineKeyboardButton(text='2/48', callback_data='format_2/48')],
        [types.InlineKeyboardButton(text='1/72', callback_data='format_1/72'),
         types.InlineKeyboardButton(text='2/72', callback_data='format_2/72'),
         types.InlineKeyboardButton(text='1/168', callback_data='format_1/168'),
         types.InlineKeyboardButton(text='Б/У', callback_data='format_Б/У')],
        [types.InlineKeyboardButton(text='1/72', callback_data='format_Ночь/24'),
         types.InlineKeyboardButton(text='2/72', callback_data='format_Ночь/48'),
         types.InlineKeyboardButton(text='1/168', callback_data='format_Ночь/72'),
         types.InlineKeyboardButton(text='Б/У', callback_data='format_ВП')],
        [types.InlineKeyboardButton(text='Рассылка/бот', callback_data='format_Рассылка/бот'),
         types.InlineKeyboardButton(text='Закреп', callback_data='format_Закреп')],
         [types.InlineKeyboardButton(text='УБТ', callback_data='format_УБТ'),
         types.InlineKeyboardButton(text='Сторис', callback_data='format_Сторис')],
    ])
    await callback.message.edit_text("Выберите формат размещения\n\nНужна помощь? Напиши в @avocx_support_bot", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('format_'))
async def posting_handler(callback: types.CallbackQuery) -> None:
    callback_data = callback.data[7:]
    temprorary_data[callback.from_user.id]['format'] = callback_data
    print(temprorary_data)
    await process_buys(callback.message, bot, message_id=callback.message.message_id, flag=0, parameters=temprorary_data[callback.from_user.id].values())


@dp.callback_query(lambda c: c.data == 'select_creative')
async def creative_for_buy(callback: types.CallbackQuery) -> None:
    creatives = db_controller.get_creatives(callback.from_user.id)
    data = [i[2] for i in creatives]
    print(data)
    await show_buttons(callback.message, 0, bot, data)


@dp.callback_query(lambda c: c.data.startswith('page_'))
async def handle_page_change(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await callback_query.answer() # Убираем кружок загрузки
    await show_buttons(callback_query.message.chat.id, page)


@dp.callback_query(lambda c: c.data.startswith('creo_'))
async def handle_page_change(callback: types.CallbackQuery):
    creatives = db_controller.get_creatives(callback.from_user.id)
    data = [i[2] for i in creatives]
    temprorary_data[callback.from_user.id]['creative'] = data[int(callback.data[5])]
    await process_buys(callback.message, bot, message_id=callback.message.message_id, flag=0, parameters=temprorary_data[callback.from_user.id].values())


@dp.callback_query(lambda c: c.data == 'create_buy')
async def create_new_buy(callback: types.CallbackQuery) -> None:
    creative = temprorary_data[callback.from_user.id]['creative']
    creatives = db_controller.get_creatives(callback.from_user.id)
    data = [i[2] for i in creatives]
    creo_id = data.index(creative)
    await check_before_create(callback.message, temprorary_data[callback.from_user.id], f'Крео {creo_id}')


@dp.callback_query(lambda c: c.data == 'final_create_buy')
async def create_buy(callback: types.CallbackQuery) -> None:
    db_controller.add_buy(callback.from_user.id, temprorary_data[callback.from_user.id])
    await message_about_created(callback.message, temprorary_data[callback.from_user.id], temprorary_data[callback.from_user.id]['creative'], 't.me/avocx_beta_bot')


@dp.callback_query(lambda c: c.data.startswith('post_'))
async def posting_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_post'),
             types.InlineKeyboardButton(text='Изменить медиа', callback_data='edit_media')],
            [types.InlineKeyboardButton(text='Звук: 🔔 вкл.', callback_data='sound_post'),
             types.InlineKeyboardButton(text='Кнопка URL', callback_data='url_button_post')],
            [types.InlineKeyboardButton(text='Отмена', callback_data='on_main_menu'),
             types.InlineKeyboardButton(text='Далее', callback_data='enter_post')]
        ]
    )

    state_data = await state.get_data()
    text = state_data['text']
    msg_id = state_data['message_id']
    
    message_id = callback.message.message_id


@dp.callback_query(lambda c: c.data == 'edit_post')
async def edit_post(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(message_id=callback.message.message_id, flag=1)
    await callback.message.edit_text("Заменить текст? Отправьте его сюда") # Заменить на отправку с удалением и редакт предыдущ
    await state.set_state(AutoPosting.waiting_for_post_to_channel)


@dp.callback_query(lambda c: c.data.startswith('ch'))
async def my_channels_handler(callback: types.CallbackQuery) -> None:
    await callback.message.delete()
    add_net = types.InlineKeyboardButton(text='+ Добавить в сеть', callback_data=f'add_{callback.data[3:]}')
    ex_net = types.InlineKeyboardButton(text='Исключить из сети каналов', callback_data=f'ex_net_{callback.data[3:]}')
    ex_bot = types.InlineKeyboardButton(text='Удалить из бота', callback_data=f'delete_{callback.data[3:]}')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [add_net], [ex_net], [ex_bot], [back]
        ]
    )
    await callback.message.answer(f'Выбран канал: {callback.data[3:]}\n\nВыберите действие:', reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('stat'))
async def my_channels_handler(callback: types.CallbackQuery) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='on_main_menu')]])
    await callback.message.edit_text(f'Аналитика за календарный месяц\nКанал: {callback.data[5:]}\n- - - - - - - - - - - - - - - - -\nВсего доход с рекламы: 0 руб.\nВсего расходов на закупы: 0 руб.\nВсего продано реклам: 0\nВсего куплено реклам: 0\nСредний чек: 0 руб.\nСредняя цена за пдп: 0 руб.\n- - - - - - - - - - - - - - - - -\n Итого за месяц: 0 руб.', reply_markup=keyboard)


@dp.callback_query(F.data.in_(['calendar']))
async def calendar_handler(callback: types.CallbackQuery) -> None:
    channels = [i[0] for i in db_controller.get_user_channels(callback.from_user.id)]
    network = types.InlineKeyboardButton(text='Сеть каналов', callback_data='network_cal')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [network], [types.InlineKeyboardButton(text=i, callback_data=f'calend_{i}') for i in channels], [back]
        ]
    )
    await callback.message.answer('Выбор площадки\nВыберите из списка для дальнейших действий', reply_markup=keyboard)



@dp.callback_query(lambda c: c.data.startswith('calend'))
async def my_channels_handler(callback: types.CallbackQuery) -> None:
    current_date = datetime.now()
    await callback.message.answer('Это календарь с отметками!\n\n Здесь можно увидеть отметки, отложки по датам\n\nВыберите нужный месяц и день!', reply_markup=create_base_calendar(current_date))


@dp.callback_query(lambda c: c.data.startswith(('prev:', 'next:')))
async def handle_date_change(callback_query: types.CallbackQuery):
    data = callback_query.data.split(":")
    
    if data[0] == "prev":
        current_date = data[1]
    elif data[0] == "next":
        current_date = data[1]
    else:
        return

    await callback_query.message.edit_reply_markup(reply_markup=create_base_calendar(current_date))
    await callback_query.answer()


@dp.callback_query(F.data.in_(['scan']))
async def scan_users_and_channels(callback: types.CallbackQuery) -> None:
    channel = types.InlineKeyboardButton(text='Канал', callback_data='scan_channel')
    user = types.InlineKeyboardButton(text='Пользователь', callback_data='scan_user')
    scam = types.InlineKeyboardButton(text='Сообщить о скаме', callback_data='scam')
    back = types.InlineKeyboardButton(text='Назад', callback_data='on_main_menu')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [channel, user],
            [scam],
            [back]
        ]
    )
    await callback.message.edit_text('Здесь можно:\n-- Проверить канал по метрикам\n-- Проверить пользователя на скам', reply_markup=keyboard)


@dp.callback_query(F.data.in_(['scan_user']))
async def scan_channel_by_metrics(callback: types.CallbackQuery, state: FSMContext) -> None:
    back = types.InlineKeyboardButton(text='В главное меню', callback_data='on_main_menu')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [back]
        ]
    )
    await callback.message.edit_text('Проверить пользователя на скам.\nИз чата перешлите сюда любое сообщение или напишите имя в формате - "@username"', reply_markup=keyboard)
    await state.set_state(Check.waiting_for_username)

@dp.callback_query(F.data.in_(['scan_channel']))
async def scan_channel_by_metrics(callback: types.CallbackQuery, state: FSMContext) -> None:
    back = types.InlineKeyboardButton(text='В главное меню', callback_data='on_main_menu')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [back]
        ]
    )
    await callback.message.edit_text('Проверить канал по метрикам.\nИз канала перешлите сюда любое сообщение или напишите юзернейм в формате - "@username"', reply_markup=keyboard)
    await state.set_state(Check.waiting_for_post_or_name)
    await state.update_data(message_id=callback.message.message_id)


@dp.callback_query(F.data.in_(['auto_recept']))
async def auto_user_reception(callback: types.CallbackQuery) -> None:
    autorecept = None
    autorecept = types.InlineKeyboardButton(text='Автоприем: 🚫', callback_data=f'reception_{callback.from_user.id}')
    autorecept = types.InlineKeyboardButton(text='Автоприем: ✅', callback_data=f'reception_{callback.from_user.id}')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    ])

    await callback.message.edit_text("Приму подписчиков за вас!\n\nМожно указать таймер времени после которого я буду принимать подписчиков в канал", reply_markup=keyboard)


@dp.callback_query(F.data.in_(['security']))
async def auto_user_reception(callback: types.CallbackQuery) -> None:
    channels = [i[0] for i in db_controller.get_user_channels(callback.from_user.id)]
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=i, callback_data=f'secure_{i}') for i in channels], [back]
        ]
    )
    await callback.message.answer("🛡 Бот @AVOCX защитит канал.\n\n— Для начала выберите канал для защиты\n— Если его нет в списке, нажмите Добавить канал", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('secure_'))
async def manage_subscribers(callback: types.CallbackQuery, state: FSMContext):   
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Последние подписавшиеся", callback_data="last_subscribers")],
        [types.InlineKeyboardButton(text="За определенное время", callback_data="time_based")],
        [types.InlineKeyboardButton(text="Неактивные подписчики", callback_data="inactive_subscribers")]
    ])
    
    await callback.message.answer("Выберите тип фильтрации подписчиков:", reply_markup=keyboard)
        

@dp.callback_query(F.data.in_(['on_main_menu']))
async def on_main_menu(callback: types.CallbackQuery) -> None:
    await main_menu(callback.message, flag=1)


@dp.callback_query(F.data.in_(['settings']))
async def process_settings_menu(callback: types.CallbackQuery) -> None:
    await settings_base(callback.message)


@dp.callback_query()
async def handle_management_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "last_subscribers":
        await callback.message.edit_text("Введите количество подписчиков для удаления:")
        await state.set_state(SubscriberManagement.waiting_for_count)
        
    elif callback.data == "time_based":
        await callback.message.edit_text("Введите время в минутах для фильтрации:")
        await state.set_state(SubscriberManagement.waiting_for_time)
        
    elif callback.data == "inactive_subscribers":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="7 дней", callback_data="7d"), types.InlineKeyboardButton(text="14 дней", callback_data="14d")],
            [types.InlineKeyboardButton(text="1 месяц", callback_data="1m"), types.InlineKeyboardButton(text="3 месяца", callback_data="3m")],
        ])
        await callback.message.edit_text("Выберите период неактивности:", reply_markup=keyboard)
        await state.set_state(SubscriberManagement.waiting_for_inactivity)


@dp.callback_query(F.data.in_(['back']))
async def back_msg(callback: types.CallbackQuery) -> None:
    await callback.message.delete()


""" Хэндлеры для обработки состояний """
@dp.message(Check.waiting_for_username, F.text)
async def process_check_by_username(message: types.Message, state: FSMContext):
    current_dir = os.path.dirname(__file__)
    relative_path = os.path.join(current_dir, 'database', 'export_scammers.csv')

    await check_user_data(message, message.text, relative_path)


@dp.message(Check.waiting_for_post_or_name, F.text)
async def process_check_channel(message: types.Message, state: FSMContext):
    channel_name: str = ''
    msg_id = await(state.get_data())

    if message.forward_from_chat:
        # Получаем ID канала из сообщения
        channel_name = message.forward_from_chat.username
    else:
        if message.text.startswith(('@',)):
            channel_name = message.text
    
    channel_stats = tg_stat_api.get_channel_stats(channel_name)
    result = '\n'.join(f"{key}: {value}" for key, value in channel_stats.items())

    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    on_main = types.InlineKeyboardButton(text='На главную', callback_data='on_main_menu')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [back, on_main]
        ]
    )

    await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id['message_id'],
            text=f'Проверил супербот @AVOCX\n\n{result}', 
            reply_markup=keyboard
        )
    await message.delete()


@dp.message(AutoPosting.waiting_for_post_to_channel, F.text)
async def process_channel_for_posting(message: types.Message, state: FSMContext):
    channels = [i[0] for i in db_controller.get_user_channels(message.from_user.id)]
    network = types.InlineKeyboardButton(text='Сеть каналов', callback_data='network_ch')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [network], [types.InlineKeyboardButton(text=i, callback_data=f'post_{i}') for i in channels], [back]
        ]
    )
    data = await state.get_data()
    message_id = data['message_id']
    flag = data['flag']
    await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text="Выбор площадки\nВыберите из списка для дальнейших действий", 
            reply_markup=keyboard
            )
    await state.update_data(text=message.text)
    if flag == 1:
        await message.delete()


@dp.message(Form.waiting_for_date, F.text)
async def process_date(message: types.Message, state: FSMContext):
    date = message.text
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='back')]])
    await message.answer("Напишите во сколько по МСК планируется выход поста, по одному из примеров", reply_markup=keyboard)
    temprorary_data[message.from_user.id]['date'] = date
    await state.set_state(Form.waiting_for_time)  # Устанавливаем состояние ожидания времени


@dp.message(Form.waiting_for_time, F.text)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)  # Сохраняем время
    temprorary_data[message.from_user.id]['date'] += f' {message.text}'
    message_id = message.message_id
    for i in range(message_id, message.message_id - 4, -1):
        await message.bot.delete_message(chat_id=message.chat.id, message_id=i)
    await process_buys(message, bot, message_id=message.message_id-4, flag=0, parameters=temprorary_data[message.from_user.id].values())


@dp.message(Form.waiting_for_price, F.text)
async def price_button(message: types.Message, state: FSMContext):
    msg_id = await(state.get_data())
    temprorary_data[message.from_user.id]['price'] = message.text
    await process_buys(message, bot, message_id=msg_id['message_id'], flag=0, parameters=temprorary_data[message.from_user.id].values())
    await message.delete()


@dp.message(Form.waiting_for_channel, F.text)
async def process_channel_name(message: types.Message, state: FSMContext):
    msg_id = await(state.get_data())
    temprorary_data[message.from_user.id]['place'] = message.text
    await process_buys(message, bot, message_id=msg_id['message_id'], flag=0, parameters=temprorary_data[message.from_user.id].values())
    await message.delete()


@dp.message(Form.waiting_for_admin, F.text)
async def process_admin_name(message: types.Message, state: FSMContext):
    msg_id = await(state.get_data())
    temprorary_data[message.from_user.id]['admin'] = message.text
    await process_buys(message, bot, message_id=msg_id['message_id'], flag=0, parameters=temprorary_data[message.from_user.id].values())
    await message.delete()


@dp.message(Form.waiting_for_theme, F.text)
async def process_admin_name(message: types.Message, state: FSMContext):
    msg_id = await(state.get_data())
    temprorary_data[message.from_user.id]['theme'] = message.text
    await process_buys(message, bot, message_id=msg_id['message_id'], flag=0, parameters=temprorary_data[message.from_user.id].values())
    await message.delete()


@dp.message(Form.add_channel)
async def process_add_channel_to_db(message: types.Message, state: FSMContext):
    await main_menu(message)


@dp.message(CreativesPosts.waiting_for_send_post, F.text)
async def save_creative(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Изменить текст", callback_data="edit_text"),
             types.InlineKeyboardButton(text="Изменить медиа", callback_data="edit_media")],
            [types.InlineKeyboardButton(text="Спойлер", callback_data="spoiler"),
             types.InlineKeyboardButton(text="Кнопки URL", callback_data="url_buttons")],
            [types.InlineKeyboardButton(text="💫 Добавить", callback_data="final_add_creative"),
             types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
    await state.update_data(channel=message.text)
    await message.delete()
    await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id-1,
            text=message.text,
            reply_markup=keyboard
    )

@dp.message(SubscriberManagement.waiting_for_count, F.text)
async def handle_count_input(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        if count <= 0:
            await message.answer("Введите положительное число")
            return
            
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
        
        await message.answer(f"Вы собираетесь удалить {count} последних подписчиков. Подтвердите действие:", 
                           reply_markup=keyboard)
        await state.update_data(count=count)
        await state.set_state(SubscriberManagement.waiting_for_confirmation)
        
    except ValueError:
        await message.answer("Введите корректное число")

@dp.message(SubscriberManagement.waiting_for_time, F.text)
async def handle_time_input(message: types.Message, state: FSMContext):
    try:
        minutes = int(message.text)
        if minutes <= 0:
            await message.answer("Введите положительное число")
            return
            
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
        
        await message.answer(f"Вы собираетесь удалить подписчиков, которые подписались {minutes} минут назад. Подтвердите действие:", 
                           reply_markup=keyboard)
        await state.update_data(minutes=minutes)
        await state.set_state(SubscriberManagement.waiting_for_confirmation)
        
    except ValueError:
        await message.answer("Введите корректное число")

@dp.callback_query(SubscriberManagement.waiting_for_inactivity, F.text)
async def handle_inactivity_choice(callback: types.CallbackQuery, state: FSMContext):
    periods = {
        "7d": timedelta(days=7),
        "14d": timedelta(days=14),
        "1m": timedelta(days=30),
        "3m": timedelta(days=90)
    }
    
    if callback.data in periods:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
        
        period = periods[callback.data]
        await callback.message.edit_text(f"Вы собираетесь удалить подписчиков, не активных более {period.days} дней. Подтвердите действие:", 
                                       reply_markup=keyboard)
        await state.update_data(period=period)
        await state.set_state(SubscriberManagement.waiting_for_confirmation)


@dp.callback_query(SubscriberManagement.waiting_for_confirmation, F.text)
async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "confirm":
        data = await state.get_data()
        
        try:
            chat_members = await callback.bot.get_chat_members_count(callback.message.chat.id)
            
            if 'count' in data:
                # Удаление последних подписчиков
                members = await callback.bot.get_chat_members(callback.message.chat.id, limit=data['count'])
                for member in members:
                    await callback.bot.ban_chat_member(callback.message.chat.id, member.user.id)
                    
            elif 'minutes' in data:
                # Удаление по времени подписки
                current_time = datetime.now()
                target_time = current_time - timedelta(minutes=data['minutes'])
                
                members = await callback.bot.get_chat_members(callback.message.chat.id)
                for member in members:
                    if member.joined_date and member.joined_date < target_time:
                        await callback.bot.ban_chat_member(callback.message.chat.id, member.user.id)
                        
            elif 'period' in data:
                # Удаление неактивных подписчиков
                current_time = datetime.now()
                target_time = current_time - data['period']
                
                members = await callback.bot.get_chat_members(callback.message.chat.id)
                for member in members:
                    if member.last_seen and member.last_seen < target_time:
                        await callback.bot.ban_chat_member(callback.message.chat.id, member.user.id)
                        
            await callback.message.edit_text("Операция выполнена успешно!")
            
        except Exception as e:
            await callback.message.edit_text(f"Произошла ошибка: {str(e)}")
            
    elif callback.data == "cancel":
        await callback.message.edit_text("Операция отменена")

""" Запуск бота """
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
