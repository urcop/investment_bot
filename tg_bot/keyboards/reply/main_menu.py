from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton('Портфель 💼'),
            KeyboardButton('Пополнить баланс 💵'),
            KeyboardButton('Профиль 📝'),
        ],
        [
            KeyboardButton('Тех.Поддержка 👤'),
        ],

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
