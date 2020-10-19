import telebot
import config
from task import To_do
from data_handler import Data
from task import User
from telebot import types
from button import Button


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


@bot.message_handler(commands=['start', 'help', 'delete_account'])
def send_welcome(message):
    if message.text == '/start':
        if not Data().is_registered(message.from_user.id):
            Data().register_user(message.from_user.id, message.from_user.username)
            bot.send_message(message.chat.id, config.HELLO_MESSAGE, reply_markup=show_main_keyboard(0))
    if message.text == '/delete_account':
        # Удаление аккаунта
        Data().delete_user(message.from_user.id)
        bot.send_message(message.chat.id, "Пока 😥", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def mes(message):
    # if message.from_user.id != 587925968:
    #     bot.send_message(message.from_user.id, "🏗Ведутся технические работы👷")
    #     return
    # Проверка регистрации пользователя
    if not Data().is_registered(message.from_user.id):
        bot.send_message(message.from_user.id, "🚫Для начала, зарегистрируйся🚫\nНапиши /start")
        return
    # Получение сведений о пользователе из БД
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
    # Обработка с параметром
    elif len(user.bot_status.split('_<>_')) > 4:
        task = To_do()
        button = Button(button_type='parameter')
        button.convert_to_button(user.bot_status)
        if button.parameter.values[button.parameter.now] == 'add':
            task = Data().get_task(user.id, int(button.task_id))
            task.text += '\n' + message.text
            task.build_task_out()
        elif button.parameter.values[button.parameter.now] == 'rewrite':
            task.id = button.task_id
            task.create_task(message.text)
        Data().update_task(user.id, task)
        bot.send_message(message.chat.id, 'Изменено', reply_markup=show_main_keyboard(0))
        Data().bot_status(user.id, 'waiting')
    # Инструкция по созданию туду
    elif message.text == 'Новый туду':
        Data().bot_status(user.id, 'creating_to_do')
        bot.send_message(message.chat.id, "В первой строке напиши название задачи, "
                                          "после - описание\n"
                                          "Например:", reply_markup=types.ReplyKeyboardRemove())
        button = Button('creating_to_do', action='cancel')
        markup = types.InlineKeyboardMarkup(row_width=2)
        item = types.InlineKeyboardButton('Отменить', callback_data=button.convert_to_string())
        markup.add(item)
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
                    button = Button('showing_tasks', action='done', task_id=task.id)
                    item1 = types.InlineKeyboardButton("✅ Сделано",
                                                       callback_data=button.convert_to_string())
                    button.action = 'delete'
                    item2 = types.InlineKeyboardButton("❌ Удалить",
                                                       callback_data=button.convert_to_string())
                    button.action = 'edit'
                    item3 = types.InlineKeyboardButton("✏ Изменить",
                                                       callback_data=button.convert_to_string())
                    markup.add(item1, item2, item3)

                    bot.send_message(message.chat.id, task.out, reply_markup=markup, parse_mode='html')
                else:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    button = Button('showing_tasks', action='backup', task_id=task.id)
                    item1 = types.InlineKeyboardButton("🔙 Вернуть", callback_data=button.convert_to_string())
                    button.action = "delete"
                    item2 = types.InlineKeyboardButton("❌ Удалить", callback_data=button.convert_to_string())
                    markup.add(item1, item2)
                    bot.send_message(message.chat.id, "🟢 " + task.title, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            button = Button(button_type=call.data.split('_<>_')[3])
            button.convert_to_button(call.data)
            if button.type == 'simple':
                if button.status == 'showing_tasks':
                    task = Data().get_task(call.from_user.id, button.task_id)
                    if not task:
                        return
                    # Активация кнопки "Сделано"
                    if button.action == 'done':
                        Data().change_task_activity(call.from_user.id, task.id, False)
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        button.action = 'backup'
                        item1 = types.InlineKeyboardButton("🔙 Вернуть", callback_data=button.convert_to_string())
                        button.action = 'delete'
                        item2 = types.InlineKeyboardButton("❌ Удалить",
                                                           callback_data=button.convert_to_string())
                        markup.add(item1, item2)
                        bot.edit_message_text(chat_id=call.message.chat.id,
                                              message_id=call.message.message_id, reply_markup=markup,
                                              text="🟢 " + task.title, parse_mode='html')
                    # Активация кнопки "Удалить"
                    elif button.action == 'delete':
                        Data().delete_task(call.from_user.id, task.id)
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    # Активация кнопки "Изменить"
                    elif button.action == 'edit':
                        button.status = 'editing_to_do'
                        button.type = 'parameter'
                        button.parameter.values = ['rewrite', 'add']
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        item = types.InlineKeyboardButton("Параметр: Перезаписать",
                                                          callback_data=button.convert_to_string())
                        markup.add(item)
                        bot.send_message(call.message.chat.id,
                                         "👇 Твое туду",
                                         reply_markup=types.ReplyKeyboardRemove())
                        bot.send_message(call.message.chat.id,
                                         task.title + task.text, reply_markup=markup)
                        Data().bot_status(call.from_user.id, button.convert_to_string())
                    # Возвращение туду в активные
                    elif button.action == "backup":
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        button.action = 'done'
                        item1 = types.InlineKeyboardButton("✅ Сделано", callback_data=button.convert_to_string())
                        button.action = 'delete'
                        item2 = types.InlineKeyboardButton("❌ Удалить", callback_data=button.convert_to_string())
                        button.action = 'edit'
                        item3 = types.InlineKeyboardButton("✏ Изменить", callback_data=button.convert_to_string())
                        markup.add(item1, item2, item3)
                        Data().change_task_activity(call.from_user.id, button.task_id, True)
                        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.message_id,
                                                      reply_markup=markup)
                # Кнопка связана с отменой создания туду
                elif button.status == 'creating_to_do':
                    if button.action == 'cancel' and Data().bot_status(call.from_user.id) == 'creating_to_do':
                        Data().bot_status(call.from_user.id, 'waiting')
                        bot.send_message(call.message.chat.id, "Отменено",
                                         parse_mode='html', reply_markup=show_main_keyboard(0))

            elif button.type == 'parameter' and Data().bot_status(call.from_user.id).find('editing_to_do') != -1:
                # Кнопка связана с изменением туду
                if button.status == 'editing_to_do':
                    button.parameter.next_step()
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                  reply_markup=button.build_parameter_button())
                    Data().bot_status(call.from_user.id, button.convert_to_string())
    except Exception as e:
        print(repr(e))


bot.polling()
