from django.urls import path, include
from Home import views

urlpatterns = [
    path("",views.home,name="home"),
]