from jnius import autoclass
from kivy import Logger, platform

PythonActivity = None
if platform == "android":
    PythonActivity = autoclass("org.kivy.android.PythonActivity").mActivity
    Context = autoclass('android.content.Context')
    ContextCompat = autoclass('android.support.v4.content.ContextCompat')


def check_permission(permission, activity=None):
    if platform == "android":
        activity = PythonActivity
    if not activity:
        return False

    permission_status = ContextCompat.checkSelfPermission(activity,
                                                          permission)

    Logger.info(permission_status)
    permission_granted = 0 == permission_status
    Logger.info("Permission Status: {}".format(permission_granted))
    return permission_granted


def ask_permission(permission):
    PythonActivity.requestPermissions([permission])
