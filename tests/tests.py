from __future__ import print_function
import os
import shutil
import sys
import tempfile

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase, override_settings
import unittest
from django.test.client import Client

from django_solver.models import RegularTask, PythonCodeModel, TemplateModel
from django_solver.base.utils import regtask_from_solver, solver_from_regtask

from .data import template_data, solver_task_example

try:
    # tests that are using solver should be excluded
    from solver.base import Task, Solver
except ImportError:
    print('Error: solver module could not be imported. Some tests will be skipped.')
    



# from django.test.utils import override_settings
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

MROOT = os.path.abspath(getattr(settings, 'MEDIA_ROOT', ''))
NEWMROOT = tempfile.mkdtemp(dir=MROOT)


def _safely_create(model, filepath, filefield='file'):
    try:
        f = open(filepath, 'r')
        myfile = File(f)
        obj = model.objects.create(**{filefield: myfile})
    except IOError:
        return
    return obj

@override_settings(MEDIA_ROOT=NEWMROOT)
class TemplateModelTestCase(TestCase):

    def setUp(self):
        TemplateModel.objects.create(
                            body=template_data.VALID_TEMPLATE_BODY_JINJA,
                                     )
        _safely_create(TemplateModel, os.path.join(current_dir, 'tests', 'data',
                       template_data.VALID_TEMPLATE_FILENAME_JINJA)
                       )

    def tearDown(self):
        shutil.rmtree(NEWMROOT, ignore_errors=True)

    def test_body_creation(self):
        self.assertEqual(TemplateModel.objects.exclude(body__exact='')[0].body,
                         template_data.VALID_TEMPLATE_BODY_JINJA)

    def test_file_template_creation(self):
        self.assertIn(template_data.VALID_TEMPLATE_FILENAME_JINJA.split('.')[0],
                      TemplateModel.objects.get(body__exact='').file.name,
                      )

@override_settings(MEDIA_ROOT=NEWMROOT)
class PythonCodeTestCase(TestCase):
    def setUp(self):
        PythonCodeModel.objects.create(
                        body=template_data.VALID_PYTHON_CODE
                                       )

    def tearDown(self):
        shutil.rmtree(NEWMROOT, ignore_errors=True)

    def test_valid_python_code_body(self):
        self.assertEqual(PythonCodeModel.objects.all()[0].body,
                         template_data.VALID_PYTHON_CODE)

    def test_valid_python_code_file(self):
        _safely_create(PythonCodeModel, os.path.join(current_dir, 'tests', 'data',
                       template_data.VALID_PYTHON_CODE_FILENAME)
                       )
        self.assertIn(template_data.VALID_PYTHON_CODE_FILENAME.split('.')[0],
                      PythonCodeModel.objects.get(body__exact='').file.name,
                      )

    def test_invalid_python_code_body(self):
        raised_invalid_code = False
        try:
            obj = PythonCodeModel.objects.create(
                            body=template_data.INVALID_PYTHON_CODE
                                                 )
            obj.clean()
        except ValidationError:
            raised_invalid_code = True
        self.assertTrue(raised_invalid_code)

    def test_invalid_python_code_file(self):
        raised_invalid_code = False
        try:
            obj = _safely_create(
                PythonCodeModel,
                os.path.join(current_dir, 'tests', 'data',
                             template_data.INVALID_PYTHON_CODE_FILENAME
                             )
                                  )
            obj.clean()
        except ValidationError:
            raised_invalid_code = True
        self.assertTrue(raised_invalid_code)


