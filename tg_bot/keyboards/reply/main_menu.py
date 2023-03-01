from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton('Портфель 💼'),
            KeyboardButton('Профиль 📝'),
        ],
        [
            KeyboardButton('Тех.Поддержка 👤'),
        ],
        [
            KeyboardButton('Пополнить баланс 💵'),

        ]
    ]
)

back_main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton('⏪Назад')
        ]
    ]
)
