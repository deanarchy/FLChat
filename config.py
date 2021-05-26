import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'D{P1>f8X12OG,WIXheZa?wJ+p84a'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'VTF!*Vwkt<5]ckH?CQ%R+j~I(ZN,LE'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    database_name = 'flchat_dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'postgresql://postgres:postgres@localhost/{database_name}'


class TestingConfig(Config):
    database_name = 'flchat_test'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        f'postgresql://postgres:postgres@localhost/{database_name}'


class ProductionConfig(Config):
    database_name = 'flchat'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SSL_REDIRECT = True if os.environ.get('DYNO') else False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
