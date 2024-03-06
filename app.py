import telebot
from config import TOKEN, currencies, quote_plural_dict
from extensions import APIException, Plural, CurrencyConverter

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = 'Для начала работы введите команду боту в следующем формате:\n<имя валюты> \
<в какую валюту перевести>  \
<количество переводимой валюты>\nУвидеть список всех доступных валют: /values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты: '
    for key in currencies.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        input_values = message.text.split(' ')

        if len(input_values) != 3:
            raise APIException('Слишком много параметров.')

        base, quote, amount = input_values
        result = CurrencyConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Стоимость {amount} {Plural.base_plural(amount, base)} в {quote_plural_dict[quote]} \
составляет {round(result, 2)}'
        bot.send_message(message.chat.id, text)


bot.polling()
