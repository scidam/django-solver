
from django.contrib.auth.models import User, Group


class Restriction:
    '''
    Test for particular restriction for the User or Group.
    If status function returns True (restriction is passed, no prevention is needed);
    If status function returns False (restriction is occured, the action should be prevented).
    '''

    def __init__(self, description=''):
        self.description = description
    
    @staticmethod
    def status(**kwargs):
        raise NotImplementedError


# -------------------------- Collection of Restrictions ---------------------------------------

# -------------------------------Check if user in a specified group -------------------------
_in_group_restriciton = Restriction(description='Check for user come from allowed group')

def _in_group_status(user=None, group=None):
    if group in user.groups.all():
        return True
    else:
        return False

_in_group_restriciton.status = _in_group_status
# -------------------------------------------------------------------------------------------


# -------------------------------Check if user has specific name ----------------------------
_specname_restriciton = Restriction(description='Check for specific user name.\
If username is equal the specified name the event should be prevented')

def _specname_status(user=None, username=''):
    if user.username == username:
        return False
    else:
        return True

_specname_restriciton.status = _specname_status
# -------------------------------------------------------------------------------------------


# ---------------- Check if username included in specified list of usernames ----------------
_username_in_list_restriciton = Restriction(description='Check for username is in specified list of not allowed usernames')

def _username_in_list_status(user=None, userlist=['']):
    return True if user.username not in userlist else False

_username_in_list_restriciton.status = _username_in_list_status
# -------------------------------------------------------------------------------------------







# ------------------------------ Restriction registration via common pool -------------------

restriction_pool = {'in_group': _in_group_restriciton,
                    'specific_username': _specname_restriciton,
                    'username_in_list': _username_in_list_restriciton
                    }




