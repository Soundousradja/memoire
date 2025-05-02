from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone




class Admin(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='admin_images/')
    restaurant = models.OneToOneField('Restaurant', on_delete=models.CASCADE)
    
    


    def __str__(self):
        return self.name
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    image = models.ImageField(upload_to='restaurants/')
    
       
    def str(self):
        return self.name    
# Dans models.py - après toutes vos définitions de classes

# Tout d'abord, ajoutez ces imports au début du fichier s'ils n'y sont pas déjà
from django.db.models.signals import post_save
from django.dispatch import receiver


# Ajoutez cette méthode à la classe Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    qte_stock = models.FloatField(default=0)
    qte_total_utilisee = models.FloatField(default=0)

    def __str__(self):
        return self.name
    def update_qte_total_utilisee(self, restaurant=None):
        # Si un restaurant spécifique est fourni, calculer uniquement pour ce restaurant
        total = 0
        plat_ingredients = PlatIngredient.objects.filter(ingredient=self)
        
        for pi in plat_ingredients:
            # Filtrer les historiques par restaurant si spécifié
            historique_query = HistoriquePlat.objects.filter(plat=pi.plat)
            if restaurant:
                historique_query = historique_query.filter(restaurant=restaurant)
            
            if historique_query.exists():
                # Multiplier la quantité par plat par la quantité de plats préparés
                for hist in historique_query:
                    total += pi.quantite_par_plat * hist.quantite
        
        self.qte_total_utilisee = total
        self.save()
        
    
class HistoriqueIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite = models.FloatField()
    date = models.DateField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ('ingredient', 'date' ,'restaurant')  # Un seul enregistrement par ingrédient par jour
    
    def __str__(self):
        return f"{self.ingredient.name} - {self.date} - {self.quantite}"
class Categorie(models.Model):
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='categories/',null=True,blank=True)
    
    def __str__(self):
        return self.name    

class Plat(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='plats/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredient, through='PlatIngredient')  
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    description = models.TextField()
    etape =  models.TextField()
    is_available = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class HistoriquePlat(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    date = models.DateField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ('plat', 'date' ,'restaurant')  # Un seul enregistrement par plat par jour
    
    def __str__(self):
        return f"{self.plat.name} - {self.date} - {self.quantite}" 

@receiver(post_save, sender=HistoriquePlat)
def update_ingredients_totals(sender, instance, **kwargs):
    # Récupérer le plat associé à cet historique
    plat = instance.plat
    
    # Mettre à jour les quantités totales utilisées pour chaque ingrédient de ce plat
    for plat_ingredient in PlatIngredient.objects.filter(plat=plat):
        plat_ingredient.ingredient.update_qte_total_utilisee()
class PlatIngredient(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_par_plat = models.IntegerField()

class PreparationJournaliere(models.Model):
    date = models.DateField(auto_now_add=True)
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('date', 'plat')  # Pour éviter les doublons sur la même date
        
    def __str__(self):
        return f"{self.plat.name} - {self.date} - {self.quantite} unités"
        
# Modèle pour les ingrédients utilisés par jour (facultatif, mais utile)
class UtilisationIngredientJour(models.Model):
    date = models.DateField(auto_now_add=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_utilisee = models.FloatField(default=0)
    
    class Meta:
        unique_together = ('date', 'ingredient')
        
    def __str__(self):
        return f"{self.ingredient.name} - {self.date} - {self.quantite_utilisee}"    
   


