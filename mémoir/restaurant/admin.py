from django.contrib import admin
from .models import Commande,Table,Reservation
# Register your models here.
admin.site.register(Commande),
admin.site.register(Table),
admin.site.register(Reservation)
