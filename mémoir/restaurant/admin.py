

from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Livreur, Livraison, Commande, CommandePlat, Table
)
from .models import Livreur,Livraison, Commande,CommandePlat,Client,Categorie, Plat, PlatIngredient, Table

# Register your models here.
admin.site.register(Livreur),
admin.site.register(Livraison),
admin.site.register(Commande),
admin.site.register(CommandePlat),
admin.site.register(Client),
admin.site.register(Categorie),
admin.site.register(Plat),
admin.site.register(PlatIngredient),
admin.site.register(Table),




