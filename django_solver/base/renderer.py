
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django import forms
from django.conf import settings

# 
# simple_template = get_template('djsolver_simple_task.html') 
# full_tempalte = get_template('djsolver_task.html')


class TaskRenderer:

	def __init__(self, task, user=None, request=None):
		self.task = task

	def _get_template(self):
		if self.task.formulation_template.file:
			try:
				self.task.formulation_template.file.seek(0)
				template = self.task.formulation_template.file.read()
				template = template.decode('utf-8')
			except IOError:
				# TODO: May be additional try to load from body is needed...
				template = ''
		elif self.task.formulation_template.body:
			template = self.task.formulation_template.body
		else:
			template = ''
		return template

	def render_simple(self):
		'''Render the task instance with default values. No ability to input new values.
		'''
		# Don't try to render non-public problems
		if not self.task.public:
			return
		template = self._get_template()
		temp = Template(template)
		cont = Context(self.task.get_defaults)
		return temp.render(cont)

	def render_with_inputs(self):
		if not self.task.public:
			return
		template = self._get_template()
		if template and self.task.defaults:
			cur_fields = self.task.get_defaults
			render_fields = cur_fields.copy()
			for item in cur_fields.keys():
				 field_widget = forms.TextInput(attrs={'id': '%s_%s'%(settings.DJSOLVER_TEXTINPUT_PREFIX, item)})
				 render_fields[item] = field_widget.render(item, cur_fields[item])
			cont = Context(render_fields)
		else:
			cont = Context()
		temp = Template(template)
		return temp.render(cont)

