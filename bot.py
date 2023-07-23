import logging
import sqlite3
import hashlib
import random
import string
from aiogram import Bot, Dispatcher, types, executor

# Вставьте ваш токен, полученный от BotFather
BOT_TOKEN = ""

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Инициализация логирования
logging.basicConfig(level=logging.INFO)


# Создание таблицы в базе данных SQLite при запуске бота
def create_table():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (token TEXT PRIMARY KEY, message TEXT)")
    conn.commit()
    conn.close()


# Функция для генерации токена
def generate_token(text):
    # Генерация случайной соли из 10 символов
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    # Конкатенация текста и соли
    data = text + salt
    # Хеширование данных с использованием sha256
    token = hashlib.sha256(data.encode()).hexdigest()
    return token
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    instructions = "Чтобы сохранить текст, просто отправьте его мне в сообщении.\nВы получите уникальный токен, по которому сможете получить текст в любой момент.\nДля получения текста используйте команду /get <токен>\nНапример: /get abcdef12345"

    await message.reply(instructions)


# Обработка входящего сообщения
@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_message(message: types.Message):
    text = message.text.strip()
    if text.startswith("/get"):
        await get_message(message)
    elif text:
        token = generate_token(text)
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (token, message) VALUES (?, ?)", (token, text))
        conn.commit()
        conn.close()
        await message.reply(f"{token}")
    else:
        await message.reply("Введите текст для сохранения.")


# Команда /get <токен>
async def get_message(message: types.Message):
    args = message.get_args()
    if args:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT message FROM messages WHERE token=?", (args,))
        result = cursor.fetchone()
        conn.close()
        if result:
            await message.reply(f" {result[0]}")
        else:
            await message.reply("Текст с указанным токеном не найден.")
    else:
        await message.reply("Для получения текста используйте команду /get <токен>")


if __name__ == "__main__":
    create_table()
    executor.start_polling(dp, skip_updates=True)
