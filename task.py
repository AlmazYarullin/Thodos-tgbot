class To_do:

    def __init__(self):
        self.title = ''
        self.text = ''
        self.active = True
        self.deleted = False
        self.out = ''
        self.id = 0

    def build_task_out(self):
        """Создание выводимого туду"""
        if self.text:
            self.out = '<b>' + self.title + '\n—</b>' + self.text
        else:
            self.out = self.out = '<b>' + self.title + '</b>'

    def create_task(self, input_text):
        """Конвертация полученного текста в task"""
        writing_title = True
        for char in input_text:
            if char == '\n':
                writing_title = False
            if writing_title:
                self.title += char
            else:
                self.text += char
        self.build_task_out()


class Parameter:

    def __init__(self):
        self.now = 0
        self.values = []

    def convert_to_string(self):
        """Конвертация типа Parameter в тип string"""
        string = '_<>_' + str(self.now)
        for value in self.values:
            string += '_<>_' + str(value)
        return string

    def convert_to_parameter(self, lst):
        """Конвертация типа string в тип Parameter"""
        self.now = int(lst[0])
        self.values = lst[1::]

    def next_step(self):
        """Смена значения параметра"""
        if self.now + 1 == len(self.values):
            self.now = 0
        else:
            self.now += 1


class Button:

    def __init__(self, status='', b_type='simple', action='', task_id=-1):
        self.status = status
        self.action = action
        self.task_id = task_id
        self.type = b_type
        self.parameter = Parameter()

    def convert_to_string(self):
        """Конвертация данных в кнопке из Button в string"""
        string = self.status + '_<>_' + self.action + '_<>_' + str(self.task_id) + '_<>_' + self.type
        if self.type == 'parameter':
            string += self.parameter.convert_to_string()
        return string

    def convert_to_button(self, string):
        """Конвертация данных из string в Button"""
        lst = string.split('_<>_')
        self.status = lst[0]
        self.action = lst[1]
        self.task_id = int(lst[2])
        if self.type == 'parameter':
            self.parameter.convert_to_parameter(lst[4::])

    def build_parameter_button(self):
        """Создание кнопки с параметром"""
        from telebot import types
        markup = types.InlineKeyboardMarkup(row_width=2)
        item = types.InlineKeyboardButton('Параметр: ' + self.convert_for_out(), callback_data=self.convert_to_string())
        markup.add(item)
        return markup

    def convert_for_out(self):
        """Конвертация значений параметра"""
        value = self.parameter.values[self.parameter.now]
        if value == 'rewrite':
            return 'Перезаписать'
        elif value == 'add':
            return 'Добавить'


class User:

    def __init__(self, u_id):
        self.id = u_id
        self.bot_status = 'waiting'
