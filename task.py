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


class User:

    def __init__(self, u_id):
        self.id = u_id
        self.bot_status = 'waiting'
