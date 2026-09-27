# Refonte progressive de Restaurant Osaka

Date : 27 septembre 2026

Statut : design approuve en conversation, en attente de validation du document

Portee : site vitrine, carte et reservation de tables

## 1. Objectif

Transformer l'application Django existante en un projet de portfolio credible qui puisse aussi servir de base a un vrai site de restaurant. La premiere version reste centree sur la presentation du restaurant, la carte et la reservation de tables. La commande en ligne, la livraison et le paiement ne font pas partie de cette version.

Le projet doit :

- conserver les comptes, plats, images, promotions et reservations existants ;
- proposer une experience mobile simple et professionnelle ;
- appliquer les regles de reservation cote serveur ;
- fournir au personnel un outil de gestion adapte au travail quotidien ;
- separer clairement les responsabilites des modules Django ;
- etre testable, securisable et deployable sans introduire une SPA React ni des microservices.

## 2. Strategie de transformation

La refonte sera progressive dans le depot actuel. Il n'y aura pas de reecriture complete.

Les fonctionnalites qui marchent restent disponibles pendant que les responsabilites sont deplacees vers des modules mieux delimites. Chaque lot comporte ses propres migrations, tests, verification visuelle et controle du diff Git.

L'architecture cible reste un monolithe Django modulaire avec rendu serveur et Bootstrap. SQLite reste acceptable en developpement. Une base PostgreSQL pourra etre utilisee lors d'un deploiement reel sans changer l'architecture fonctionnelle.

## 3. Architecture cible

### `accounts`

Responsable de l'inscription, la connexion, la recuperation de mot de passe, le profil client et l'association des reservations a un compte.

Ce module ne calcule pas les disponibilites et ne contient pas de logique de menu.

### `restaurant`

Responsable des informations de l'etablissement et des regles generales d'accueil :

- nom, adresse, telephone et email public ;
- capacite simultanee par defaut ;
- duree standard d'une reservation ;
- intervalle entre les heures d'arrivee ;
- horaires hebdomadaires ;
- fermetures et ouvertures exceptionnelles.

Ce module devient la source unique des horaires affiches sur l'accueil, la page de contact et le parcours de reservation.

### `menu`

Responsable des categories, plats, ingredients, allergenes et promotions.

Les ingredients et les allergenes sont deux concepts distincts. Un plat peut indiquer ses ingredients, ses allergenes, son caractere vegetarien, son niveau de piquant, sa disponibilite et son image.

Les promotions possedent une periode de validite et un statut actif. L'accueil et la page Promotions utilisent les memes donnees.

### `reservations`

Responsable des disponibilites et du cycle de vie des reservations :

- generation des creneaux ouverts ;
- calcul de la capacite restante ;
- creation et confirmation automatique ;
- modification et annulation ;
- acces securise des visiteurs sans compte ;
- historique et statuts de gestion.

La logique metier est placee dans des services testables, et non dans les templates ou dans du JavaScript client.

### `dashboard`

Responsable de l'interface quotidienne du personnel. Il utilise les services publics des autres modules au lieu de manipuler toute la logique dans un seul fichier `core/views.py`.

Le Django Admin est conserve pour la maintenance technique. Le tableau de bord personnalise est destine au personnel du restaurant.

### `core`

Responsable uniquement des pages transversales et de leur composition : accueil, contact, pages legales et contexte commun. Il ne porte plus les CRUD des autres modules.

### `config`

Responsable des reglages du projet, de l'environnement, du routage racine, des journaux et des parametres de deploiement.

## 4. Modele fonctionnel

### Configuration du restaurant

`RestaurantSettings` contient une configuration unique :

- identite et coordonnees publiques ;
- capacite simultanee par defaut : 20 couverts ;
- duree d'occupation par defaut : 90 minutes ;
- pas entre deux heures d'arrivee : 30 minutes ;
- delai minimal de modification ou d'annulation : 2 heures ;
- nombre maximal de personnes par reservation automatique : 8.

