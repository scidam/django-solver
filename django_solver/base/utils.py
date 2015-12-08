try:
    from solver.base import Solver, Task
except ImportError:
    pass
import ast
import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from .models import RegularTask, TemplateModel, PythonCodeModel






@transaction.atomic
def regtask_from_solver(task_solver, store_template_to_file=False, store_code_to_file=False):
    '''
    creates and returns a task model instance from a task solver instance.
    
    If save is True, it saves the RegularTask instance to database. 
    '''

    if not isinstance(task_solver, Solver):
        raise TypeError("task should be an instance of the Task class") 
    
    if store_template_to_file:
        tm_formulation, tm_solution = TemplateModel(), TemplateModel()
        tm_formulation.file.save(settings.DJSOLVER_TEMPLATE_FILENAME, ContentFile(task_solver.task.code))
        tm_solution.file.save(settings.DJSOLVER_TEMPLATE_FILENAME, ContentFile(task_solver.task.code))
    else:
        tm_formulation = TemplateModel(body=task_solver.task.content)
        tm_solution = TemplateModel(body=task_solver.task.solution_template)
    
    if store_code_to_file:
        # File creation is needed ... 
        pcm_code, pcm_preamble, pcm_postamble  = PythonCodeModel(),\
            PythonCodeModel(), PythonCodeModel()
        pcm_code.file.save(settings.DJSOLVER_CODE_FILENAME, ContentFile(task_solver.task.code))
        pcm_preamble.file.save(settings.DJSOLVER_CODE_FILENAME, ContentFile(task_solver.task.code))
        pcm_postamble.file.save(settings.DJSOLVER_CODE_FILENAME, ContentFile(task_solver.task.code))
    else:
        pcm_code = PythonCodeModel(body=task_solver.task.code)
        pcm_preamble = PythonCodeModel(body=task_solver.preamble)
        pcm_postamble = PythonCodeModel(body=task_solver.postamble)
    pcm_code.save()
    pcm_preamble.save()
    pcm_postamble.save()
    tm_formulation.save()
    tm_solution.save()
    rt = RegularTask(formulation_template=tm_formulation,
                     solution_template=tm_solution,
                     code=pcm_code,
                     code_preamble=pcm_preamble,
                     code_postamble=pcm_postamble,
                     defaults=task_solver.task.default_vals
                     )
    return rt


def solver_from_regtask(regtask, silent=True):
    if not isinstance(regtask, RegularTask):
        raise TypeError("task should be an instance of the RegularTask class") 

    # try to create a solvertask from body based inputs
    
    if regtask.formulation_template:
        if regtask.formulation_template.file and not regtask.formulation_template.body:
            task_content = regtask.formulation_template.file.read().decode('utf-8')
        else:
            task_content = regtask.formulation_template.body
    else:
        task_content = ''

    if regtask.defaults:
        if silent:
            try:
                task_defvals = ast.literal_eval(regtask.defaults)
            except:
                task_defvals = None
        else:
            task_defvals = ast.literal_eval(regtask.defaults)
    else:
        task_defvals = None

    if regtask.code:
        if regtask.code.file and not regtask.code.body:
            task_code = regtask.code.file.read().decode('utf-8')
        else:
            task_code = regtask.code.body
    else:
        task_code = ''

    if regtask.solution_template:
        if regtask.solution_template.file and not regtask.solution_template.body:
            task_soltempl = regtask.solution_template.file.read().decode('utf-8')
        else:
            task_soltempl = regtask.solution_template.body
    else:
        task_soltempl = None

    if regtask.code_preamble:
        if regtask.code_preamble.file and not regtask.code_preamble.body:
            solver_preamble = regtask.code_preamble.file.read().decode('utf-8')
        else:
            solver_preamble = regtask.code_preamble.body
    else:
        solver_preamble = ''

    if regtask.code_postamble:
        if regtask.code_postamble.file and not regtask.code_postamble.body:
            solver_postamble = regtask.code_postamble.file.read().decode('utf-8')
        else:
            solver_postamble = regtask.code_postamble.body
    else:
        solver_postamble = ''

    atask = Task(task_content, solution_template=task_soltempl,
                 default_vals=task_defvals,
                 code=task_code
                 )
    asolver = Solver(atask,
                     preamble=solver_preamble,
                     postamble=solver_postamble
                     )
    return atask, asolver




# ---------- Input data validation and conversion -------------------

float_value_pat = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')

integer_value_pat = re.compile(r'[+-]?\d+')

allowed_input_types = ['float', 'integer', 'string']


def validate(input_data, input_type):
    pass


def  _strictly_validate_numericals(input_data, dtype):

    if dtype == 'integer':
        cpat = integer_value_pat
    elif dtype == 'float':
        cpat = float_value_pat
    else:
        return False
    
    def _single_integer_check(single):
        # empty input data not allowed in strictly validation
        if len(single) == 0:
            return False
        if cpat.match(single):
            return True
        else:
            return False
    
    def _integer_row_validation(row):
        datalist = row.split(settings.DJSOLVER_DATA_DELIMITER)
        return True if all(map(_single_integer_check, datalist)) else False
    
    if input_data.count(settings.DJSOLVER_DATA_DELIMITER) == 0\
        and input_data.count(settings.DJSOLVER_DATA_ROW_DELIMITER) == 0:
        return _single_integer_check(input_data)

    # 1D array checking ... It is just a row
    elif input_data.count(settings.DJSOLVER_DATA_DELIMITER) > 0\
        and input_data.count(settings.DJSOLVER_DATA_ROW_DELIMITER) == 0:
        return _integer_row_validation(input_data)

    # 2d array checking ... It is just few rows
    elif input_data.count(settings.DJSOLVER_DATA_DELIMITER) > 0\
        and input_data.count(settings.DJSOLVER_DATA_ROW_DELIMITER) > 0:
        rows = input_data.split(settings.DJSOLVER_DATA_ROW_DELIMITER)
        return True if all(map(_integer_row_validation, rows)) else False
    else:
        return False



def strict_validate(input_data, input_type):
    if input_type == 'string':
        return True if input_data else False
    elif input_type == 'float':
        return _strictly_validate_integers(input_data, 'float')
    elif input_type == 'integer':
        return _strictly_validate_integers(input_data, 'integer')
    else:
        return False
    

def smart_validate(input_data, input_type):
    pass

def convert(input_data):
    ''' Performs smart data conversion procedure. '''
    
    pass
# -------------------------------------------------------------------

def get_data_form_request(request):
    # request should be ajax only
    if not request.is_ajax():
        return None

    taskid = request.POST.get('task-id', None)
    input_data_str = request.POST.get('input-data', None)
    
    
    
    