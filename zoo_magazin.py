from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv, find_dotenv
from aiogram.types import CallbackQuery
from aiogram.types import ReplyKeyboardMarkup
from database import connection

import os

load_dotenv(find_dotenv())

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add('Каталог 🗂️').insert('Информация о магазине ❗')


def get_categories():
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT name_categories 
                FROM public.categories''')
            result = cursor.fetchall()
            categories = [row[0] for row in result]
            return categories

    finally:
        connection.commit()


def create_product_inline_keyboard():
    inline_keyboard = types.InlineKeyboardMarkup()
    categories = get_categories()
    for category in categories:
        inline_keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f'category_{category}'))

    return inline_keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Мы рады приветствовать вас в нашем телеграмм боте зоомагазина! 😸')
    await message.answer('Наше местоположение:')
    await bot.send_location(chat_id=message.chat.id, latitude=58.587313, longitude=49.663890, reply_markup=keyboard)
    await bot.send_sticker(message.from_user.id,
                           sticker='CAACAgIAAxkBAAJk2mVuaiRZ3JzzrajdS0ZD6jU5mldcAAKVHgAC4oIpSOvBo6-SQphqMwQ')


@dp.message_handler(text='Каталог 🗂️')
async def message_catalog(message: types.Message):
    inline_keyboard = create_product_inline_keyboard()
    await message.answer(f'Наш магазин содержит в себе следующие категории:', reply_markup=inline_keyboard)


@dp.message_handler(text='Информация о магазине ❗')
async def message_info(message: types.Message):
    await message.answer(f'Магазин расположен по адресу: Милицейская улица, дом 53')
    await message.answer(
        f'График работы магазина 🗓️:\n'
        f'Понедельник 10:00-19:00\n'
        f'Вторник 10:00-19:00\n'
        f'Среда 10:00-19:00\n'
        f'Четверг 10:00-19:00\n'
        f'Пятница 10:00-19:00\n'
        f'Воскресенье 10:00-17:00\n'
        f'Суббота  10:00-17:00\n')


@dp.callback_query_handler(lambda c: c.data.startswith('category_'))
async def inline_category_callback(query: CallbackQuery):
    selected_category = query.data.split('_')[1]
    product_info_list = get_product(category=selected_category)

    if product_info_list:
        for product_info in product_info_list:
            product_info_filtered = {
                'ID товара': product_info[0],
                'Наименование': product_info[1],
                'Категория': product_info[3],
                'Описание': product_info[4],
                'Количество': product_info[5],
                'Цена': product_info[6]
            }

            product_info_str = '\n'.join([f'{key}: {value}' for key, value in product_info_filtered.items()])
            image_data = product_info[2]
            await bot.send_photo(chat_id=query.message.chat.id, photo=image_data,
                                 caption=f'Информация о товаре:\n{product_info_str}')

        inline_keyboard = create_product_inline_keyboard()
        await query.message.answer(f'Также Вы можете посмотреть другие категории!:', reply_markup=inline_keyboard)
    else:
        await query.message.answer(f'Информация о продуктах в категории "{selected_category}" не найдена.')


def get_product(category=None):
    try:
        with connection.cursor() as cursor:
            if category:
                cursor.execute('''
                    SELECT P.id_product, P.name, I.url, C.name_categories || ' - ' || PC.name AS category, P.description, P.amount, P.price
                    FROM public.product P
                    JOIN public.categories_parent_category CPC ON P.id_category = CPC.id_categories_parent_category
                    JOIN parent_category PC ON CPC.id_parent_categories = PC.id_parent_category
                    JOIN public.categories C ON CPC.id_categories = C.id_categories
                    JOIN public.image I ON P.id_image = I.id_image
                    WHERE C.name_categories = %s
                ''', (category,))
            data = cursor.fetchall()
            return data
    finally:
        connection.commit()


@dp.message_handler()
async def chat_answer(message: types.Message):
    await message.reply('Я вас не понимаю, повторите запрос!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
