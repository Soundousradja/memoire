from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('util',views.utilisateur, name='util'),
    path('client/', views.client_page, name='client_page'),
    
    path('utilisateurs/<str:role>/', views.users_by_role, name='users_by_role'),
     path('ajouter_utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('utilisateur/', views.utilisateurs_par_role, name='utilisateur'),
    path('modifier_utilisateur/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('supprimer_utilisateur/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('offre/', views.offre, name='offre'),
    path('ajouter_offre/', views.ajouter_offre, name='ajouter_offre'),
    path('afficher/', views.afficher, name='afficher'),
     path('supprimer_offre/<int:offre_id>/', views.supprimer_offre, name='supprimer_offre'),
     path('modifier_offre/<int:id>/', views.modifier_offre, name='modifier_offre'),
     
     
    path('access-denied/', views.access_denied, name='access_denied'),
    path('staff-default/', views.staff_default_view, name='staff_default_interface'),
    path('forgot_password/', views.forgot_password_view, name='forgot_password'),


    path('reset-password/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),


    path('login/', views.login_view, name='login'), 
    path('register/client/', views.client_register_view, name='client_register'),


   




]