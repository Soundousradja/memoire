from django.core.management.base import BaseCommand
from Menu.models import PlatIngredient, Ingredient
from datetime import datetime, timedelta
from django.db import models

class Command(BaseCommand):
    help = "Mise à jour quotidienne de la quantité totale utilisée des ingrédients"

    def handle(self, *args, **kwargs):
        # Réinitialiser les quantités utilisées à 0
        Ingredient.objects.update(qte_total_utilisee=0)

        total_qte_utilisee = Ingredient.objects.aggregate(total=models.Sum("qte_total_utilisee"))["total"] or 0

        self.stdout.write(self.style.SUCCESS(f"✅ Mise à jour effectuée ! Total utilisé : {total_qte_utilisee}"))

