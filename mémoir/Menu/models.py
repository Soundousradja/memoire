from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
# Modèle pour les ingrédients
from django.db import models

from SuperAdmin.models import Restaurant

   # return sum(commande.calculer_prix_total() for commande in Commande.objects.filter(paiement='Non Paye'))

# Fonction pour calculer le total des dépenses
def total_depenses():
    return sum(depense.prix for depense in Depense.objects.all())
# Ajoutez ces classes à votre fichier models.py


    
class Depense(models.Model):
     produit = models.CharField(max_length=100)
     prix = models.DecimalField(max_digits=10, decimal_places=2)
     date = models.DateField(default=timezone.now)
     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

     def __str__(self):
         return f"{self.produit } ({self.restaurant})"   

