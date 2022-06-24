import os


SECRET_KEY = os.environ.get('SECRET_KEY')

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "postgresql://" + \
                          os.environ.get('RDADASHDB_USERNAME') + ":" + os.environ.get('RDADASHDB_PASSWORD') + \
                          "@" + os.environ.get('RDADASHDB_URL') + ":" + os.environ.get('RDADASHDB_PORT') + \
                          "/" + os.environ.get('RDADASHDB_DATABASE')


CREATE_DBTABLES = os.environ.get('CREATE_DBTABLES')

SYSTEM_USER_ACCESSIBLE = os.environ.get('SYSTEM_USER_ACCESSIBLE')
SYSTEM_USER_PASSWORD = os.environ.get('SYSTEM_USER_PASSWORD')
