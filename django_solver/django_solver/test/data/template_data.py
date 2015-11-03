
VALID_TEMPLATE_BODY_JINJA = "My name is {{username}}. I am {{age}} y.o."

INVALID_TEMPLATE_BODY_JINJA = "My name is {1username}}. I am {{1age}} y.o."

VALID_TEMPLATE_FILENAME_JINJA = "valid_jinja_template.temp"


#---------------------- For PythonCodeModel testing ---------------------
VALID_PYTHON_CODE = '''
OUTPUTS = dict()
x = 1
y = 2
z = x + y
OUTPUTS['result'] = z
'''
INVALID_PYTHON_CODE = '''
x = 1
y = 1
z = 1x - {y
'''




VALID_PYTHON_CODE_FILENAME = 'valid_code.py'

INVALID_PYTHON_CODE_FILENAME = 'invalid_code.py'



#---------------------- For TaskModel testing ---------------------------
VALID_DEFAULT_DICT = '''
{'username':'dmitry', 'age': 30}
'''

INVALID_DEFAULT_DICT = '''
{'username';'dmitry', 'age': 30}
'''