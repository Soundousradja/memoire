from django.utils import timezone
from home.models import Offre

def mettre_a_jour_toutes_les_offres():
    today = timezone.now().date()
    offres = Offre.objects.all()
    
    for offre in offres:
        if offre.Date_Fin <= today:
            offre.statut = "expiré"
            print(f"{offre.Nom_Offre} expire")
        else:
            offre.statut = "active"
            print(f"{offre.Nom_Offre} est active")
        
        offre.save()

    print("Statuts mis à jour avec succès.")
