from django.urls import path
from . import views

urlpatterns = [
    path('', views.checker_view, name='checker'),
    path('generator/', views.generator_view, name='generator'),
]