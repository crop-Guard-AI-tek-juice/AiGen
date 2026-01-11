from django.urls import path
from .views import generate_advice

urlpatterns = [
    path('generate-advice/',generate_advice, name='generate_advice'),
]
