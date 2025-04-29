from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from SuperAdmin.models import Categorie,Ingredient,Plat,PlatIngredient
from django.utils import timezone
from django.utils.timesince import timesince
from SuperAdmin.models import Restaurant


class Client(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='client_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='client_permissions', 
        blank=True
    )

    def __str__(self):
        return self.username
    
class Table(models.Model):
    numéro = models.PositiveIntegerField(unique=True)  
    capacité = models.PositiveIntegerField() 
    available_tables = models.PositiveIntegerField(default=1)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"Table {self.numéro} (Capacité: {self.capacité})"
    


class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    guests = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
   
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.client.username} - Table {self.table.numéro} - {self.date} {self.time}"


class Commande(models.Model):
    
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)
    restaurant = models.CharField(max_length=100)
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
    ]
    #paiement = models.CharField(max_length=10, choices=STATUT_PAIEMENT, default='Non Paye')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='cash')
    created_at = models.DateTimeField(default=timezone.now)

    plats = models.ManyToManyField(Plat, through="CommandePlat")
    def calculer_prix_total(self):
        return sum(cp.plat.price * cp.quantity for cp in self.commandeplat_set.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Sauvegarde la commande

    def __str__(self):
     if self.client:
        return f"Commande {self.id} - {self.client.username}"
     return f"Commande {self.id} - Client inconnu"
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
    
