import telebot
from telebot import types
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from datetime import timedelta, date
from dbhelper import DBHelper

state_storage = StateMemoryStorage()
TOKEN="5801758101:AAGCNR592FzuhiUK_fTT9gYBOdM9InjIEgk"

bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

TS1 = "09:00AM-11:00AM"
TS2 = "11:00AM-01:00PM"
TS3 = "01:00PM-03:00PM"

SERVICE1 = "First Dose Registration"
SERVICE2 = "Second Dose Registration"
SERVICE3 = "Booster Dose Registration"

class MyStates(StatesGroup):
    name = State()
    location = State()
    service = State()
    confirmation = State()

@bot.message_handler(regexp="book|Book")
def start(message):
    bot.set_state(message.from_user.id, MyStates.name, message.chat.id)
    bot.send_message(message.chat.id, 'Greetings! Please enter your name 🙏')
    
@bot.message_handler(state="*", commands=['cancel'])
def cancel(message):
    bot.send_message(
        message.chat.id, "Your vaccination registration was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.name)
def get_name(message):
    inp = message.text
    bot.send_message(message.chat.id, 'Hello ' + inp + "! Please enter your location 🙏")
    bot.set_state(message.from_user.id, MyStates.location, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = inp

@bot.message_handler(state=MyStates.location)
def get_location_service_date(message):
    inp = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['location'] = inp
    button_service1 = types.InlineKeyboardButton(SERVICE1, callback_data=SERVICE1)
    button_service2 = types.InlineKeyboardButton(SERVICE2, callback_data=SERVICE2)
    button_service3 = types.InlineKeyboardButton(SERVICE3, callback_data=SERVICE3)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_service1)
    keyboard.add(button_service2)
    keyboard.add(button_service3)
    bot.send_message(message.chat.id, "Select the Service", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.data in [SERVICE1, SERVICE2, SERVICE3]:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['service'] = call.data
        
        date1 = date.today().strftime('%d-%m-%Y')
        date2 = (date.today() + timedelta(days=7)).strftime('%d-%m-%Y')
        date3 = (date.today() + timedelta(days=14)).strftime('%d-%m-%Y')

        button_date1 = types.InlineKeyboardButton(date1, callback_data=date1)
        button_date2 = types.InlineKeyboardButton(date2, callback_data=date2)
        button_date3 = types.InlineKeyboardButton(date3, callback_data=date3)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_date1)
        keyboard.add(button_date2)
        keyboard.add(button_date3)
        bot.send_message(call.message.chat.id, "Select the Date", reply_markup=keyboard)

    elif call.data not in [TS1, TS2, TS3]:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date'] = call.data

        button_ts1 = types.InlineKeyboardButton(TS1, callback_data=TS1)
        button_ts2 = types.InlineKeyboardButton(TS2, callback_data=TS2)
        button_ts3 = types.InlineKeyboardButton(TS3, callback_data=TS3)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_ts1)
        keyboard.add(button_ts2)
        keyboard.add(button_ts3)
        bot.send_message(call.message.chat.id, "Select the Time slot", reply_markup=keyboard)

    else:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['time'] = call.data
            msg = ("Your vaccination details:\n"
               f"Name: {data['name']}\n"
               f"Location: {data['location']}\n"
               f"Service: {data['service']}\n"
               f"Date: {data['date']}\n"
               f"Time slot: {data['time']}\n"
               f"Please confirm your details [Yes/No].")
            bot.send_message(call.message.chat.id, msg)
            bot.set_state(call.from_user.id, MyStates.confirmation, call.message.chat.id)

# result
@bot.message_handler(state=MyStates.confirmation)
def confirm_order(message):
    inp = message.text.lower()
    if inp == "yes":
        bot.send_message(message.chat.id, "Great. The vaccination registration is confirmed.")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            conn = DBHelper()
            conn.setup()
            conn.add_item(date.today().strftime('%d-%m-%Y'), data['name'], data['location'], data['service'], data['date'], data['time'])
        bot.delete_state(message.from_user.id, message.chat.id)
        return
    elif inp == "no":
        bot.send_message(message.chat.id, "Okay. Let's start again.")
        start(message)
        return
    bot.send_message(message.chat.id, 'Please enter "Yes" or "No".')

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
