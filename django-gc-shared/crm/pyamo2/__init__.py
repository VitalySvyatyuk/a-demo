from django.conf import settings
from api import PyamoAPI


def get_pyamo_api(debug=False):
    return PyamoAPI(
        settings.PYAMO['base_url'],
        settings.PYAMO['login'],
        settings.PYAMO['hash'],
        debug=debug)
