import os


SECRET_KEY = os.environ.get('SECRET_KEY')

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = os.environ.get('RDADASHDB_ENGINE') + "://" + \
                          os.environ.get('RDADASHDB_LOGIN') + "@" + \
                          os.environ.get('RDADASHDB_URL') + "/" + \
                          os.environ.get('RDADASHDB_DATABASE')

CREATE_DBTABLES = os.environ.get('CREATE_DBTABLES')

SYSTEM_USER_ACCESSIBLE = os.environ.get('SYSTEM_USER_ACCESSIBLE')
SYSTEM_USER_PASSWORD = os.environ.get('SYSTEM_USER_PASSWORD')

AWSS3_ACCESS_KEY = os.environ.get('AWSS3_ACCESS_KEY')
AWSS3_SECRET_KEY = os.environ.get('AWSS3_SECRET_KEY')
