from django.urls import path
from . import views

urlpatterns = [
    path('passer-commande/', views.passer_commande, name='passer_commande'),
    path('', views.acceuil, name='acceuil'),
    path('M', views.menu_view, name='menu'),
    
    path('R', views.réservation, name='réservation'),

    path('panier/', views.voir_panier, name='voir_panier'),
    path('ajouter-au-panier/<int:plat_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('supprimer-du-panier/<int:plat_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('modifier-panier/<int:plat_id>/<int:quantity>/', views.modifier_panier, name='modifier_panier'),
    path('offres/', views.afficher_offres, name='afficher_offres'),
    path('serveur/', views.serveur_interface, name='serveur_interface'),
    path('serveurmenu', views.serveurmenu, name='serveurmenu'),
    path('serveur/reservations/', views.serveur_reservations, name='serveur_reservations'),
    path('serveur/reservations/<int:reservation_id>/<str:reponse>/', views.repondre_reservation, name='repondre_reservation'),
    path('historique/', views.historique_commandes, name='historique_commandes'),
    path('serveur/envoyer-commande/', views.serveur_envoyer_commande, name='serveur_envoyer_commande'),
     
    path('verifier-reservation/', views.verifier_reservation, name='verifier_reservation'),
    path('restaurant/evaluer/<int:commande_id>/', views.evaluer_commande, name='evaluer_commande'),
    path('profile/', views.profile_view, name='profile'),
     path('logout/', views.logout_view, name='logout'),
     path('logout1/', views.logout_serveur, name='logout1'),
]
