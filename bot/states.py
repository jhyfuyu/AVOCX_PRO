from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_price = State()
    waiting_for_channel = State()
    waiting_for_admin = State()
    waiting_for_theme = State()
    add_channel = State()


class Check(StatesGroup):
    waiting_for_username = State()
    waiting_for_post_or_name = State()


class SubscriberManagement(StatesGroup):
    waiting_for_count = State()
    waiting_for_time = State()
    waiting_for_inactivity = State()
    waiting_for_confirmation = State()


class CreativesPosts(StatesGroup):
    waiting_for_send_post = State()

class AutoPosting(StatesGroup):
    waiting_for_post_to_channel = State()
    waiting_for_select = State()
