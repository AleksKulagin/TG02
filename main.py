from config import TOKEN
import logging
import os
import asyncio
from aiogram.types import FSInputFile, Message
from aiogram.filters import Command
from gtts import gTTS
from googletrans import Translator
from aiogram import Bot, Dispatcher, Router, F

API_TOKEN = TOKEN

# Установите уровень логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация переводчика
translator = Translator()

# Создайте папку для хранения изображений, если она не существует
if not os.path.exists('img'):
    os.makedirs('img')


@router.message(Command("start"))
async def start_command(message: Message):
    await message.reply("Привет, Я бот. Сохраняю фото в архиве и "
                        "перевожу текст на английский.")

@router.message(Command("help"))
async def start_command(message: Message):
    await message.reply("Сохраню Ваше фото в архиве (голосовое подтверждение) "
                        "и переведу текст с русского на английский.")

@router.message(lambda message: message.photo)
async def handle_photo(message: Message):
    try:
        # Получаем файл фото
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        # Скачиваем файл
        file_path = file_info.file_path
        file_name = f"img/{photo.file_id}.jpg"
        await bot.download_file(file_path, file_name)

        # Создаем голосовое сообщение
        tts = gTTS(text="Спасибо! Ваши данные получены! и сохранены!", lang='ru')
        audio_file = f"{file_name}.mp3"
        tts.save(audio_file)

        # Отправляем голосовое сообщение
        voice_message = FSInputFile(audio_file)
        await message.reply_voice(voice_message)

        # Удаляем временный аудиофайл
        os.remove(audio_file)

    except Exception as e:
        logging.error(f"Failed to process photo: {e}")
        await message.reply("There was an error saving your photo. Please try again.")

@router.message(F.text)
async def handle_text(message: Message):
    try:
        text_to_translate = message.text
        # Дождитесь завершения корутины и затем получите `text` из результата
        translation_result = await translator.translate(text_to_translate, src='auto', dest='en')
        translated_text = translation_result.text
        await message.answer(translated_text)
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.reply(f"Ошибка перевода: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

