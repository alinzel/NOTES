from django.urls import path
from . import views

app_name="[pyecharts_django_test]"

urlpatterns = [
path("index",views.index, name="index")
        ]