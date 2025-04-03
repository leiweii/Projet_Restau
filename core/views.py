from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from reservations.models import Reservation, HoraireSpecial
from menu.models import Plat, Categorie, Ingredient
from django.db.models import Q
from reservations.forms import ReservationForm
from menu.forms import PlatForm, CategorieForm, IngredientForm
from reservations.forms import HoraireSpecialForm
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.forms import UserProfileUpdateForm


def contact_view(request):
    today = date.today()
    fermeture_message = None

    special = HoraireSpecial.objects.filter(date=today).first()
    if special and special.ferme:
        fermeture_message = f"⚠️ Le restaurant est exceptionnellement fermé aujourd’hui ({today.strftime('%d/%m/%Y')})."

    horaires = {
        'Lundi': '12h00 - 14h30 / 19h00 - 22h30',
        'Mardi': '12h00 - 14h30 / 19h00 - 22h30',
        'Mercredi': '12h00 - 14h30 / 19h00 - 22h30',
        'Jeudi': '12h00 - 14h30 / 19h00 - 22h30',
        'Vendredi': '12h00 - 14h30 / 19h00 - 22h30',
        'Samedi': ' ----------/ 19h00 - 22h30',
        'Dimanche': '-------- / 19h00 - 22h30',
    }

    return render(request, 'core/contact.html', {
        'fermeture_message': fermeture_message,
        'horaires': horaires
    })



def home_view(request):
    return render(request, 'core/home.html')




# 限定只允许管理员访问
def admin_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(admin_required)
def dashboard_home(request):
    search = request.GET.get('search', '')
    reservations = Reservation.objects.all().order_by('-date')

    if search:
        reservations = reservations.filter(
            Q(nom__icontains=search) |
            Q(telephone__icontains=search) |
            Q(email__icontains=search)
        )

    plats = Plat.objects.select_related('categorie').all()

    return render(request, 'core/dashboard.html', {
        'reservations': reservations,
        'plats': plats,
        'search': search,
    })



# gerer les réservations
@user_passes_test(admin_required)
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'core/reservation_edit.html', {'form': form, 'reservation': reservation})

@user_passes_test(admin_required)
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.delete()
        return redirect('dashboard')
    return render(request, 'core/reservation_delete.html', {'reservation': reservation})


# gerer les plats
@user_passes_test(admin_required)
def plat_edit(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PlatForm(instance=plat)
    return render(request, 'core/plat_edit.html', {'form': form, 'plat': plat})

@user_passes_test(admin_required)
def plat_delete(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    if request.method == 'POST':
        plat.delete()
        return redirect('dashboard')
    return render(request, 'core/plat_delete.html', {'plat': plat})


@user_passes_test(admin_required)
def plat_create(request):
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PlatForm()
    return render(request, 'core/plat_create.html', {'form': form})




# gerer les horaires
@user_passes_test(admin_required)
def horaires_list(request):
    horaires = HoraireSpecial.objects.order_by('date')
    return render(request, 'core/horaires_list.html', {'horaires': horaires})

@user_passes_test(admin_required)
def horaire_create(request):
    if request.method == 'POST':
        form = HoraireSpecialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('horaires_list')
    else:
        form = HoraireSpecialForm()
    return render(request, 'core/horaire_form.html', {'form': form, 'title': 'Ajouter un jour spécial'})

@user_passes_test(admin_required)
def horaire_edit(request, pk):
    horaire = get_object_or_404(HoraireSpecial, pk=pk)
    if request.method == 'POST':
        form = HoraireSpecialForm(request.POST, instance=horaire)
        if form.is_valid():
            form.save()
            return redirect('horaires_list')
    else:
        form = HoraireSpecialForm(instance=horaire)
    return render(request, 'core/horaire_form.html', {'form': form, 'title': 'Modifier le jour'})

@user_passes_test(admin_required)
def horaire_delete(request, pk):
    horaire = get_object_or_404(HoraireSpecial, pk=pk)
    if request.method == 'POST':
        horaire.delete()
        return redirect('horaires_list')
    return render(request, 'core/horaire_delete.html', {'horaire': horaire})



# gerer les catégories

@user_passes_test(admin_required)
def categorie_list(request):
    categories = Categorie.objects.all().order_by('nom')
    return render(request, 'core/categorie_list.html', {'categories': categories})

@user_passes_test(admin_required)
def categorie_create(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categorie_list')
    else:
        form = CategorieForm()
    return render(request, 'core/categorie_form.html', {'form': form, 'title': 'Ajouter une catégorie'})

@user_passes_test(admin_required)
def categorie_edit(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            return redirect('categorie_list')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'core/categorie_form.html', {'form': form, 'title': 'Modifier la catégorie'})

@user_passes_test(admin_required)
def categorie_delete(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        return redirect('categorie_list')
    return render(request, 'core/categorie_delete.html', {'categorie': categorie})



# gerer les clients
@user_passes_test(admin_required)
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'core/user_list.html', {'users': users})

@user_passes_test(admin_required)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user, profile=profile)
        if form.is_valid():
            form.save(user, profile)
            return redirect('user_list')
    else:
        form = UserProfileUpdateForm(instance=user, profile=profile)
    return render(request, 'core/user_edit.html', {'form': form, 'user_obj': user})

@user_passes_test(admin_required)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'core/user_delete.html', {'user_obj': user})


# gerer les Ingredients

@user_passes_test(admin_required)
def ingredient_list(request):
    ingredients = Ingredient.objects.order_by('nom')
    return render(request, 'core/ingredient_list.html', {'ingredients': ingredients})

@user_passes_test(admin_required)
def ingredient_create(request):
    form = IngredientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('ingredient_list')
    return render(request, 'core/ingredient_form.html', {'form': form, 'title': 'Ajouter un ingrédient'})

@user_passes_test(admin_required)
def ingredient_edit(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    form = IngredientForm(request.POST or None, instance=ingredient)
    if form.is_valid():
        form.save()
        return redirect('ingredient_list')
    return render(request, 'core/ingredient_form.html', {'form': form, 'title': 'Modifier l’ingrédient'})

@user_passes_test(admin_required)
def ingredient_delete(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient_list')
    return render(request, 'core/ingredient_delete.html', {'ingredient': ingredient})


