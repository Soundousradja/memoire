from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
# Modèle pour les ingrédients
from django.db import models
from SuperAdmin.models import Plat ,Ingredient,PlatIngredient
from SuperAdmin.models import Restaurant






   

# Fonction pour calculer le total des commandes de la journée


# Fonction pour calculer les totaux payés et non payés
#def total_paye():
    #return sum(commande.calculer_prix_total() for commande in Commande.objects.filter(paiement='Paye'))

#def total_non_paye():
   # return sum(commande.calculer_prix_total() for commande in Commande.objects.filter(paiement='Non Paye'))

# Fonction pour calculer le total des dépenses
# def total_depenses():
#     return sum(depense.prix for depense in Depense.objects.all())
# Ajoutez ces classes à votre fichier models.py

class HistoriqueIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite = models.FloatField()
    date = models.DateField()
    
    class Meta:
        unique_together = ('ingredient', 'date')  # Un seul enregistrement par ingrédient par jour
    
    def __str__(self):
        return f"{self.ingredient.name} - {self.date} - {self.quantite}"

class HistoriquePlat(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    date = models.DateField()
    
    class Meta:
        unique_together = ('plat', 'date')  # Un seul enregistrement par plat par jour
    
    def __str__(self):
        return f"{self.plat.name} - {self.date} - {self.quantite}"
# class Depense(models.Model):
#     produit = models.CharField(max_length=100)
#     prix = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField(default=timezone.now)
#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.produit } ({self.restaurant})"   

