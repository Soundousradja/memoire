from django.urls import path
from . import views

urlpatterns = [
    path('', views.acceuil, name='acceuil'),
    path('M', views.menu_view, name='menu'),
    
    path('R', views.réservation, name='réservation'),
    path('passer-commande/', views.passer_commande, name='passer_commande'),
    path('panier/', views.voir_panier, name='voir_panier'),
    path('ajouter-au-panier/<int:plat_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('supprimer-du-panier/<int:plat_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('modifier-panier/<int:plat_id>/<int:quantity>/', views.modifier_panier, name='modifier_panier'),
    path('offres/', views.afficher_offres, name='afficher_offres'),
    path('serveur', views.serveuracceuil, name='serveuracceuil'),
    path('serveurmenu', views.serveurmenu, name='serveurmenu'),
    path('serveur/reservations/', views.serveur_reservations, name='serveur_reservations'),
    path('serveur/reservations/<int:reservation_id>/<str:reponse>/', views.repondre_reservation, name='repondre_reservation'),
    path('historique/', views.historique_commandes, name='historique_commandes'),
    path('serveur/envoyer-commande/', views.serveur_envoyer_commande, name='serveur_envoyer_commande'),
     
    path('verifier-reservation/', views.verifier_reservation, name='verifier_reservation'),
    path('restaurant/evaluer/<int:commande_id>/', views.evaluer_commande, name='evaluer_commande'),
    
     path('interface-livreur/', views.interface_livreur, name='interface_livreur'),
    
    # APIs pour les commandes et livraisons
    path('landing_page', views.landing_page, name='landing'),
    path('api/commandes/', views.get_commandes, name='get_commandes'),
    path('api/livreur/disponibilite/', views.update_livreur_disponibilite, name='update_livreur_disponibilite'),
    path('api/livraison/accepter/', views.accept_delivery, name='accept_delivery'),
    path('api/livraison/livrer/', views.mark_as_delivered, name='mark_as_delivered'),
    path('api/livraison/refuser/', views.refuse_delivery, name='refuse_delivery'),


]
   

