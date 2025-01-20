import telebot
import PIL as pil
import PIL.ImageOps
from PIL import Image
import io
from telebot import types
from random import randint

TOKEN = '7308792898:AAG29SEzQcPX10e0XCuDuvbuQbK_C19XYwc'
bot = telebot.TeleBot(TOKEN)

user_states = {}  # тут будем хранить информацию о действиях пользователя

# набор символов из которых составляем изображение
ASCII_CHARS = '@%#*+=-:. '
JOKES = ['Шутка №1', 'Шутка №2', 'Шутка №3', 'Шутка №4']
COMPLIMENTS = ['Комплимент №1', 'Комплимент №2', 'Комплимент №3', 'Комплимент №4']


def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def grayify(image):
    return image.convert("L")


def image_to_ascii(image_stream, new_width=40, ascii_chars_in=ASCII_CHARS):
    """ Функция преобразования изображения в зображение из символов заданной последовательности """
    # Переводим в оттенки серого
    image = Image.open(image_stream).convert('L')
    ''' Перевод изображения в оттенки серого '''
    # меняем размер сохраняя отношение сторон
    width, height = image.size
    aspect_ratio = height / float(width)
    new_height = int(
        aspect_ratio * new_width * 0.55)  # 0,55 так как буквы выше чем шире
    img_resized = image.resize((new_width, new_height))
    ''' Измененияе размера изображения с сохранением соотношения сторон '''
    img_str = pixels_to_ascii(img_resized, ascii_temp=ascii_chars_in)
    img_width = img_resized.width
    ''' Получение данных для окончательного преобразования '''
    max_characters = 4000 - (new_width + 1)
    max_rows = max_characters // (new_width + 1)
    ''' Определение максимального колличества строк и символов'''
    ascii_art = ""
    for i in range(0, min(max_rows * img_width, len(img_str)), img_width):
        ascii_art += img_str[i:i + img_width] + "\n"
    ''' Окончательное преобразование '''
    return ascii_art


