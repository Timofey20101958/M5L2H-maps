import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: /remember_city - позаоляет сохранить город на карту, /show_city - покажет все добавленные города, /show_my_cities - показывает все добавленные города ")
    # Допиши команды бота


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    # Реализуй отрисовку города по запросу
    manager.create_grapf(city_name + ".png", [city_name])
    with open(city_name+".png", "rb") as photo:
        bot.send_photo(message.send.id, photo)

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)

    if not cities:
        bot.send_message(user_id, "У вас пока нет сохранённых городов.")
        return

    # Отправляем список городов
    cities_list = "\n".join(f"• {city}" for city in cities)
    bot.send_message(user_id, f"Ваши сохранённые города:\n{cities_list}")

    # Отправляем карту с городами
    filename = f"my_cities_{user_id}.png"
    try:
        manager.create_graph(filename, cities)
        with open(filename, "rb") as photo:
            bot.send_photo(user_id, photo, caption="Карта ваших городов")
    except Exception as e:
        bot.send_message(user_id, f"Не удалось создать карту: {str(e)}")
    

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
