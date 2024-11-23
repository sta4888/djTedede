from .settings import *

TESTING = True

# Remove drf-yasg from INSTALLED_APPS during testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'drf_yasg']

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