Ces valeurs sont modifiables par le personnel autorise.

### Horaires hebdomadaires

`WeeklyOpeningHours` represente un intervalle d'ouverture pour un jour de la semaine. Plusieurs lignes peuvent exister pour un meme jour, afin de representer par exemple un service de midi et un service du soir.

Un intervalle doit avoir une heure de fin strictement posterieure a son heure de debut. Les intervalles d'un meme jour ne doivent pas se chevaucher.

### Horaires exceptionnels

`SpecialOpeningHours` remplace les horaires normaux pour une date precise. Une date peut etre entierement fermee ou comporter un ou plusieurs intervalles speciaux.

Les horaires exceptionnels sont prioritaires sur les horaires hebdomadaires.

### Reservation

Une reservation contient les coordonnees du client, la date et l'heure d'arrivee, le nombre de personnes, un commentaire facultatif et les dates d'audit.

Elle possede un statut parmi :

- `confirmed` : reservation validee automatiquement ;
- `cancelled` : annulee mais conservee dans l'historique ;
- `seated` : client arrive et installe ;
- `completed` : service termine ;
- `no_show` : client non presente.

Les reservations visiteurs possedent un jeton de gestion aleatoire, non devinable et revocable. Le jeton permet uniquement de consulter, modifier ou annuler la reservation concernee. Il ne donne aucun acces au compte ou au tableau de bord.

### Menu et allergenes

`Allergen` represente un allergene officiel distinct d'un ingredient. Les donnees existantes de plats et ingredients sont conservees. Aucun ingredient n'est automatiquement transforme en allergene sans correspondance explicite validee.

Les plats recoivent progressivement les champs de presentation necessaires sans casser les donnees existantes.

## 5. Regles de reservation

### Generation des creneaux

Pour une date et un nombre de personnes :

1. lire les horaires exceptionnels de la date, sinon les horaires hebdomadaires ;
2. generer des heures d'arrivee toutes les 30 minutes dans chaque intervalle ;
3. exclure les heures passees et celles qui ne permettent pas de respecter le delai minimal ;
4. verifier la capacite sur toute la duree de 90 minutes ;
5. retourner uniquement les creneaux disposant d'une capacite suffisante.

Une reservation de 9 personnes ou plus n'est pas creee automatiquement. L'interface invite le client a telephoner au restaurant.

### Calcul des chevauchements

Chaque reservation occupe l'intervalle allant de son heure d'arrivee a 90 minutes plus tard. Deux reservations se chevauchent lorsque leurs intervalles ont une partie commune.

Pour accepter une nouvelle reservation, le total des personnes de toutes les reservations actives qui chevauchent chaque partie de l'intervalle ne doit jamais depasser 20, ou la capacite configuree.

Les reservations `cancelled`, `completed` et `no_show` ne consomment pas de capacite future. Le statut `seated` continue de compter jusqu'a la fin theorique de son intervalle, sauf decision ulterieure explicite.

### Creation et concurrence

Le serveur revalide les horaires et la capacite au moment de l'enregistrement, meme si le navigateur a deja affiche le creneau comme disponible.

La verification finale et la creation sont realisees dans une transaction. Une ligne de verrouillage unique par restaurant et par date est acquise avec `select_for_update()` avant de recalculer la capacite et d'enregistrer la reservation. PostgreSQL fournit la garantie de concurrence attendue en production. SQLite reste adapte au developpement local, mais son verrouillage global ne constitue pas la preuve de production. Le test de concurrence bloquant est donc execute avec PostgreSQL, en complement des tests fonctionnels executes avec SQLite.

### Modification et annulation

Un client peut modifier la date, l'heure ou le nombre de personnes jusqu'a deux heures avant l'arrivee. Toute modification relance la validation complete des disponibilites.

