from django.urls import path
from predictor import views

urlpatterns = [
    path("", views.index, name="index"),
    path("predict/", views.predict, name="predict"),
    path("about/", views.about, name="about"),
    path("api/predict/", views.api_predict, name="api_predict"),
]
