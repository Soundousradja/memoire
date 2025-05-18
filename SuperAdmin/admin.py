from django.contrib import admin
from .models import Categorie, Plat, PlatIngredient,Admin,Restaurant

admin.site.register(Categorie),
admin.site.register(Plat),
admin.site.register(PlatIngredient),
admin.site.register(Admin),
admin.site.register(Restaurant),