Une annulation est autorisee jusqu'a deux heures avant l'arrivee. Elle change le statut en `cancelled` et conserve l'historique. Apres la limite, l'interface affiche le telephone du restaurant.

Le personnel autorise peut modifier ou annuler une reservation depuis le tableau de bord en laissant une trace d'audit minimale.

## 6. Notifications

La creation reussie d'une reservation est independante de la livraison des emails.

Apres validation et enregistrement :

- le client voit immediatement une confirmation a l'ecran ;
- un email client contient le recapitulatif et le lien de gestion securise ;
- une notification est envoyee au restaurant ;
- un echec SMTP est journalise sans transformer une reservation confirme en echec apparent ;
- le personnel peut relancer une notification echouee.

Les secrets SMTP, le `SECRET_KEY` et les reglages propres a l'environnement sont charges depuis des variables d'environnement. Le mot de passe d'application Gmail actuellement present dans l'historique doit etre revoque avant toute autre utilisation.

## 7. Experience client

### Accueil

L'accueil presente dans cet ordre :

1. proposition du restaurant et appel principal `Reserver une table` ;
2. etat d'ouverture du jour et prochain service ;
3. selection courte de plats ;
4. promotions actives ;
5. adresse, horaires et acces ;
6. liens sociaux reels uniquement s'ils sont configures.

Les promotions et horaires ne sont plus ecrits directement dans le template.

### Carte

La carte propose une navigation claire par categories, une recherche et un tri par prix. Elle affiche les informations essentielles sans creer un composant modal complet pour chaque plat.

Une fiche plat ou un panneau de detail unique presente la description, les ingredients, les allergenes et les marqueurs alimentaires. Les plats indisponibles peuvent rester visibles avec la mention `Indisponible`, selon un reglage du personnel.

### Reservation

Le parcours comporte trois etapes :

1. date et nombre de personnes ;
2. choix parmi les creneaux reellement disponibles ;
3. coordonnees, commentaire et confirmation.

Les champs requis, erreurs, formats et regles d'annulation sont affiches clairement. Les labels sont explicitement associes aux champs. Le parcours reste utilisable au clavier et sur petit ecran.

### Gestion d'une reservation

Le visiteur utilise le lien securise de son email. Le membre connecte retrouve ses reservations dans son profil. Les deux parcours utilisent les memes services de modification et d'annulation.

## 8. Tableau de bord du personnel

Le tableau de bord contient cinq zones :

- vue du jour : reservations, couverts attendus, annulations et arrivees proches ;
- reservations : filtres par date, statut, nom, email ou telephone, avec actions de statut ;
- carte : categories, plats, ingredients, allergenes, images et disponibilite ;
- horaires et capacite : semaine type, exceptions et parametres de reservation ;
- promotions : creation, modification, activation, desactivation et dates de validite.

Toutes les vues du tableau de bord exigent un utilisateur authentifie et autorise. Les operations sensibles sont effectuees en POST avec protection CSRF. Les suppressions definitives sont reservees aux donnees qui ne possedent pas d'historique metier utile.

## 9. Securite, confidentialite et exploitation

Le premier lot doit :

- revoquer hors du code le mot de passe Gmail compromis ;
- retirer les secrets du code et documenter les variables attendues ;
- separer les reglages de developpement et de production ;
- desactiver `DEBUG` en production ;
- configurer les hotes, HTTPS et cookies securises ;
- ne plus versionner les journaux, bases locales et rapports de couverture ;
- verifier que les journaux ne collectent pas plus de donnees personnelles que necessaire ;
- fournir une politique de confidentialite expliquant l'usage et la conservation des donnees de reservation ;
- definir une politique de conservation ou d'anonymisation des anciennes reservations.

Le nettoyage de fichiers deja suivis ou de l'historique Git fera l'objet d'une operation explicite et reversible autant que possible. Aucun fichier utilisateur ne sera supprime implicitement.

## 10. Erreurs et cas limites

