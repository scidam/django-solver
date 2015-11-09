
import ast
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django_solver.base.errors import PYCODE_ERROR, DEFAULT_DICT_ERROR

__all__ = ['TemplateModel', 'PythonCodeModel', 'TaskModel']

@python_2_unicode_compatible
class TemplateModel(models.Model):
    '''Base template model for task and solution formulations.

    .. note::

        Field <file> has higher priority over <body>. If <file> is defined,
        it will be used at first.

    '''
    body = models.TextField(verbose_name=_("Content"), blank=True, default='')
    file = models.FileField(upload_to='templates/%Y/%m/%d',
                            verbose_name=_("Template file"),
                            blank=True, null=True)
    type = models.CharField(verbose_name=_("Template type"),
                            default=settings.ALLOWED_TEMPLATE_TYPES[0][0],
                            choices=settings.ALLOWED_TEMPLATE_TYPES,
                            max_length=2
                            )

    def __str__(self):
        if self.file:
            return self.file.name[:30]
        if self.body:
            return self.body[:30]



@python_2_unicode_compatible
class PythonCodeModel(models.Model):
    '''Base PythonCode model.

    Used to store python code for solver. It uses weak validation
    of Python code (just parsing (not compiling) it with ast module).

     .. note::

        Field <file> has higher priority over <body>. If <file> is defined,
        it will be used at first.
    '''

    body = models.TextField(verbose_name=_("Python code"),
                            blank=True, default='')
    file = models.FileField(upload_to='pycodes/%Y/%m/%d',
                            verbose_name=_("Code file"), blank=True, null=True)

    def __str__(self):
        if self.file:
            return self.file.name[:30]
        if self.body:
            return self.body[:30]

    def clean(self):
        if self.file:
            if os.path.isfile(self.file.path):
                try:
                    ast.parse(self.file.read())
                except:
                    raise ValidationError(PYCODE_ERROR)

        if self.body and not self.file:
            try:
                ast.parse(self.body)
            except:
                raise ValidationError(PYCODE_ERROR)


class TaskModel(models.Model):
    formulation_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Formulation")
                                                )
    solution_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Solution")
                                            )
    code = models.OneToOneField(PythonCodeModel,
                                verbose_name=_("Python code")
                                )

    code_preamble = models.OneToOneField(PythonCodeModel,
                                         verbose_name=_("Python code")
                                         )

    code_postamble = models.OneToOneField(PythonCodeModel,
                                          verbose_name=_("Python code")
                                          )

    defaults = models.TextField(verbose_name=_("Default values"), blank=True, default='')

    # Date of Task creation
    created = models.DateTimeField(auto_now=True, blank=True)

    public = models.BooleanField(default=False,
                                 verbose_name=_('Published'), blank=True
                                 )

    def render(self):
        raise NotImplemented

    def clean(self):
        if self.defaults:
            parsed = None
            try:
                parsed = ast.parse(self.defaults).body[0].value
            except:
                raise ValidationError(DEFAULT_DICT_ERROR)
            if not isinstance(parsed, ast.Dict):
                raise ValidationError(DEFAULT_DICT_ERROR)
