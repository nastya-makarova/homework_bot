import json
import logging
import logging.handlers
import os
import sys
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (
    APIResponseKeyError,
    HomeworkNotFoundError,
    HomeworkResponseError,
    HomeworkStatusError,
    RequestExceptionError,
    ResponseFormatError,
    ResponseStatusError,
    TimestampError,
    TokenNotFoundError,
)

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
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    tokens = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )
    for name, value in tokens:
        if value is None:
            raise TokenNotFoundError(
                f'Отсутствует обязательная переменная окружения: '
                f'{name}'
            )


def send_message(bot, message):
    """Функция отправляет сообщение в чат, определяемый TELEGRAM_CHAT_ID."""
    try:
        logging.debug('Подготовка к отправке сообщения в Telegram.')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение в Telegram успешно отправлено.')
    except Exception as error:
        logging.error(f'Сообщение отправить не удалось. {error}')


def get_api_answer(timestamp):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
    if not isinstance(timestamp, int) or timestamp < 0:
        raise TimestampError('Введено некорректное значение метки времени.')

    payload = {'from_date': timestamp}

    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except requests.RequestException as error:
        raise RequestExceptionError(
            f'Ошибка при запросе к основному API: {error}'
        ) from error

    if homework_statuses.status_code != 200:
        raise ResponseStatusError(
            f'API возвращает код, отличный от 200.'
            f'Код ответа API: {homework_statuses.status_code}'
        )

    try:
        return homework_statuses.json()
    except json.JSONDecodeError as error:
        raise ResponseFormatError(
            f'Не удалось обработать ответ от сервера.{error}'
        ) from error


def check_response(response):
    """Функция проверяет ответ API на соответствие документации."""
    response_keys = ['homeworks', 'current_date']
    for key in response_keys:
        if key not in response:
            raise APIResponseKeyError(f'Ответ API не содержит %s, {key}')

    homeworks = response['homeworks']
    if not homeworks:
        raise HomeworkNotFoundError('Домашние работы не найдены.')
    elif not isinstance(homeworks, list):
        raise HomeworkResponseError(
            'В ответе API домашки под ключом `homeworks`'
            'данные приходят не в виде списка.'
        )
    elif not isinstance(response, dict):
        raise HomeworkResponseError(
            'В ответе API домашки данные приходят не в виде словаря.'
        )


def parse_status(homework):
    """Функция извлекает статус конкретной домашней работы."""
    if 'homework_name' not in homework:
        raise APIResponseKeyError('Ответ API не содержит ключ `homework_name`')
    homework_name = homework['homework_name']

    if 'status' not in homework:
        raise APIResponseKeyError('Ответ API не содержит ключ `status`')
    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        raise HomeworkStatusError('Неожиданный статус домашней работы.')

    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    previous_status = None
    current_error = None
    previous_error = None

    try:
        check_tokens()
    except TokenNotFoundError as error:
        logging.critical(error)
        return

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homework = response['homeworks'][0]
            current_status = homework['status']
            if current_status != previous_status:
                message = parse_status(homework)
                send_message(bot, message)
                previous_status = current_status
            else:
                logging.debug('Статус работы не изменился.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            current_error = str(error)

        if current_error != previous_error:
            try:
                send_message(bot, message)
            except Exception as error:
                logging.error(error)

            previous_error = current_error

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s - %(asctime)s - %(message)s',
        level=logging.DEBUG,
        stream=sys.stdout
    )
    main()
