from django.urls import path
from .views import supadmin
from django.urls import path
from .views import gestion_restaurants, ajouter_restaurant
from . import views  # Importation des vues de l'app
from .views import ajouter_admin
from .views import modifier_admin
from .views import menu_view, ajouter_plat, modifier_plat, supprimer_plat



urlpatterns = [
    path('supadmin/', views.supadmin, name='supadmin'),  
    path('restaurants/', views.gestion_restaurants, name='gestion_restaurants'),
    path('gestion_admin/', views.gestion_admin, name='gestion_admin'),
    path("ajouter_restaurant/", views.ajouter_restaurant, name="ajouter_restaurant"),
    path('ajouter_admin/', views.ajouter_admin, name='ajouter_admin'),
    path("modifier_restaurant/<int:id>/", views.modifier_restaurant, name="modifier_restaurant"),
    path('supprimer_restaurant/<int:id>/', views.supprimer_restaurant, name='supprimer_restaurant'),
    path('supprimer_admin/<int:id>/', views.supprimer_admin, name='supprimer_admin'),
    path('modifier_admin/<int:id>/', modifier_admin, name='modifier_admin'),
    path('menuinterface/', views.menu_interface, name='menu_interface'),  
    path('menu/', menu_view, name='menu'),   
  path('categorie/<int:categorie_id>/ajouter-plat/', views.ajouter_plat, name='ajouter_plat'),

    path('menu/<str:categorie>/', views.plats_par_categorie, name='plats_par_categorie'),
    path('categories/', views.categories_view, name='categories'),
    path('pizza/', views.pizza_view, name='pizza'),
    path('dessert/', views.dessert_view, name='dessert'),
    path('boisson/', views.boisson_view, name='boisson'),
    path('category_selection/', views.category_selection, name='category_selection'),
    path("ingredients/ajouter/", views.ajouter_ingredient, name="ajouter_ingredient"),
    path('gestion_ingredients/', views.gestion_ingredient, name='gestion_ingredients'),
    path('ingredient_management/', views.ingredient_management, name='ingredient_management'),
    
    path('categories/', views.category_selection, name='category_selection'),
    path('categorie_plats/<int:categorie_id>/', views.categorie_plats, name='categorie_plats'),  
    path('plat/modifier/<int:plat_id>/', views.modifier_plat, name='modifier_plat'),
    path('plat/supprimer/<int:plat_id>/', views.supprimer_plat, name='supprimer_plat'),
  
    path('categorie_plats/<int:categorie_id>/', views.categorie_plats, name='categorie_plats'),
    path('plat/modifier/<int:plat_id>/', views.modifier_plat, name='modifier_plat'),

   
   
]
   


  
  
   

