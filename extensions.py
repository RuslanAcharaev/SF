import requests
import json
from config import base_plural_dict, currencies, API_KEY


class APIException(Exception):  # Класс пользовательских исключений
    pass


class Plural:  # Класс склонения числительных
    @staticmethod
    def base_plural(amount, currency):
        quantity = str(int(float(amount)))

        if quantity[-2:] == '11':
            return base_plural_dict[f'{currency}1']
        elif quantity[-1] == '1':
            return base_plural_dict[f'{currency}2']
        else:
            return base_plural_dict[f'{currency}1']


class CurrencyConverter:  # Класс для перевода одной валюты в другую и условий вызова пользовательских исключений
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        if base == quote:
            raise APIException(f'Невозможно перевести одинаковыые валюты {base}.')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}.')

        if float(amount) < 0:
            raise APIException('Введено отрицательное количество конвертируемой валюты.')

        try:
            base_ticker = currencies[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}.')

        try:
            quote_ticker = currencies[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}.')

        r = requests.get(f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{base_ticker}/{quote_ticker}/{amount}')
        result = json.loads(r.content)['conversion_result']

        return result
