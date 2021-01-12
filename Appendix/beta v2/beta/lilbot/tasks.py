from background_task import background
from django.utils import timezone
import os, sys
from beta.settings import BASE_DIR
file_path = os.path.join(BASE_DIR, 'templates/pyScript')
#Bear in mind that the relative path is from your Django project's root folder.
sys.path.insert(1, file_path)
import lilbot_prediction
from background_task.models import Task

@background()
def startMidiGen():
    print("clear tasks")
    Task.objects.all().delete()
    print('++++++++++++++++++++++++++ midi generation started ...')
    lilbot_prediction.runAll()
    print('++++++++++++++++++++++++++ midi Generation ended ...')
