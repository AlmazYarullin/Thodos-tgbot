class to_do():

	def __init__(self):
		self.title = ''
		self.text = ''
		self.active = True
		self.deleted = False
		self.out = ''


	def build_task_out(self):
		if self.text:
			self.out = '<b>' + self.title + '\n—</b>' + self.text
		else:
			self.out = self.out = '<b>' + self.title + '</b>'

class user():

	def __init__(self, u_id):
		self.user_id = u_id
		self.tasks = []
		self.bot_status = 'waiting'

class task_callback():

	def __init__(self, status, t_idx, u_idx):
		self.status = status
		self.index = t_idx

