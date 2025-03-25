from django.urls import path
from .views import reserver_view, mes_reservations_view, modifier_reservation_view, supprimer_reservation_view

urlpatterns = [
    path('reserver/', reserver_view, name='reserver'),
    path('mes/', mes_reservations_view, name='mes_reservations'),
    path('modifier/<int:pk>/', modifier_reservation_view, name='modifier_reservation'),
    path('supprimer/<int:pk>/', supprimer_reservation_view, name='supprimer_reservation'),
]

