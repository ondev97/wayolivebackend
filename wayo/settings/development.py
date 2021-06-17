from .base import *


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR,'static/')

MEDIA_ROOT = os.path.join(BASE_DIR,'static/images/')