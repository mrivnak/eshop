from django.urls import path

from . import views

urlpatterns = [
    path('status', views.StatusCheck.as_view())
]
