from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateInvestment(StatesGroup):
    type = State()
    category = State()
    quality = State()
    item = State()
    price = State()
    count = State()