class TaskModelTestCase(TestCase):
    def setUp(self):
        tempobj = TemplateModel.objects.create(body=template_data.VALID_TEMPLATE_BODY_JINJA)
        pyobj = PythonCodeModel.objects.create(body=template_data.VALID_PYTHON_CODE)
        RegularTask.objects.create(formulation_template=tempobj, 
                                 solution_template=tempobj,
                                 code=pyobj,
                                 code_preamble=pyobj,
                                 code_postamble=pyobj,
                                 defaults=template_data.VALID_DEFAULT_DICT
                                 )
        self.client = Client()
        

    def test_model_creation(self):
        """Just creation of TaskModel instance"""
        task = RegularTask.objects.all()[0]
        self.assertEqual(task.code_preamble.body,
                         template_data.VALID_PYTHON_CODE)

    def test_invalid_model_creation(self):
        raised_validation = False
        try:
            tempobj = TemplateModel.objects.create(body=template_data.VALID_TEMPLATE_BODY_JINJA)
            pyobj = PythonCodeModel.objects.create(body=template_data.VALID_PYTHON_CODE)
            obj = RegularTask.objects.create(formulation_template=tempobj,
                         solution_template=tempobj,
                         code=pyobj,
                         code_preamble=pyobj,
                         code_postamble=pyobj,
                         defaults=template_data.INVALID_DEFAULT_DICT
                         )
            obj.clean()
        except ValidationError:
            raised_validation = True
        self.assertTrue(raised_validation)

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regular_task_creation(self):
        atask = Task(solver_task_example.task_template, 
                           solution_template=solver_task_example.task_solution_template,
                           default_vals=solver_task_example.task_defaults,
                           code=solver_task_example.task_code
                           )
        asolver = Solver(atask,
                                preamble=solver_task_example.task_code_preamble,
                                postamble=solver_task_example.task_code_postamble
                                )
        regtask = regtask_from_solver(asolver)
        self.assertIsInstance(regtask, RegularTask)
        self.assertTrue(RegularTask.objects.exists())

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regular_task_create_with_filetemplate(self):
        atask = Task(solver_task_example.task_template, 
                           solution_template=solver_task_example.task_solution_template,
                           default_vals=solver_task_example.task_defaults,
                           code=solver_task_example.task_code
                           )
        asolver = Solver(atask,
                                preamble=solver_task_example.task_code_preamble,
                                postamble=solver_task_example.task_code_postamble
                                )
        regtask = regtask_from_solver(asolver, store_template_to_file=True)
        self.assertIsInstance(regtask, RegularTask)
        self.assertTrue(RegularTask.objects.exists())
        self.assertTrue(os.path.isfile(os.path.join(MROOT, regtask.formulation_template.file.url)))
        self.assertTrue(os.path.isfile(os.path.join(MROOT, regtask.solution_template.file.url)))

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regular_task_create_with_filecodes(self):
        atask = Task(solver_task_example.task_template, 
                           solution_template=solver_task_example.task_solution_template,
                           default_vals=solver_task_example.task_defaults,
                           code=solver_task_example.task_code
                           )
        asolver = Solver(atask,
                                preamble=solver_task_example.task_code_preamble,
                                postamble=solver_task_example.task_code_postamble
                                )
        regtask = regtask_from_solver(asolver, store_code_to_file=True)
        self.assertIsInstance(regtask, RegularTask)
        self.assertTrue(RegularTask.objects.exists())
        self.assertTrue(os.path.isfile(os.path.join(MROOT, regtask.code.file.url)))
        self.assertTrue(os.path.isfile(os.path.join(MROOT, regtask.code_preamble.file.url)))
        self.assertTrue(os.path.isfile(os.path.join(MROOT, regtask.code_postamble.file.url)))

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regulartask_to_solvertask(self):
        '''Testing for regular task instance conversion and try to solve it.'''
        regtask = RegularTask.objects.all()[0]
        atask, asolver = solver_from_regtask(regtask)
        self.assertIsInstance(asolver, Solver)
        self.assertIsInstance(atask, Task)

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regulartask_trytosolve(self):
        '''Try to solve a regular task with code in body field.
        '''
        tempobj = TemplateModel(body=template_data.VALID_TEMPLATE_BODY_JINJA)
        pyobj = PythonCodeModel(body=template_data.VALID_PYTHON_CODE)
        tempobj.save()
        pyobj.save()
        regtask = RegularTask.objects.create(formulation_template=tempobj, 
                                 solution_template=tempobj,
                                 code=pyobj,
                                 defaults=template_data.VALID_DEFAULT_DICT
                                 )
        atask, asolver = solver_from_regtask(regtask)
        asolver.solve()
        self.assertTrue(asolver.is_solved)

    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regulartask_solve_codefromfile(self):
        '''Try to solve a regular task with code passed as a file'''
        tempobj = TemplateModel(body=template_data.VALID_TEMPLATE_BODY_JINJA)
        tempobj.save()
        pyobj = _safely_create(PythonCodeModel, os.path.join(current_dir, 'tests', 'data',
                       template_data.VALID_PYTHON_CODE_FILENAME
                       ))
        regtask = RegularTask.objects.create(formulation_template=tempobj, 
                                 solution_template=tempobj,
                                 code=pyobj,
                                 defaults=template_data.VALID_DEFAULT_DICT
                                 )
        atask, asolver = solver_from_regtask(regtask)
        asolver.solve()
        self.assertTrue(asolver.is_solved)
    
    @unittest.skipIf('Solver' in locals(), "Solver not installed")
    def test_regulartask_to_solvertask_notsilent(self):
        '''
        check silent creation of solver instance with invalid default values.
        '''
        tempobj = TemplateModel(body=template_data.VALID_TEMPLATE_BODY_JINJA)
        tempobj.save()
        regtask = RegularTask.objects.create(formulation_template=tempobj, 
                                 defaults=template_data.INVALID_DEFAULT_DICT
                                 )
        error_checked = False
        try:
            atask, asolver = solver_from_regtask(regtask, silent=False)
        except:
            error_checked = True
        atask, asolver = solver_from_regtask(regtask)
        self.assertTrue(error_checked)
        self.assertIsInstance(atask, Task)
        self.assertIsInstance(asolver, Solver)


class CategoryTestCase(TestCase):
    '''Problem categories'''
    def setUp(self):
        taskcat = TaskCategory(
                               name=category_data.test_category_name,
                               keywords=category_data.test_category_keys, 
                               description=category_data.test_category_descr
                               )
        taskcat.save()
        self.category = taskcat

    def test_category_created(self):
        self.assertTrue(TaskCategory.objects.exists())

    def test_category_features(self):
        self.assertEqual(self.category.name, category_data.test_category_name)
        self.assertEqual(self.category.keywords, category_data.test_category_keys)
        self.assertEqual(self.category.description, category_data.test_category_descr)

    def test_category_parsing(self): 
        keylist = category_data.test_category_keys.split(',')
        self.assertEqual(self.category.parsekeywords, keylist)

    def test_category_structure(self):
        TaskCategory.objects.create(name=category_data.test_child1_name, parent=self.category)
        cat2 = TaskCategory.objects.create(name=category_data.test_child2_name, parent=self.category)
        TaskCategory.objects.create(name=category_data.test_child3_name, parent=cat2)
        TaskCategory.objects.create(name=category_data.test_child4_name, parent=cat2)
        del cat2
        # Testing for structure correctness
        self.assertTrue(self.category.is_root_node())
        cat2 = TaskCategory.objects.get(name=category_data.test_child2_name)
        chil1 = set([x['name'] for x in cat2.get_children().values()]) 
        chil2 = set([category_data.test_child3_name, category_data.test_child4_name])
        self.assertEqual(chil1, chil2)

        

    
    
        
        
        
    
        
    

    
 
 