Le systeme doit gerer explicitement :

- date passee ou restaurant ferme ;
- heure en dehors d'un service ;
- nombre de personnes hors limites ;
- creneau devenu complet entre l'affichage et la validation ;
- jeton visiteur invalide, expire ou revoque ;
- tentative de modifier une reservation annulee ou terminee ;
- tentative apres le delai de deux heures ;
- erreur d'envoi d'email ;
- image manquante ;
- suppression d'une categorie ou d'un plat encore reference ;
- intervalles d'ouverture invalides ou chevauchants.

Chaque erreur client doit fournir une explication et, lorsque possible, une action de repli : autre creneau, retour a la carte ou contact telephonique.

## 11. Strategie de migration

Les migrations sont ajoutees par petits lots. Elles doivent preserver les donnees existantes.

Ordre recommande :

1. corriger la divergence de migration existante de `MenuPromotionnel.nom` ;
2. ajouter la configuration du restaurant et les horaires hebdomadaires ;
3. adapter les horaires exceptionnels existants ;
4. ajouter les statuts et champs d'audit de reservation avec valeurs par defaut sures ;
5. generer les jetons des reservations visiteurs qui doivent rester gerables ;
6. ajouter les allergenes et nouveaux champs de plat ;
7. ajouter les periodes et le statut des promotions.

Avant toute migration affectant des donnees existantes, une sauvegarde de la base locale est requise. Les transformations de donnees sont testees sur une copie.

## 12. Strategie de tests

### Tests metier

- generation des creneaux pour un ou plusieurs services ;
- priorite des horaires exceptionnels ;
- exclusion des dates passees et respect du delai minimal ;
- chevauchements a 30, 60 et 90 minutes ;
- capacite exacte, capacite depassee et annulation liberant la capacite ;
- limite de 1 a 8 personnes ;
- modification avec revalidation ;
- cycle complet des statuts ;
- jetons de gestion non devinables et limites a une reservation.

### Tests d'integration

- parcours visiteur complet sans compte ;
- parcours membre et affichage dans le profil ;
- acces du personnel et refus des utilisateurs ordinaires ;
- echec SMTP sans perte ni duplication de reservation ;
- migrations sur un jeu de donnees representatif ;
- concurrence sur le dernier creneau disponible.

### Verification d'interface

- largeurs mobile et bureau ;
- navigation au clavier ;
- labels, erreurs et etats de focus ;
- menu long et plats sans image ;
- tableaux du personnel sur petit ecran ;
- absence de liens sociaux factices et de contenus contradictoires.

Chaque lot doit passer ses tests cibles, l'ensemble de la suite Django, `makemigrations --check --dry-run`, les controles de deploiement applicables et une inspection du diff.

## 13. Lots d'implementation

1. Securiser la configuration et stabiliser le depot.
2. Unifier les informations et horaires du restaurant.
3. Implementer le moteur de disponibilite et de capacite.
4. Implementer le cycle de reservation et l'acces visiteur securise.
5. Rendre les notifications tolerantes aux erreurs.
6. Structurer les allergenes et la presentation de la carte.
7. Reorganiser le tableau de bord du personnel.
8. Refaire progressivement les pages client.
9. Ajouter confidentialite, accessibilite, SEO et configuration de deploiement.

Chaque lot est realise, teste et examine separement. Les decisions qui modifient l'authentification, les modeles ou les migrations restent visibles dans le plan et ne sont pas elargies sans validation.

## 14. Hors perimetre de la premiere version

- commande de repas ;
- panier ;
- livraison ou retrait ;
- paiement en ligne ;
- affectation automatique de tables physiques ;
- application mobile ;
- API publique ;
- architecture React ou microservices ;
- programme de fidelite ;
- synchronisation automatique avec un fournisseur de reservation tiers.

Ces elements pourront etre reexamines seulement apres stabilisation de la reservation de tables.
