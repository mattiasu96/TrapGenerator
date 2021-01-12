from django.urls import path
from django.contrib import admin
from . import views



urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home , name = "home"),
    # path('test', views.testFun, name="script"),
    path('midiGeneration', views.midiGen, name="midiGeneration"),
    path('wait', views.waitPage, name="waitaminute"),
    path('generateNew', views.generateNew, name="reGen"),
    # path('prova', views.prova, name="prova"),
]