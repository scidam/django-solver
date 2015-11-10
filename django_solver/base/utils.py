try:
    from solver import Task
except ImportError:
    pass
from .base.models import RegularTask    


def create_solver_task(task, taskmodel):
    '''
    creates a task model from task solver instance
    '''
    
    if not isinstance(taskmodel, RegularTask):
        raise TypeError, "taskmodel should be an instance of TaskModel class" 
    elif not isinstance(taskmodel, Task):
        raise TypeError, "task should be an instance of Task class" 
    
        

