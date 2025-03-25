from django.urls import path
from .views import home_view, contact_view, dashboard_home, reservation_edit, reservation_delete, plat_edit, plat_delete, plat_create
from .views import horaires_list, horaire_create, horaire_edit, horaire_delete, categorie_list, categorie_create, categorie_edit, categorie_delete
from .views import user_list, user_edit, user_delete
urlpatterns = [
    path('', home_view, name='home'),
    path('contact/', contact_view, name='contact'),
    path('admin-panel/', dashboard_home, name='dashboard'),
    path('admin-panel/reservation/<int:pk>/edit/', reservation_edit, name='reservation_edit'),
    path('admin-panel/reservation/<int:pk>/delete/', reservation_delete, name='reservation_delete'),
    path('admin-panel/plat/<int:pk>/edit/', plat_edit, name='plat_edit'),
    path('admin-panel/plat/<int:pk>/delete/', plat_delete, name='plat_delete'),
    path('admin-panel/plat/add/', plat_create, name='plat_create'),
    path('admin-panel/horaires/', horaires_list, name='horaires_list'),
    path('admin-panel/horaires/add/', horaire_create, name='horaire_create'),
    path('admin-panel/horaires/<int:pk>/edit/', horaire_edit, name='horaire_edit'),
    path('admin-panel/horaires/<int:pk>/delete/', horaire_delete, name='horaire_delete'),
    path('admin-panel/categories/', categorie_list, name='categorie_list'),
    path('admin-panel/categories/add/', categorie_create, name='categorie_create'),
    path('admin-panel/categories/<int:pk>/edit/', categorie_edit, name='categorie_edit'),
    path('admin-panel/categories/<int:pk>/delete/', categorie_delete, name='categorie_delete'),
    path('admin-panel/users/', user_list, name='user_list'),
    path('admin-panel/users/<int:pk>/edit/', user_edit, name='user_edit'),
    path('admin-panel/users/<int:pk>/delete/', user_delete, name='user_delete'),

]
