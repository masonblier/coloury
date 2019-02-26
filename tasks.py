from celery import Celery
from image_color import findDominantColor

# celery config
app = Celery('coloury',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['coloury.tasks'])

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack'],
    CELERY_TASK_SERIALIZER = 'msgpack',
    CELERY_RESULT_SERIALIZER = 'msgpack'
)

# tasks

@app.task(name='tasks.ProcessImageColors')
def ProcessImageColors(filename):
    return findDominantColor(filename)

# start app unless included as lib
if __name__ == '__main__':
    app.start()
