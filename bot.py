import telebot
import config
from task import To_do
from data_handler import Data
from task import User
from telebot import types


def show_main_keyboard(items):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Новый туду")
    item2 = types.KeyboardButton("Мои туду")
    markup.add(item1, item2)
    if items:
        for item in items:
            item = types.KeyboardButton(item)
            markup.add(item)
    return markup


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветствие"""
    if message.text == '/start':
        Data().register_user(message.from_user.id, message.from_user.username)
        bot.send_message(message.chat.id,
                         "Привет, я Тодос - бот и твой личный ассистент!\n"
                         "Я помогу тебе не выбиться из графика и "
                         "не забыть про твои дела.", reply_markup=show_main_keyboard(0))


@bot.message_handler(content_types=['text'])
def mes(message):
    if not Data().is_registered(message.from_user.id):
        bot.send_message(message.from_user.id, "🚫Для начала, зарегистрируйся🚫\nНапиши /start")
        return
    user = User(message.from_user.id)
    user.bot_status = str(Data().bot_status(user.id))
    # Процесс создания туду
    if user.bot_status == 'creating_to_do':
        task = To_do()
        task.create_task(message.text)
        Data().create_task(user.id, task)
        Data().bot_status(user.id, 'waiting')
        bot.send_message(user.id, 'Туду успешно создано',
                         reply_markup=show_main_keyboard(0))
    # Изменение туду
    elif user.bot_status.find('editing_to_do') != -1:
        task = To_do()
        if Data().bot_status(user.id).split('_<>_')[1] == 'add':
            task = Data().get_task(user.id, int(Data().bot_status(user.id).split('_<>_')[2]))
            task.text += '\n' + message.text
            task.build_task_out()
        else:
            task.id = Data().bot_status(user.id).split('_<>_')[1]
            task.create_task(message.text)
        Data().update_task(user.id, task)
        bot.send_message(message.chat.id, 'Изменено', reply_markup=show_main_keyboard(0))
        Data().bot_status(user.id, 'waiting')
    # Инструкция по созданию туду
    elif message.text == 'Новый туду':
        Data().bot_status(user.id, 'creating_to_do')
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Отменить",
                                           callback_data='creating_to_do_<>_cancel')
        markup.add(item1)
        bot.send_message(message.chat.id, "В первой строке напиши название задачи, "
                                          "после - описание\n"
                                          "Например:", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Список покупок\n"
                                          "молоко, хлеб, бананы", reply_markup=markup)
    # Вывод существующих туду
    elif message.text == 'Мои туду':
        if not Data().tasks_exist(user.id):
            bot.send_message(message.chat.id, 'У тебя нет ни одного туду', reply_markup=show_main_keyboard(0))
        else:
            bot.send_message(message.chat.id, 'Твои туду:', reply_markup=show_main_keyboard(0))
            for index in range(Data().get_index_of_the_last_task(user.id) + 1):
                task = Data().get_task(user.id, index)
                if not task:
                    continue
                if task.active:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item1 = types.InlineKeyboardButton("✅ Сделано",
                                                       callback_data='task_<>_done_<>_' + str(index))
                    item2 = types.InlineKeyboardButton("❌ Удалить",
                                                       callback_data='task_<>_delete_<>_' + str(index))
                    item3 = types.InlineKeyboardButton("✏ Изменить",
                                                       callback_data='task_<>_edit_<>_' + str(index))
                    markup.add(item1, item2, item3)

                    bot.send_message(message.chat.id, task.out, reply_markup=markup, parse_mode='html')
                else:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item1 = types.InlineKeyboardButton("❌ Удалить",
                                                       callback_data=('task_<>_delete_<>_' + str(index)))
                    markup.add(item1)
                    bot.send_message(message.chat.id, "🟢 " + task.title, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            call_info = call.data.split('_<>_')
            # Кнопка связана с выведенными туду
            if call_info[0] == 'task':
                status = call_info[1]
                task = Data().get_task(call.from_user.id, int(call_info[2]))
                # Активация кнопки "Сделано"
                if status == 'done':
                    Data().task_done(call.from_user.id, task.id)
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item1 = types.InlineKeyboardButton("❌ Удалить",
                                                       callback_data='task_<>_delete_<>_' + str(
                                                           task.id) + '_<>_' + str(call.from_user.id))
                    markup.add(item1)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id, reply_markup=markup,
                                          text="✅ " + task.title, parse_mode='html')
                # Активация кнопки "Удалить"
                if status == 'delete':
                    Data().delete_task(call.from_user.id, task.id)
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                # Активация кнопки "Изменить"
                if status == 'edit':
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item = types.InlineKeyboardButton("Параметр: Переписать", callback_data='editing_to_do_<>_add_<>_' + str(task.id))
                    markup.add(item)
                    bot.send_message(call.message.chat.id,
                                     "👇 Скопируй туду, отредактируй и отправь", reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(call.message.chat.id,
                                     task.title + task.text, reply_markup=markup)
                    Data().bot_status(call.from_user.id, 'editing_to_do_<>_' + str(task.id))
            # Кнопка связана с отменой создания туду
            if call_info[0] == 'creating_to_do':
                if call_info[1] == 'cancel' and Data().bot_status(call.from_user.id) == 'creating_to_do':
                    Data().bot_status(call.from_user.id, 'waiting')
                    #                   message_id=call.message.message_id)
                    bot.send_message(call.message.chat.id, "Отменено",
                                     parse_mode='html', reply_markup=show_main_keyboard(0))
            # Кнопка связана с изменением туду
            if call_info[0] == 'editing_to_do':
                if call_info[1] == 'add':
                    Data().bot_status(call.from_user.id, 'editing_to_do_<>_add_<>_' + str(call_info[2]))
                    bot.edit_message_text()

    except Exception as e:
        bot.send_message(587925968, repr(e))


bot.polling()
