# 🍣 Osaka — Application Web de Réservation Restaurant (Django)

Application web complète développée avec **Django** permettant à un restaurant japonais de :

* gérer les réservations en ligne
* afficher le menu
* proposer des menus promotionnels
* administrer le site via un dashboard personnalisé
* gérer horaires spéciaux et jours fériés

Projet pédagogique mais structuré comme un vrai projet pro.

---

# 🚀 Fonctionnalités principales

## 👤 Clients

* Réserver une table **avec ou sans compte**
* Créer un compte / se connecter
* Mot de passe oublié
* Voir :

  * historique des réservations
  * modifier / supprimer réservation
* Consulter :

  * menu du restaurant
  * promotions
  * horaires
  * page contact + Google Maps

---

## 🍱 Menu du restaurant

* Catégories :

  * Entrées
  * Plats
  * Desserts
  * Boissons
* Recherche de plats
* Filtre par prix
* 4 plats par ligne
* Ingrédients affichés
* Images des plats

---

## 🎁 Menus promotionnels (-20%)

Le restaurant peut créer :

* Menu Entrée + Plat
* Menu Plat + Dessert

Avec :

* nom du menu
* composition
* prix calculé automatiquement (-20%)

Page publique :

```
/promotions/
```

---

## 🛠 Dashboard Admin personnalisé (sans Django Admin)

Accessible :

```
/admin-panel/
```

Permet de gérer :

* réservations
* plats
* catégories
* ingrédients
* menus promotionnels
* horaires spéciaux

CRUD complet :

* créer
* modifier
* supprimer

Accès réservé aux `is_staff=True`.

---

# 🗄 Structure base de données

## Utilisateur

```
User
 └── Profile (1-1)
 └── Reservation (1-N)
```

## Menu

```
Categorie
 └── Plat
      └── Ingredient (N-N)
```

## Promotions

```
MenuPromotionnel
 ├── plat_principal
 └── plat_associe
```

## Horaires spéciaux

```
HoraireSpecial
- date
- ferme
- ouverture
- fermeture
- description
```

---

# ⚙️ Installation

## 1️⃣ Cloner le projet

```bash
git clone https://github.com/leiweii/Projet_Restau.git
```

## 2️⃣ Environnement virtuel

```bash
python -m venv env
source venv/bin/activate
```

Windows :

```bash
venv\Scripts\activate
```

## 3️⃣ Installer dépendances

```bash
pip install django pillow
```

---

## 4️⃣ Migration DB

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 5️⃣ Créer superuser

```bash
python manage.py createsuperuser
```

Puis dans shell :

```python
from django.contrib.auth.models import User
u = User.objects.get(username="admin")
u.is_staff = True
u.save()
```

---

## 6️⃣ Lancer serveur

```bash
python manage.py runserver
```

Site :

```
http://127.0.0.1:8000
```

---

# 📁 Structure projet

```
osaka/
│
├── accounts/
├── menu/
├── reservations/
├── core/
│
├── templates/
├── static/
├── media/
└── manage.py
```

---

# 📄 Pages du site

| URL           | Description |
| ------------- | ----------- |
| /             | Accueil     |
| /menu/        | Menu        |
| /promotions/  | Menus promo |
| /reservation/ | Réserver    |
| /contact/     | Contact     |
| /login/       | Connexion   |
| /profile/     | Profil      |
| /admin-panel/ | Dashboard   |

---

# 🧪 Tests shell

```bash
python manage.py shell
```

Créer plats :

```python
from menu.models import Plat
Plat.objects.create(nom="Sushi", prix=10)
```

Créer menu promo :

```python
from menu.models import MenuPromotionnel
MenuPromotionnel.objects.create(...)
```

Tester prix :

```python
menu.prix_total()
```

---

# 🔐 Sécurité

* Login requis pour profil
* Admin staff uniquement
* CSRF activé
* Validation formulaire

---

# 🌍 Multilingue

Support :

* Français
* Anglais
* Chinois

Utilisation :

```
django i18n
```

---

# 📧 Notifications

Possible :

* email confirmation réservation
* reset password

---

### Réservation

* vérifie horaires
* vérifie jours fermés
* vérifie capacité

---

# 🖥 Technologies

* Python
* Django
* SQLite
* Bootstrap
* HTML CSS JS


# 👨‍💻 Auteur

Leiwei SHI

# 📌 Commandes utiles

```bash
python manage.py shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
