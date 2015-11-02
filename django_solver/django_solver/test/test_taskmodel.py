from django.test import TestCase

from ..models import TaskModel

class TaskModelTestCase(TestCase):
    def setUp(self):
        TaskModel.objects.create(formulation_template="My name is {{username}}. I am {{age}} y.o.", 
                                 solution_template="Answer:{{myname}}x{{myage}}",
                                 code="""OUTPUTS['myname']=INPUTS['username']
OUTPUTS['myage']=INPUTS['age']""",
                                 code_preamble="import ast",                              
                                 code_postamble="print('')",
                                 default_vals="{'username':'dmitry', 'age': 30}",
                                 )
    
    def test_model_creation(self):
        """Just creation of TaskModel instance"""
        task = TaskModel.objects.get(code_postamble="print('')")
        self.assertEqual(task.code_preamble, 'import ast')
