from django.db import models

from django_solver.restrictions import restriction_pool
from django_solver.base.models import RegularUserModel
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class RestrictionModel(models.Model):
    CHOICES = [(x, x) for x in restriction_pool.keys()]
    restriction = models.CharField(choices=CHOICES,
                                   default=CHOICES[0][0],
                                   max_length=100)
    user = models.ForeignKey(RegularUserModel, related_name='restrictions', null=True, blank=False)

    def __str__(self):
        return self.restriction
    
    def status(self, **kwargs):
        _kwargs = kwargs
        _kwargs.update({'user': self.user.user})
        if self.restriction in restriction_pool.keys():
            return restriction_pool[self.restriction].status(**_kwargs)
        else:
            return False
        