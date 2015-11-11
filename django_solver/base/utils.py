try:
    from solver.base import Solver, Task
except ImportError:
    pass
from .models import RegularTask, TemplateModel, PythonCodeModel

from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings

@transaction.atomic
def create_regular_task(task_solver, store_template_to_file=False, store_code_to_file=False):
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