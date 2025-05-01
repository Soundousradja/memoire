from django.contrib import admin
from .models import CustomUser
# Activer la sélection multiple des plats dans l'admin
 # Rend le champ ManyToMany plus ergonomique
admin.site.register(CustomUser),# Register your models here.
