import logging
import os

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class TelegramHandler(logging.Handler):
    """Отправляет сообщения в телеграм, когда происходит ошибка."""

    def __init__(self, bot, telegram_chat_id, last_log_message=None):
        """Инициализирует обработчик для отправки сообщений в Telegram."""
        super().__init__()
        self.bot = bot
        self.telegram_chat_id = telegram_chat_id
        self.last_log_message = last_log_message

    def emit(self, record):
        """
        Метод отправляет сообщение в Telegram.
        Сообщение будет отправлено, если уровень логирования является ERROR
        и сообщение не совпадает с последним отправленным.
        """
        if record.levelname in ('ERROR', 'CRITICAL'):
            log_message = self.format(record)
            if log_message != self.last_log_message:
                logging.debug('Запуск отправки сообщения в Telegram')
                self.send_message(bot, log_message)
                self.last_log_message = log_message

    def send_message(self, bot, message):
        """Метод отправляет сообщение в Telegram с помощью указанного бота."""
        if not self.telegram_chat_id:
            logging.error(
                'Отсутствует обязательная переменная окружения:'
                'telegram chat_id '
            )
            return
        try:
            logging.info('Попытка отправить сообщение в Telegram')
            response = bot.send_message(chat_id=self.telegram_chat_id, text=message)
            logging.info(f'Сообщение отправлено в Telegram, статус: {response.status_code}')
        except Exception as error:
            logging.error(error, 'Невозможно отправить сообщение об ошибке.')
