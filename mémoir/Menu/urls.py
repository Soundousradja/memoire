from django.urls import path
from . import views
app_name = 'menu'
urlpatterns = [
    path('',views.categories_view, name='menu_Journalier'),
    path('liste/', views.get_plats),
   
    path('api/calculer-ingredients/', views.calculer_ingredients),
    path('api/ajouter-plat/', views.ajouter_plat),
    path('api/enregistrer-ingredients/', views.enregistrer_ingredients, name="enregistrer_ingredients"),
    path('plats/', views.afficher_plats, name='afficher_plats'),
    #Achat
    path('get-ingredients/', views.get_ingredients, name='get_ingredients'),
    path('formulaire/', views.formulaire_ingredients, name='Liste_Achat'),
    #Gérer Commande
     path('commande/', views.commande, name='commande'),
     #chef
     path('chef/',views.chef,name='chef'),
     path('PageChef/',views.Pagechef,name='pagechef'),
     path('menuchef/',views.menu_chef,name='menuchef'),
     path('plat_chef/',views.plat_chef,name='platchef'),
     path('commandes/liste/', views.liste_commandes, name='liste_commandes'),
     path('commandes/update-statut/<int:commande_id>/', views.update_statut_commande, name='update_statut_commande'),
    path("commande-details/<int:id>/", views.commande_details),
    path("table",views.GestionTable, name='Gestiontable'),
    path('tables/ajouter/', views.ajouter_table, name='ajouter_table'),
    path('tables/modifier/<int:table_id>/', views.modifier_table, name='modifier_table'),
    path('tables/supprimer/<int:table_id>/', views.supprimer_table, name='supprimer_table'),
    path('logout/', views.logout_view, name='logout'),
    
    
    path('depenses/',views.depenses, name='depenses'),

   
]