import logging
import logging.handlers
import os
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (
    APIResponseError,
    StatusError,
    TimestampError,
    TokenNotFoundError,
)
from handlers import TelegramHandler


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(levelname)s - %(asctime)s - %(message)s'
)

stream_handler = logging.StreamHandler()
telegram_handler = TelegramHandler(
    telegram_token=TELEGRAM_TOKEN,
    telegram_chat_id=TELEGRAM_CHAT_ID
)
stream_handler.setFormatter(formatter)
telegram_handler.setFormatter(formatter)

logger.addHandler(telegram_handler)
logger.addHandler(stream_handler)


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    tokens = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
              'TELEGRAM_TOKEN': TELEGRAM_TOKEN}
    for name, value in tokens.items():
        if value is None or value == '':
            logger.critical(
                'Отсутствует обязательная переменная окружения: %s', name
            )
            raise TokenNotFoundError
        else:
            return True


def send_message(bot, message):
    """Функция отправляет сообщение в чат, определяемый TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение успешно отправлено')
    except Exception as error:
        logger.error(error, 'Сообщение отправить не удалось.')


def get_api_answer(timestamp):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
    if not isinstance(timestamp, int) or timestamp < 0:
        logger.error('Введено некорректное значение метки времени.')
        raise TimestampError

    if check_tokens():
        payload = {'from_date': timestamp}
        try:
            homework_statuses = requests.get(
                ENDPOINT,
                headers=HEADERS,
                params=payload
            )
            if homework_statuses.status_code != 200:
                logger.error('API возвращает код, отличный от 200')

        except Exception as error:
            logger.error(error, 'Ошибка при запросе к основному API.')
            print(f'Ошибка при запросе к основному API: {error}')
        else:
            return homework_statuses.json()


def check_response(response):
    """Функция проверяет ответ API на соответствие документации."""
    if 'homeworks' not in response and 'current_date' not in response:
        logger.error('Ответ API не соответвует документации.')
        raise APIResponseError
    elif response.get('homeworks') == []:
        logger.debug('Домашние работы не найдены.')
        return False
    else:
        return True


def parse_status(homework):
    """Функция извлекает статус конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        logger.error('Неожиданный статус домашней работы.')
        raise StatusError
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    #timestamp = int(time.time())
    timestamp = -2000

    logging.basicConfig(
        format='%(levelname)s - %(asctime)s - %(message)s',
        level=logging.DEBUG
    )

    statuses = {}

    while True:
        try:
            response = get_api_answer(timestamp)
            if check_response(response):
                homework = response.get('homeworks')[0]
                homework_id = homework.get('id')
                if homework_id not in statuses:
                    statuses[homework_id] = homework.get('status')
                old_status = statuses.get(homework_id)
                if old_status != homework.get('status'):
                    statuses[homework_id] = homework.get('status')
                    message = parse_status(homework)
                    send_message(bot, message)
                else:
                    logging.debug('Статус работы не изменился.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
