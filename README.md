# Restaurant Osaka

Application Django de présentation et de réservation pour un restaurant japonais. Le projet conserve une architecture monolithique simple : les comptes, le menu, les réservations et l'administration métier sont séparés en applications Django.

## État actuel

Fonctionnalités déjà présentes :

- menu public avec catégories, plats, ingrédients, recherche et filtre de prix ;
- menus promotionnels composés de deux plats ;
- réservation avec ou sans compte ;
- espace client pour consulter, modifier et supprimer ses réservations ;
- inscription, connexion, profil et réinitialisation du mot de passe ;
- tableau de bord réservé au personnel pour gérer réservations, plats, catégories, ingrédients, utilisateurs, promotions et horaires spéciaux ;
- configuration distincte pour le développement et la production.

Travail prévu dans les prochaines phases : règles complètes d'horaires hebdomadaires, créneaux de 30 minutes, capacité simultanée, lien sécurisé pour les réservations invitées, délai de modification et nouvelle interface responsive. Ces éléments ne doivent pas être considérés comme terminés.

## Architecture

```text
accounts/              comptes et profils
core/                  accueil, contact et tableau de bord métier
menu/                  catégories, plats, ingrédients et promotions
reservations/          réservations et horaires spéciaux
restaurant_project/    URLs et réglages Django
  settings/
    base.py             réglages communs
    development.py      développement local
    production.py       production sécurisée
templates/              gabarits HTML
static/                 CSS, JavaScript et images statiques
media/                  images ajoutées par l'administration
```

Le projet utilise Django 5, SQLite en local, Bootstrap 5 et django-crispy-forms. Il ne contient ni API séparée ni frontend React.

## Installation locale

Prérequis : Python 3.11 ou version compatible avec les dépendances du fichier `requirements.txt`.

```powershell
python -m venv env
env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sous macOS ou Linux, l'activation se fait avec `source env/bin/activate`.

Le site est ensuite disponible sur `http://127.0.0.1:8000/`. En développement, les emails sont affichés dans le terminal et aucun identifiant SMTP n'est nécessaire.

`manage.py` sélectionne automatiquement `restaurant_project.settings.development`. Pour choisir explicitement un autre module :

```powershell
$env:DJANGO_SETTINGS_MODULE = "restaurant_project.settings.production"
```

## Configuration de production

Copier `.env.example` vers un fichier local `.env`, remplacer toutes les valeurs d'exemple, puis injecter ces variables dans l'environnement d'exécution. Django ne charge pas automatiquement le fichier `.env` : l'hébergeur, Docker ou un gestionnaire de secrets doit le faire.

Variables obligatoires :

- `DJANGO_SECRET_KEY` : secret long, aléatoire et propre à la production ;
- `DJANGO_ALLOWED_HOSTS` : noms de domaine séparés par des virgules ;
- `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD` : compte SMTP ;
- `PATRON_EMAIL` : destinataire des notifications ;
- `DEFAULT_FROM_EMAIL` : expéditeur visible.

`EMAIL_HOST`, `EMAIL_PORT` et `EMAIL_USE_TLS` disposent de valeurs par défaut modifiables. Les réglages de production activent HTTPS forcé, cookies sécurisés, HSTS et `DEBUG=False`.

> Important : un ancien mot de passe d'application Gmail a déjà été conservé dans l'historique du projet. Il faut le révoquer dans le compte Google concerné et en créer un nouveau uniquement dans le gestionnaire de secrets de production. Le retirer du code actuel ne le retire pas de l'historique Git.

Avant un déploiement :

```powershell
$env:DJANGO_SETTINGS_MODULE = "restaurant_project.settings.production"
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic
```

## URLs principales

| URL | Fonction |
| --- | --- |
| `/` | accueil |
| `/menu/` | menu |
| `/menu/promotions/` | promotions |
| `/reservations/reserver/` | nouvelle réservation |
| `/reservations/mes/` | réservations du client connecté |
| `/compte/connexion/` | connexion |
| `/compte/profil/` | profil |
| `/contact/` | contact |
| `/admin-panel/` | tableau de bord du personnel |
| `/admin/` | administration Django |

## Qualité et vérifications

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Les fichiers locaux sensibles ou générés (`.env`, base SQLite, journaux, couverture, sauvegardes et environnement virtuel) sont ignorés par Git.

## Documentation du projet

- la conception cible se trouve dans `docs/superpowers/specs/2026-09-27-restaurant-osaka-design.md` ;
- les plans d'implémentation se trouvent dans `docs/superpowers/plans/`.

Auteur initial : Leiwei SHI.
