from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from SuperAdmin.models import Categorie,Ingredient,Plat,PlatIngredient
from django.utils import timezone
from django.utils.timesince import timesince
from SuperAdmin.models import Restaurant
from home.models import CustomUser
from mémoir import settings

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# class Client(AbstractUser):
#     phone = models.CharField(max_length=15, unique=True)
#     address = models.TextField()
   
#     groups = models.ManyToManyField(
#         'auth.Group', 
#         related_name='client_set',  
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission', 
#         related_name='client_permissions', 
#         blank=True
#     )




    
class Table(models.Model):
    numéro = models.PositiveIntegerField(unique=True)  
    capacité = models.PositiveIntegerField() 
    available_tables = models.PositiveIntegerField(default=1)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"Table {self.numéro} (Capacité: {self.capacité})"
    


class Reservation(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    guests = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
   
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.client.username} - Table {self.table.numéro} - {self.date} {self.time}"


class Commande(models.Model):
    

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    STATUT_PAIEMENT = [
        ('Paye', 'Payé'),
        ('Non Paye', 'Non Payé'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de préparation'),
         ('En cours de préparation', 'En cours de préparation'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('Prête', 'Prête'),
    ]
    STATUT_PREPARATION = [
        ('En cours de préparation', 'En cours de préparation'),
        ('Prête', 'Prête'),
    ]
    statut = models.CharField(max_length=25, choices=STATUT_CHOICES, default='en_attente')
    #statut_preparation = models.CharField(max_length=25, choices=STATUT_PREPARATION, default='En cours de préparation')
    
    MODE_PAIEMENT_CHOICES = [
        ('cash', 'Paiement à la livraison'),
        ('carte', 'Carte bancaire'),
        ('sur_place', 'Sur place')
    ]
    #paiement = models.CharField(max_length=10, choices=STATUT_PAIEMENT, default='Non Paye')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='cash')
    created_at = models.DateTimeField(default=timezone.now)

    plats = models.ManyToManyField(Plat, through="CommandePlat")
    def calculer_prix_total(self):
        return sum(cp.plat.price * cp.quantity for cp in self.commandeplat_set.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Sauvegarde la commande

   
def total_journee():
    total = sum(commande.calculer_prix_total() for commande in Commande.objects.all())
    return total

      
class CommandePlat(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)  
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"{self.quantity} x {self.plat.name} (Commande {self.commande.id})"
class Evaluation(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='evaluation')
    note = models.IntegerField(choices=[(1, '1 étoile'), (2, '2 étoiles'), (3, '3 étoiles'), 
                                       (4, '4 étoiles'), (5, '5 étoiles')])
    commentaire = models.TextField(blank=True, null=True)
    date_evaluation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Évaluation de la commande {self.commande.id}: {self.note} étoiles"    
    
from django.db import models
from django.utils import timezone
from django.conf import settings

class Livreur(models.Model):
    id_livr = models.AutoField(primary_key=True)
    nom_livr = models.CharField(max_length=100)
    statut_dispo = models.BooleanField(default=True)
    statut_disponibilité = models.CharField(max_length=20, choices=[
        ('disponible', 'Disponible'),
        ('indisponible', 'Indisponible'),
    ], default='disponible')
   
    def __str__(self):
        return f"{self.nom_livr} (ID: {self.id_livr})"
    
    def is_available(self):
        return self.statut_dispo and self.statut_disponibilité == 'disponible'
    
    def set_disponible(self, disponible=True):
        self.statut_disponibilité = 'disponible' if disponible else 'indisponible'
        self.statut_dispo = disponible
        self.save()
    
    def assign_delivery(self, commande):
        """Assigne une commande à ce livreur"""
        if not self.is_available():
            return False
        
        # Crée une nouvelle livraison
        livraison = Livraison(
            id_livr=self,
            id_cmd=commande,
            etat_livraison='en_cours',
            adresse=commande.adresse,
            date=timezone.now()
        )
        livraison.save()
        
        # Met à jour le statut de la commande
        commande.statut = 'en_cours'
        commande.save()
        
        return True


class Livraison(models.Model):
    ETAT_CHOICES = [
        ('attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('probleme', 'Problème'),
    ]
    
    id_livr = models.ForeignKey(Livreur, on_delete=models.CASCADE)
    id_cmd = models.ForeignKey('Commande', on_delete=models.CASCADE, default=1)  # Use a valid ID
    etat_livraison = models.CharField(max_length=20, choices=ETAT_CHOICES, default='attente')
    adresse = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Livraison {self.id} - Commande {self.id_cmd.id}"
    
    def mark_as_delivered(self):
        """Marque la livraison comme livrée"""
        self.etat_livraison = 'livree'
        self.save()
        
        # Met à jour aussi le statut de la commande
        commande = self.id_cmd
        commande.statut = 'livree'
        commande.save()
        
        # Rend le livreur à nouveau disponible
        livreur = self.id_livr
        livreur.set_disponible(True)
        livreur.save()