def pixels_to_ascii(image, ascii_temp=ASCII_CHARS):
    """ Функция преобразования пиксилей в символы последовательности """
    pixels = image.getdata()
    characters = ""
    ''' Создание массива пиксилей '''
    for pixel in pixels:
        characters += ascii_temp[pixel * len(ascii_temp) // 256]
    ''' Заполнение строки символов '''
    return characters


# Огрубляем изображение
def pixelate_image(image, pixel_size):
    image = image.resize(
        (image.size[0] // pixel_size, image.size[1] // pixel_size),
        Image.NEAREST
    )
    image = image.resize(
        (image.size[0] * pixel_size, image.size[1] * pixel_size),
        Image.NEAREST
    )
    return image


def resize_for_sticker(image, size=256):
    """ Функция уменьшения размера изображения с сохранением соотношений сторон """
    resize_percent = (size / image.size[0])
    ''' Вычисление степени изменения '''
    vsize = int((image.size[1] * resize_percent))
    ''' Вычисление размера вертикали '''
    result_image = image.resize((size, vsize), Image.Resampling.LANCZOS)
    ''' Преобразование изображения '''
    return result_image


def invert_colors(image):
    """ Функция инвертирования цветов на изображение """
    reverse_art = pil.ImageOps.invert(image)
    ''' Вызов функции инвертирования цветов из библиотеки'''
    return reverse_art


def convert_to_heatmap(image):
    """ Функция преобразования изображения в тепловую карту """
    result_image = PIL.ImageOps.colorize(image, black="blue", white="red")
    '''Вызов функции преобразования изображения в тепловую карту'''
    return result_image


def flip_image(image, flip_type):
    """ Функция отражения изображения """
    if flip_type == "horizontally":
        flip_image = image.transpose(pil.Image.FLIP_LEFT_RIGHT)
    elif flip_type == "vertically":
        flip_image = image.transpose(pil.Image.FLIP_TOP_BOTTOM)
    ''' Отражение изображения по указанному направлению'''
    return flip_image


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """ Функция распознования получения сообщений /start и /help """
    bot.reply_to(message, "Select option from menu", reply_markup=get_start_keyboard())
    ''' Отправка ответного сообщения и вывод клавиатуры '''


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "I got your photo! Please choose what you'd like to do with it.",
                 reply_markup=get_options_keyboard())
    user_states[message.chat.id] = {'photo': message.photo[-1].file_id}


def get_start_keyboard():
    """ Клавиатура выбора взаимодействия """
    keyboard = types.InlineKeyboardMarkup()
    image_btn = types.InlineKeyboardButton("Image", callback_data="image")
    jokes_btn = types.InlineKeyboardButton("Jokes", callback_data="jokes")
    compliment_btn = types.InlineKeyboardButton("Compliment", callback_data="compliment")
    coin_btn = types.InlineKeyboardButton("Flip a coin", callback_data="coin")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(image_btn, jokes_btn, compliment_btn, coin_btn)
    ''' Создание кнопок '''
    return keyboard


def get_coin_keyboard():
    """ Клавиатура выбора вероятностей последовательности """
    keyboard = types.InlineKeyboardMarkup()
    heads_btn = types.InlineKeyboardButton("Heads", callback_data="heads")
    tails_btn = types.InlineKeyboardButton("Tails", callback_data="tails")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(heads_btn, tails_btn)
    ''' Создание кнопок '''
    return keyboard


def get_coin_result_keyboard():
    """ Клавиатура выбора вероятностей последовательности """
    keyboard = types.InlineKeyboardMarkup()
    reflip_btn = types.InlineKeyboardButton("One more time", callback_data="coin")
    flip_end_btn = types.InlineKeyboardButton("Return to start", callback_data="flip_end")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(reflip_btn, flip_end_btn)
    ''' Создание кнопок '''
    return keyboard


def get_options_keyboard():
    """ Клавиатура выбора действия применяемого к картинке """
    keyboard = types.InlineKeyboardMarkup()
    pixelate_btn = types.InlineKeyboardButton("Pixelate", callback_data="pixelate")
    ascii_btn = types.InlineKeyboardButton("ASCII Art", callback_data="ascii")
    reverse_btn = types.InlineKeyboardButton("Reverse", callback_data="revers")
    flip_btn = types.InlineKeyboardButton("flip", callback_data="flip")
    heatmap_btn = types.InlineKeyboardButton("heatmap", callback_data="heatmap")
    stiker_resize_btn = types.InlineKeyboardButton("stiker", callback_data="resize")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(pixelate_btn, ascii_btn, reverse_btn, flip_btn, heatmap_btn, stiker_resize_btn)
    ''' Создание кнопок '''
    return keyboard


def get_ascii_line_keyboard():
    """ Клавиатура выбора типа ASCII последовательности """
    keyboard = types.InlineKeyboardMarkup()
    pixelate_btn = types.InlineKeyboardButton("Default", callback_data="ascii_default")
    ascii_btn = types.InlineKeyboardButton("New", callback_data="ascii_new")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(pixelate_btn, ascii_btn)
    ''' Создание кнопок '''
    return keyboard


def get_resize_keyboard():
    """ Клавиатура выбора вида отражения """
    keyboard = types.InlineKeyboardMarkup()
    default_btn = types.InlineKeyboardButton("Default", callback_data="resize_default")
    set_size_btn = types.InlineKeyboardButton("Set size", callback_data="resize_set")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(default_btn, set_size_btn)
    ''' Создание кнопок '''
    return keyboard


def get_flip_keyboard():
    """ Клавиатура выбора вида отражения """
    keyboard = types.InlineKeyboardMarkup()
    horizontally_btn = types.InlineKeyboardButton("Horizontally", callback_data="flip_horizontally")
    vertically_btn = types.InlineKeyboardButton("Vertically", callback_data="flip_vertically")
    ''' Описание кнопок клавиатуры '''
    keyboard.add(horizontally_btn, vertically_btn)
    ''' Создание кнопок '''
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """ Обработчик инлайн клавиатур """
    if call.data == "pixelate":
        bot.answer_callback_query(call.id, "Pixelating your image...")
        pixelate_and_send(call.message)
        ''' Обработка кнопки пиксилизации '''
    elif call.data == "ascii":
        bot.reply_to(call.message, "Choose to use the default ASCII sequence or set your own.",
                     reply_markup=get_ascii_line_keyboard())
        ''' Обработка кнопки перерисовки в символах '''
    elif call.data == "revers":
        bot.answer_callback_query(call.id, "Revers your image color...")
        reverse_and_send(call.message)
        ''' Обработка кнопки реверса цветов изображения '''
    elif call.data == "flip":
        bot.reply_to(call.message, "Select reflect horizontally or vertically.",
                     reply_markup=get_flip_keyboard())
        ''' Обработка кнопки отражения изображения '''
    elif call.data == "heatmap":
        bot.answer_callback_query(call.id, "Build heatmap...")
        build_heatmap_and_send(call.message)
        ''' Обработка кнопки постройки тепловой карты '''
    elif call.data == "ascii_default":
        bot.answer_callback_query(call.id, "Converting your image to ASCII art...")
        use_text = False
        ascii_and_send(call.message, use_text)
        ''' Обработка кнопки отрисовки в базовой последоветельности символов '''
    elif call.data == "ascii_new":
        bot.send_message(call.message.chat.id, 'Enter your ASCII sequence (ten characters for the best result)')

        @bot.message_handler()
        def handle_ascii(message):
            bot.reply_to(message, "I got your ASCII sequence")
            use_this_text = True
            ascii_and_send(message, use_this_text)
        ''' Обработка кнопки отрисовки в задоваемой последоветельности символов '''
    elif call.data == "flip_horizontally":
        flip_and_send(call.message, "horizontally")
        ''' Обработка кнопки отражения изображения по горизонтали '''
    elif call.data == "flip_vertically":
        flip_and_send(call.message, "vertically")
        ''' Обработка кнопки отражения изображения по вертикали '''
    elif call.data == "resize":
        bot.reply_to(call.message, "Choose to use the default size (width = 256) or set your own.",
                     reply_markup=get_resize_keyboard())
        ''' Обработка кнопки перерисовки в символах '''
    elif call.data == "resize_default":
        bot.answer_callback_query(call.id, "Resize your image to 256 pixelart...")
        use_text = False
        resize_and_send(call.message, use_text)
        ''' Обработка кнопки изменения размера картинки с шириной в 256 пиксилей'''
    elif call.data == "resize_set":
        bot.send_message(call.message.chat.id, 'Enter your size (for example 256)')

        @bot.message_handler()
        def handle_resize(message):
            bot.reply_to(message, "I got size")
            use_text = True
            resize_and_send(message, use_text)
        ''' Обработка кнопки изменения размера картинки с заданой шириной '''
    elif call.data == "jokes":
        joke_text = joke_chose()
        bot.send_message(call.message.chat.id, f'{joke_text}')
        bot.send_message(call.message.chat.id, 'Maybe something else', reply_markup=get_start_keyboard())
        ''' Обработка кнопки отправки в чат случайной шутки '''
    elif call.data == "image":
        bot.send_message(call.message.chat.id, "Send me an image, and I'll provide options for you!")
        ''' Обработка кнопки старта работы с изображением '''
    elif call.data == "compliment":
        compliment_text = compliment_chose(call)
        bot.send_message(call.message.chat.id, f'{compliment_text}')
        bot.send_message(call.message.chat.id, 'Maybe something else', reply_markup=get_start_keyboard())
        ''' Обработка кнопки отправки в чат случайного комплимента '''
    elif call.data == "coin":
        bot.send_message(call.message.chat.id, 'Сhoose your side', reply_markup=get_coin_keyboard())
    elif call.data == "heads":
        result_text = flip_a_coin_and_send('Heads')
        bot.send_message(call.message.chat.id, f'{result_text}', reply_markup=get_coin_result_keyboard())
    elif call.data == "tails":
        result_text = flip_a_coin_and_send('Tails')
        bot.send_message(call.message.chat.id, f'{result_text}', reply_markup=get_coin_result_keyboard())
    elif call.data == "flip_end":
        bot.send_message(call.message.chat.id, "Select option from menu", reply_markup=get_start_keyboard())


def pixelate_and_send(message):
    """ Функция пиксилизирования изображения"""
    image_stream = image_take_from_message(message)
    image = Image.open(image_stream)
    ''' Выдиление присланного изображения '''
    pixelated = pixelate_image(image, 20)
    ''' Пиксилизация '''
    output_stream = io.BytesIO()
    pixelated.save(output_stream, format="JPEG")
    output_stream.seek(0)
    bot.send_photo(message.chat.id, output_stream)
    ''' Отправка результата '''


def reverse_and_send(message):
    """ Функция отправки результатов по преобразованию """
    image_stream = image_take_from_message(message)
    image = Image.open(image_stream)
    ''' Выдиление присланного изображения '''
    reversed_image = invert_colors(image)
    output_stream = io.BytesIO()
    reversed_image.save(output_stream, format="JPEG")
    output_stream.seek(0)
    ''' Подготовка результата '''
    bot.send_photo(message.chat.id, output_stream)
    ''' Отправка результата '''


def flip_a_coin_and_send(text):
    player_side = text
    sides = ['Heads', 'Tails']
    number = randint(0, 99)
    if number % 2 == 0:
        side = sides[0]
    else:
        side = sides[1]
    print(side)
    if side == player_side:
        result_text = f'Выпало {side}. Вы угадали'
    else:
        result_text = f'Выпало {side}. Вы не угадали'
    return (result_text)




def resize_and_send(message, use_text):
    """ Функция отправки результатов по преобразованию """
    image_stream = image_take_from_message(message)
    image = Image.open(image_stream)
    ''' Выдиление присланного изображения '''
    if use_text:
        sticker = resize_for_sticker(image, size=int(message.text))
    else:
        sticker = resize_for_sticker(image)
    output_stream = io.BytesIO()
    sticker.save(output_stream, format="JPEG")
    output_stream.seek(0)
    ''' Подготовка результата '''
    bot.send_photo(message.chat.id, output_stream)
    ''' Отправка результата '''


def build_heatmap_and_send(message):
    """ Функция отправки результатов по преобразованию """
    image_stream = image_take_from_message(message)
    grey_image = Image.open(image_stream).convert('L')
    ''' Выдиление присланного изображения '''
    heatmap_image = convert_to_heatmap(grey_image)
    output_stream = io.BytesIO()
    heatmap_image.save(output_stream, format="JPEG")
    output_stream.seek(0)
    ''' Подготовка результата '''
    bot.send_photo(message.chat.id, output_stream)
    ''' Отправка результата '''


def flip_and_send(message, flip_type):
    """ Функция отправки результатов по преобразованию """
    image_stream = image_take_from_message(message)
    image = Image.open(image_stream)
    ''' Выдиление присланного изображения '''
    temp_image = flip_image(image, flip_type)
    output_stream = io.BytesIO()
    temp_image.save(output_stream, format="JPEG")
    output_stream.seek(0)
    ''' Подготовка результата '''
    bot.send_photo(message.chat.id, output_stream)
    ''' Отправка результата '''


def ascii_and_send(message, use_text):
    """ Функция отправки результатов по преобразованию """
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image_stream = io.BytesIO(downloaded_file)
    ''' Выдиление присланного изображения '''
    if use_text:
        ascii_art = image_to_ascii(image_stream, ascii_chars_in=message.text)
    else:
        ascii_art = image_to_ascii(image_stream, ascii_chars_in=ASCII_CHARS)
    ''' Проверка используемой для преобразования последовательности '''
    bot.send_message(message.chat.id, f"```\n{ascii_art}\n```", parse_mode="MarkdownV2")
    ''' Отправка результата '''


def compliment_chose(message):
    """ Функция выбора случайного комплимента """
    name = message.from_user.first_name
    index = randint(0, len(COMPLIMENTS)-1)
    ''' Выбор номера комплимента из списка '''
    compliment_text = f' {name} ты {COMPLIMENTS[index]}'
    ''' Выбор комплимента по номеру '''
    return compliment_text

def joke_chose():
    """ Функция функция выбора случайной шутки """
    index = randint(0, len(JOKES)-1)
    ''' Выбор номера шутки из списка '''
    joke_text = JOKES[index]
    ''' Выбор шутки по номеру '''
    return joke_text


def image_take_from_message(message):
    """ Функция выделения изображения из чата"""
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image_stream = io.BytesIO(downloaded_file)
    ''' Выделение изображения'''
    return image_stream


bot.polling(none_stop=True)