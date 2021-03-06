
import ast
import os

from mptt.models import MPTTModel, TreeForeignKey

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django_solver.base.errors import PYCODE_ERROR, DEFAULT_DICT_ERROR
from django.contrib.auth.models import User
from django_solver.restrictions import restriction_pool

__all__ = ['TemplateModel', 'PythonCodeModel', 'RegularTask', 'TaskCategory', 'RegularUserModel']


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
                            default=settings.DJSOLVER_TEMPLATE_TYPES[0][0],
                            choices=settings.DJSOLVER_TEMPLATE_TYPES,
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
                    ast.parse(self.file.read().decode('utf-8'))
                except:
                    raise ValidationError(PYCODE_ERROR)

        if self.body and not self.file:
            try:
                ast.parse(self.body)
            except:
                raise ValidationError(PYCODE_ERROR)


@python_2_unicode_compatible
class TaskModel(models.Model):
    formulation_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Formulation")
                                                )
    solution_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Solution"),
                                blank=True,
                                null=True
                                            )
    code = models.ForeignKey(PythonCodeModel,
                                verbose_name=_("Python code"),
                                null=True,
                                blank=True
                                )

    code_preamble = models.ForeignKey(PythonCodeModel,
                                         verbose_name=_("Python code"),
                                         null=True,
                                         blank=True
                                         )

    code_postamble = models.ForeignKey(PythonCodeModel,
                                          verbose_name=_("Python code"),
                                          null=True,
                                          blank=True
                                          )

    defaults = models.TextField(verbose_name=_("Default values"),
                                blank=True, default='')

    # Date of Task creation
    updated = models.DateTimeField(auto_now=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    public = models.BooleanField(default=False,
                                 verbose_name=_('Published'), blank=True
                                 )
    keywords = models.CharField(max_length=1000, blank=True, default=True)

    @property
    def get_keywords(self):
        return self.keywords.split(settings.DJSOLVER_KEYWORD_SEPARATOR)

    @property
    def get_defaults(self):
        try:
            res = ast.literal_eval(self.defaults)
        except:
            res = dict()
        return res 

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

    class Meta:
        abstract = True


class RegularTask(TaskModel):

    class Meta:
        abstract = False


@python_2_unicode_compatible
class TaskCategory(MPTTModel):
    name = models.CharField(max_length=100, unique=True, default='')
    keywords = models.CharField(max_length=1000, blank=True, default='')
    description = models.CharField(max_length=2000, blank=True, default='')
    image = models.ImageField(upload_to="djsolver/cats", null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    regtask = models.ForeignKey(RegularTask, verbose_name=_('Problem'),
                                null=True, blank=True, related_name='categories'
                                )
    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name[:50]

    @property
    def get_keywords(self):
        return self.keywords.split(settings.DJSOLVER_KEYWORD_SEPARATOR)


@python_2_unicode_compatible
class RegularUserModel(models.Model):
    user = models.OneToOneField(User,
                                verbose_name=_("User"),
                                )
    def __str__(self):
        return self.user.username

    def status(self, **kwargs):
        _kwargs = kwargs
        _kwargs.update({'user': self.user})
        res = []
        for item in self.restrictions.all():
            if item.restriction in restriction_pool.keys():
              res.append(restriction_pool[item.restriction].status(**_kwargs))
        return all(res)
