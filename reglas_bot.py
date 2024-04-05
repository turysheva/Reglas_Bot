from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from dotenv import load_dotenv
import openai
import os
import requests
import aiohttp
import json


# подгружаем переменные окружения
load_dotenv()

# передаем секретные данные в переменные
TOKEN = os.environ.get("TG_TOKEN")
GPT_SECRET_KEY = os.environ.get("GPT_SECRET_KEY")

# передаем секретный токен chatgpt
openai.api_key = GPT_SECRET_KEY


# функция для синхронного общения с chatgpt
async def get_answer(text):
    payload = {"text":text}
    response = requests.post("http://127.0.0.1:5000/api/get_answer", json=payload)
    return response.json()


# функция-обработчик команды /start 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # при первом запуске бота добавляем этого пользователя в словарь
    if update.message.from_user.id not in context.bot_data.keys():
        context.bot_data[update.message.from_user.id] = 5
    
    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text('Pregunte sobre las normas de construcción en Casa Linda o Domconst')


# функция-обработчик команды /data 
async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # создаем json и сохраняем в него словарь context.bot_data
    with open('data.json', 'w') as fp:
        json.dump(context.bot_data, fp)
    
    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text('Данные сгружены')

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as session:
        # Подготовка данных для отправки
        payload = {"text": update.message.text}
        # Отправка запроса на ваш API-сервер
        async with session.post("http://127.0.0.1:5000/api/get_answer", json=payload) as response:
            # Обработка ответа от сервера
            if response.status == 200:
                data = await response.json()
                await context.bot.send_message(chat_id=update.effective_chat.id, text=data['message'])
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Lo sentimos, no pudimos obtener una respuesta.")


def main():

    # создаем приложение и передаем в него токен бота
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # создаем job_queue 
    job_queue = application.job_queue
   

    # добавление обработчиков
    application.add_handler(CommandHandler("start", start, block=True))
    application.add_handler(CommandHandler("data", data, block=True))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    # запуск бота (нажать Ctrl+C для остановки)
    application.run_polling()
    print('Бот остановлен')


if __name__ == "__main__":
    main()