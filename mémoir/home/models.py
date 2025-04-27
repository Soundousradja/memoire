from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db import models
from SuperAdmin.models import Restaurant


from django.contrib.auth.hashers import make_password


class UserRole(models.TextChoices):
    CLIENT = 'client', 'Client'
    SERVEUR = 'serveur', 'Serveur'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(
        max_length=100,
        choices=[('client', 'Client'), ('serveur', 'Serveur'), ('chef', 'Chef'), ('livreur', 'Livreur'),('fournisseur', 'Fournisseur'),('superadmin', 'Super Admin'),
        ('admin', 'Admin')],
        default='client'
    )
    mot_de_passe_clair = models.CharField(max_length=128, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)  # Champ adresse
    telephone = models.CharField(max_length=15, blank=True, null=True)  # Champ téléphone
    

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    def save(self, *args, **kwargs):
        if not self.pk and not self.password.startswith('pbkdf2_sha256$'):  # Avoid double hashing
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def str(self):
        return self.username
class Offre(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('expiré', 'Expiré')
    ]
    image = models.ImageField(upload_to='offres/', null=True, blank=True)
    Nom_Offre = models.CharField(max_length=50)
    Date_Debut = models.DateField()
    Date_Fin = models.DateField ()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, editable=False)  # Désactive la modification manuelle
    def mettre_a_jour_statut(self):
        """ Met à jour le statut en fonction des dates """
        today = now().date()

        if self.Date_Fin <= today:
            self.statut = 'expiré'
        else:
            self.statut = 'active'  # Actif si la date de début est arrivée ou est dans le futur

    def save(self, *args, **kwargs):
        """ Met à jour automatiquement le statut avant de sauvegarder """
        self.mettre_a_jour_statut()
        super().save(*args, **kwargs)
