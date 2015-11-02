
from django.db import models


class TemplateModel(models.Model):
    '''Base template model for task and solution formulations.
    '''
    body = models.TextField(verbose_name=_("Content"))
    file = models.FileField(upload_to='templates/%Y/%m/%d',
                            verbose_name=_("Template file"))



class TaskModel(models.Model):
    formulation_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Formulation")
                                                )
    solution_template = models.OneToOneField(
                                TemplateModel,
                                verbose_name=_("Solution")
                                            )
    code

    pub_date = models.DateTimeField('date published')