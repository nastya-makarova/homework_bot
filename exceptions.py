class TokenNotFoundError(Exception):
    """Исключение выбрасывается при недоступности переменных с токенами."""


class TimestampError(ValueError):
    """Исключение выбрасывается при некорректном значении метки времени."""


class HomeworkNotFoundError(Exception):
    """Исключение выбрасывается при пустом списке домашних работ."""


class HomeworkStatusError(Exception):
    """Исключение выбрасывается при неизвестном статусе работы."""


class HomeworkResponseError(TypeError):
    """
    Исключение выбрасывается при несоответсвии ответа API документации.
    В ответе API данные представлены не в виде словаря.
    Данные под ключом `homeworks` в ответе API представлены не в виде списка.
    """


class ResponseStatusError(Exception):
    """Исключение выбрасывается, если API возвращает код, отличный от 200."""


class APIResponseKeyError(TypeError):
    """
    Исключение выбрасывается при несоответсвии ответа API документации.
    Ответ API не содержит необходимые ключи.
    """


class RequestExceptionError(Exception):
    """Исключение выбрасывается при ошибке запроса."""


class ResponseFormatError(ValueError):
    """Исключение выбрасывается, если не удалось обработать ответ."""
