from django.urls import path
from .views import reserver_view, mes_reservations_view

urlpatterns = [
    path('reserver/', reserver_view, name='reserver'),
    path('mes/', mes_reservations_view, name='mes_reservations'),
]
