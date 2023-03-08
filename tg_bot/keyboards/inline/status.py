from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

change_status = CallbackData('edit_status', 'confirm')
status_choice_callback = CallbackData('status_choice', 'status')
select_selected_status = CallbackData('select_selected', 'action', 'status')
status_period_callback = CallbackData('status_period', 'status', 'period', 'price')

status_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='VIP', callback_data=status_choice_callback.new('vip'))
        ],
        [
            InlineKeyboardButton(text='Premium', callback_data=status_choice_callback.new('premium'))
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data=status_choice_callback.new('back'))
        ],
    ]
)


async def selection_selected_status(status):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Купить', callback_data=select_selected_status.new('buy', status))
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data=select_selected_status.new('back', 'None'))
            ]
        ]
    )
    return keyboard


async def status_period(status):
    status_prices = {
        'vip': (100, 250),
        'premium': (500, 1200)
    }
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='1 месяц', callback_data=status_period_callback.new(
                    status, 1, status_prices[status][0]
                )),
                InlineKeyboardButton(text='3 месяца', callback_data=status_period_callback.new(
                    status, 3, status_prices[status][1]
                )),
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data=select_selected_status.new('back', 'None'))
            ]
        ]
    )
    return keyboard

edit_status_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Обновить статус', callback_data=change_status.new('yes'))
        ]
    ]
)
