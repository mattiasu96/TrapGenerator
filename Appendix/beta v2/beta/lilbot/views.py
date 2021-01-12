import sys
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from background_task import background
from django.utils import timezone
import mimetypes
from . import tasks

# sys.path.insert(1, r'C:\Users\Emanuele\Documents\Progetto CPAC\Code\Appendice\beta\beta\beta\templates\pyScript')
# import simple 
# sys.path.insert(1, r'C:\Users\Emanuele\Documents\Progetto CPAC\Code\Appendice\beta\beta v2\beta\templates\pyScript')
# import lilbot_prediction

import os
from time import sleep
from beta.settings import BASE_DIR
file_path = os.path.join(BASE_DIR, 'templates/pyScript')
#Bear in mind that the relative path is from your Django project's root folder.
sys.path.insert(1, file_path)
import lilbot_prediction


midiDisplay = False
waitingFlag = False
checkFile = lilbot_prediction.checkFile
midiFilePath = lilbot_prediction.static_midi

# @background(schedule=timezone.now())
# def startMidiGen():
#     print('++++++++++++++++++++++++++ midi generation started ...')
#     lilbot_prediction.runAll()
#     #sleep(10)
#     print('++++++++++++++++++++++++++ midi Generation ended ...')
#     # hbg = True
#     # print(hbg)

@background()
def hasBeenGenerated():
    # hbg = True
    print('has been generated')
    # print(hbg)

# Create your views here.
hbg = False

def home(request):
    print("Home")
    return render(request, 'index.html', { 
        'midiDisplay' : False,
        'waitingFlag' : False })

# def testFun(request):
#     print('Test')
#     simple.generateTestFile()
#     print("test eseguito")
#     return render(request, 'index.html', { 'midiDisplay' : True })


def midiGen(request):
    print('midi generation')
    hbg = False
    stillWaiting()
    print('end waiting')
    return render(request, 'index.html', { 
        'midiDisplay' : True,
        'waitingFlag' : False,
        'mifi': midiFilePath })

def waitPage(request):
    print('wait page')
    hasBeenGenerated()
    print(hbg)
    return render(request, 'index.html', { 
        'midiDisplay' : False,
        'waitingFlag' : True })

def generateNew(request):
    tasks.startMidiGen()
    # return home(request)
    return redirect('home')

def stillWaiting():
    hbg = False
    print("Still waiting --- hbg is: ", hbg)
    while hbg is False:
        sleep(2)
        hbg = os.path.exists(checkFile)


#  def conta(z):
#     z = 0     
#     while z < 10:
#         sleep(1)
#         z = z + 1
#         print(z)

# def prova(request):
#     conta(0)
#     # redirect = reverse('home')      
#     # redirect = reverse('waitaminute')             
#     # return JsonResponse({'redirect': redirect})
#     return HttpResponse('<h1>Page</h1>')




