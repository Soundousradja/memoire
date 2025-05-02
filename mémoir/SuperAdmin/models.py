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


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    qte_stock = models.FloatField(default=0)  # Stock actuel
    qte_total_utilisee = models.FloatField(default=0)  # Quantité totale utilisée


    def __str__(self):
        return self.name
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
class PlatIngredient(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_par_plat = models.IntegerField()

