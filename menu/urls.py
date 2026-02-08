from django.urls import path
from .views import menu_view, promotions_view

urlpatterns = [
    path('', menu_view, name='menu'),
    path('promotions/', promotions_view, name='promotions'),
]
