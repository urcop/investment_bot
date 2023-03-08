from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

queue_item_callback = CallbackData('queue_item', 'item_id', 'queue_id')
accept_set_price_callback = CallbackData('accept_set_price', 'answer')


async def generate_item_keyboard(item_id, queue_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Принять', callback_data=queue_item_callback.new(item_id, queue_id))
            ]
        ]
    )
    return keyboard

accept_set_price_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data=accept_set_price_callback.new('yes')),
            InlineKeyboardButton(text='Нет', callback_data=accept_set_price_callback.new('no'))
        ]
    ]
)
