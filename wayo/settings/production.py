from .base import *
ALLOWED_HOSTS = ['188.166.229.132']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DEBUG'),
    }
}

INSTALLED_APPS =+[
    'storages',
]

AWS_ACCESS_KEY_ID = 'NMH56U2MV4NVQHBZB4DV'
AWS_SECRET_ACCESS_KEY = 'p5lvJTqge/owJ83RjHkUfqfNEJSf17gzq6ZcFwbdN9M'
AWS_STORAGE_BUCKET_NAME = 'wayodatastorage'
AWS_S3_ENDPOINT_URL = 'https://sgp1.digitaloceanspaces.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'Data'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = 'https://%s/%s/' % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'