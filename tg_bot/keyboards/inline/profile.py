from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

status_callback = CallbackData('get_status', 'is_clicked')

status_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Статус', callback_data=status_callback.new(True))
        ]
    ]
)