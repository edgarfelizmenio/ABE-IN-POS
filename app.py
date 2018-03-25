import logging

from flask import Flask
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = make_celery(app)

logging.basicConfig(level=logging.INFO)

appLogger = logging.StreamHandler()
appLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
app.logger.addHandler(appLogger)
app.logger.setLevel(logging.INFO)

from api import *

if __name__ == '__main__':
    # do not run on port 80 on development
    app.run()