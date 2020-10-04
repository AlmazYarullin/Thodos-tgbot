import telebot
import config
from data import to_do
from data import user
from data import task_callback
from telebot import types

def register_user(telegram_user_id):
	'''Регистрация пользователя'''
	global users
	users.update({telegram_user_id: user(telegram_user_id)})

def erase_deleted_tasks():
	for key in users:
		if users[key]:
			temp_tasks = []
			for task in users[key].tasks:
				if not task.deleted:
					temp_tasks.append(task)
			users[key].tasks = temp_tasks

def main_keyboard(items):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	item1 = types.KeyboardButton("Новый туду")
	item2 = types.KeyboardButton("Мои туду")
	markup.add(item1, item2)
	if items:
		for item in items:
			item = types.KeyboardButton(item)
	return markup

def new_task(message):
	task = to_do()
	writing_title = True
	for char in message:
		if char == '\n':
			writing_title = False
		if writing_title:
			task.title += char
		else:
			task.text += char
	task.build_task_out()
	return task

global users
users = {}

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start', 'help'])

def send_welcome(message):
	"""Приветствие"""
	global user_to_index
	global tasks_from_index
	register_user(message.from_user.id)
	bot.send_message(message.chat.id, "Привет, я Тодос - бот и твой личный ассистент!\n"
		"Я помогу тебе не выбиться из графика и "
		"не забыть про твои дела.", reply_markup=main_keyboard(0))

@bot.message_handler(content_types=['text'])

def mes(message):
	global users
	#Очистка удаленных туду
	erase_deleted_tasks()
	#Проверка регистрации пользователя
	if not message.from_user.id in users:
		bot.send_message(message.chat.id, '🚫Для начала, зарегистрируйся🚫\nНапиши /start')

	# Процесс создания туду
	elif users[message.from_user.id].bot_status == 'creating_to_do':
		users[message.from_user.id].tasks.append(new_task(message.text))
		users[message.from_user.id].bot_status = 'waiting'
		bot.send_message(message.chat.id, 'Туду успешно создано', reply_markup=main_keyboard(0))
	# Изменение туду
	elif users[message.from_user.id].bot_status.find('editing_to_do') != -1:
		temp = users[message.from_user.id].bot_status.split('_<>_')
		users[message.from_user.id].tasks[int(temp[1])] = new_task(message.text)
		bot.send_message(message.chat.id, 'Изменено')
		users[message.from_user.id].bot_status = 'waiting'
	# Инструкция по созданию туду
	elif message.text == 'Новый туду':
		users[message.from_user.id].bot_status = 'creating_to_do'
		markup = types.InlineKeyboardMarkup(row_width=2)
		item1 = types.InlineKeyboardButton("Отменить", callback_data='creating_to_do_<>_cancel')
		markup.add(item1)
		bot.send_message(message.chat.id, "В первой строке напиши название задачи, "
			"после - описание\n"
			"Например:\nСписок покупок\n"
			"молоко, хлеб, бананы", reply_markup=markup)
	# Вывод существующих туду
	elif message.text == 'Мои туду':
		if not users[message.from_user.id].tasks:
			bot.send_message(message.chat.id, 'У тебя нет ни одного туду', reply_markup=main_keyboard(0))
		else:
			bot.send_message(message.chat.id, 'Твои туду:', reply_markup=main_keyboard(0))
			for index, task in enumerate(users[message.from_user.id].tasks):

				if task.active:
					markup = types.InlineKeyboardMarkup(row_width=2)
					item1 = types.InlineKeyboardButton("✅ Сделано", callback_data='task_<>_done_<>_' + str(index) + '_<>_' + str(message.from_user.id))
					item2 = types.InlineKeyboardButton("❌ Удалить", callback_data='task_<>_delete_<>_' + str(index) + '_<>_' + str(message.from_user.id))
					item3 = types.InlineKeyboardButton("✏️ Изменить", callback_data='task_<>_edit_<>_' + str(index) + '_<>_' + str(message.from_user.id))

					markup.add(item1, item2, item3)

					bot.send_message(message.chat.id, task.out, reply_markup=markup, parse_mode='html')
				else:
					markup = types.InlineKeyboardMarkup(row_width=2)
					item1 = types.InlineKeyboardButton("❌ Удалить", callback_data=('task_<>_delete_<>_' + str(index) + '_<>_' + str(message.from_user.id)))

					markup.add(item1)
					bot.send_message(message.chat.id, "🟢 " + task.title, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)

def callback_inline(call):
	try:
		if call.message:
			global users
			call_info = call.data.split('_<>_')
			# Кнопка связана с выведенными туду
			if call_info[0] == 'task':
				task = task_callback(call_info[1], int(call_info[2]), int(call_info[3]))
				# Активация кнопки "Сделано"
				if task.status == 'done':
					users[call.from_user.id].tasks[task.index].active = False

					markup = types.InlineKeyboardMarkup(row_width=2)
					item1 = types.InlineKeyboardButton("Удалить", callback_data='task_<>_delete_<>_' + str(task.index) + '_<>_' + str(call.from_user.id))

					markup.add(item1)
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, text="✅ " + users[call.from_user.id].tasks[task.index].title, parse_mode='html')
				# Активация кнопки "Удалить"
				if task.status == 'delete':
					users[call.from_user.id].tasks[task.index].deleted = True
					bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
				# Активация кнопки "Изменить"
				if task.status == 'edit':
					bot.send_message(call.message.chat.id, "👇 Скопируй туду, отредактируй и отправь")
					bot.send_message(call.message.chat.id, users[call.from_user.id].tasks[task.index].title + users[call.from_user.id].tasks[task.index].text)
					users[call.from_user.id].bot_status = 'editing_to_do_<>_' + str(task.index)
			# Кнопка связана с отменой создания туду
			if call_info[0] == 'creating_to_do':
				if call_info[1] == 'cancel':
					users[call.from_user.id].bot_status = 'waiting'
					bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
					bot.send_message(call.message.chat.id, "Отменено", parse_mode='html', reply_markup=main_keyboard(0))
	except Exception as e:
		print(repr(e))

bot.polling()