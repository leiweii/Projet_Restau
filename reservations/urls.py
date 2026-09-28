from django.urls import path
from .views import (
    availability_view,
    guest_cancel_reservation_view,
    guest_modify_reservation_view,
    guest_reservation_view,
    mes_reservations_view,
    modifier_reservation_view,
    reserver_view,
    supprimer_reservation_view,
)

urlpatterns = [
    path('reserver/', reserver_view, name='reserver'),
    path('disponibilites/', availability_view, name='reservation_availability'),
    path('mes/', mes_reservations_view, name='mes_reservations'),
    path('modifier/<int:pk>/', modifier_reservation_view, name='modifier_reservation'),
    path('supprimer/<int:pk>/', supprimer_reservation_view, name='supprimer_reservation'),
    path('gerer/<uuid:token>/', guest_reservation_view, name='guest_reservation'),
    path(
        'gerer/<uuid:token>/modifier/',
        guest_modify_reservation_view,
        name='guest_modify_reservation',
    ),
    path(
        'gerer/<uuid:token>/annuler/',
        guest_cancel_reservation_view,
        name='guest_cancel_reservation',
    ),
    # path('commander/', commander_view, name='commander'),
]

