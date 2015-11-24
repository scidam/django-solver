
from django.template.loader import get_template, render_to_string

from django.template import Context, Template


# 
# simple_template = get_template('djsolver_simple_task.html') 
# full_tempalte = get_template('djsolver_task.html')


class TaskRenderer:

	def __init__(self, task, user=None, request=None):
		self.task = task

	def render_simple(self):
		'''Render the task instance with default values. No ability to input new values.
		'''
		# Don't try to render non-public problems
		if not self.task.public:
			return
		if self.task.formulation_template.file:
			try:
				template = self.task.formulation_template.file.read()
				template = template.decode('utf-8')
			except IOError:
				template = ''
		elif self.task.formulation_template.body:
			template = self.task.formulation_template.body
		else:
			template = ''
		temp = Template(template)
		cont = Context(self.task.get_defaults)
		return temp.render(cont)

	def render_with_inputs(self):
		
		
		