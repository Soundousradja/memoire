import datetime
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from Menu.models import HistoriqueIngredient, HistoriquePlat
from restaurant.models import Commande
from SuperAdmin.models import PlatIngredient
from SuperAdmin.models import Plat
from SuperAdmin.models import Categorie
from SuperAdmin.models import Ingredient
from restaurant.models import  total_journee
from django.utils.timesince import timesince
from restaurant.models import CommandePlat
from django.shortcuts import render, redirect
from .models import  Restaurant
from datetime import datetime
#from .models import total_paye, total_non_paye

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, date
from django.db.models import Sum
from django.utils.timesince import timesince
from .models import  HistoriquePlat, HistoriqueIngredient
from restaurant.models import Table

@csrf_exempt
def get_plats(request):
    categorie = request.GET.get("categorie", None)
    date_str = request.GET.get("date", None)
    
    # Filtrer par catégorie
    if categorie:
        plats = Plat.objects.filter(categorie__name=categorie)

    else:
        plats = Plat.objects.all()
        
    data = []
    if date_str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        for plat in plats:
            plat_info = {"id": plat.id, "name": plat.name}
            
            # Chercher l'historique pour ce plat à cette date
            try:
                historique = HistoriquePlat.objects.get(plat=plat, date=date_obj)
                plat_info["quantite_historique"] = historique.quantite
            except HistoriquePlat.DoesNotExist:
                plat_info["quantite_historique"] = 0
                
            data.append(plat_info)
    else:
        data = [{"id": plat.id, "name": plat.name} for plat in plats]
    
    return JsonResponse(data, safe=False)


@csrf_exempt
def calculer_ingredients(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plat_id = data.get("plat_id")
            quantite = int(data.get("quantite", 1))
            date_str = data.get("date")

            if not plat_id:
                return JsonResponse({"error": "ID du plat requis"}, status=400)

            plat = Plat.objects.get(id=plat_id)
            ingredients = PlatIngredient.objects.filter(plat=plat)

            resultats = []
            for ing in ingredients:
                # Si une date est spécifiée, vous pourriez vouloir récupérer 
                # la consommation des ingrédients pour cette date spécifique
                if date_str:
                    # Recherche de l'historique de l'ingrédient pour cette date
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        historique = HistoriqueIngredient.objects.get(ingredient=ing.ingredient, date=date_obj)
                        qte_total = ing.quantite_par_plat * quantite
                    except HistoriqueIngredient.DoesNotExist:
                        qte_total = ing.quantite_par_plat * quantite
                else:
                    qte_total = ing.quantite_par_plat * quantite

                resultats.append({
                    "name": ing.ingredient.name,
                    "qteParPlat": ing.quantite_par_plat,
                    "qteTotal": qte_total
                })

            return JsonResponse({"ingredients": resultats})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def categories_view(request):
    categories = Categorie.objects.all()
    return render(request, 'PagesMenu/menu.html', {'categories': categories})



@csrf_exempt
def ajouter_plat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nom_plat = data.get("name")
        ingredients = data.get("ingredients", [])

        if not nom_plat:
            return JsonResponse({"error": "Nom du plat requis"}, status=400)

        plat = Plat.objects.create(nom=nom_plat)

        for ing in ingredients:
            try:
                ingredient_obj = Ingredient.objects.get(nom=ing["name"])
                PlatIngredient.objects.create(plat=plat, ingredient=ingredient_obj, quantite_par_plat=ing["qteParPlat"])
            except Ingredient.DoesNotExist:
                return JsonResponse({"error": f"Ingrédient {ing['name']} non trouvé"}, status=400)

        return JsonResponse({"message": "Plat ajouté avec succès"})

@csrf_exempt
def enregistrer_ingredients(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date_str = data.get("date")
            if date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                date_obj = date.today()
                
            plat_id = data.get("plat_id")
            quantite_plat = int(data.get("quantite_plat", 0))
            
            # Enregistrer l'historique du plat si l'ID est fourni
            if plat_id and quantite_plat > 0:
                try:
                    plat = Plat.objects.get(id=plat_id)
                    historique_plat, created = HistoriquePlat.objects.get_or_create(
                        plat=plat,
                        date=date_obj,
                        defaults={'quantite': 0}
                    )
                    historique_plat.quantite = quantite_plat  # Remplacer la quantité au lieu d'ajouter
                    historique_plat.save()
                except Plat.DoesNotExist:
                    return JsonResponse({"error": f"Plat avec ID {plat_id} non trouvé"}, status=404)
            
            # Enregistrer l'historique des ingrédients
            for item in data.get("ingredients", []):
                try:
                    ingredient = Ingredient.objects.get(name=item["name"])
                    
                    # Mettre à jour la quantité totale utilisée dans le modèle Ingredient
                    qte_total = float(item["qteTotal"])
                    ingredient.qte_total_utilisee = qte_total  # Remplacer au lieu d'ajouter
                    ingredient.save()
                    
                    # Enregistrer dans l'historique des ingrédients
                    historique, created = HistoriqueIngredient.objects.get_or_create(
                        ingredient=ingredient,
                        date=date_obj,
                        defaults={'quantite': 0}
                    )
                    historique.quantite = qte_total  # Remplacer la quantité au lieu d'ajouter
                    historique.save()
                    
                except Ingredient.DoesNotExist:
                    return JsonResponse({"error": f"Ingrédient {item['name']} non trouvé"}, status=404)
                
            return JsonResponse({"message": "Historique des ingrédients et des plats mis à jour avec succès!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def afficher_plats(request):
    from datetime import date
    
    slug = request.GET.get('categorie')  # Ex: "fast-food"
    if slug:
        categorie_name = slug.replace('-', ' ')  # ← déslugifie
    else:
        categorie_name = None
        
    # Passer la date d'aujourd'hui au template
    today_date = date.today().strftime('%Y-%m-%d')
    
    return render(request, 'pagesMenu/GérerPlat.html', {
        'categorie': categorie_name,
        'today_date': today_date
    })

# Autres fonctions de views.py restent inchangées
#Liste Achat
def get_ingredients(request):
    ingredients = Ingredient.objects.all().values('id', 'name', 'qte_total_utilisee')
    return JsonResponse(list(ingredients), safe=False)
def formulaire_ingredients(request):
    return render(request, 'PagesMenu/ListeAchat.html')
#Gérer Commande
def commande(request):
    commandes = Commande.objects.all()
    context = {
        'commandes': commandes,
        'total_journee': total_journee(),
        #'total_paye': total_paye(),
        #'total_non_paye': total_non_paye(),
        
    }
    return render(request, 'PagesMenu/Commande.html', context)
# Chef Cuisinier
def chef(request):
    return render(request,'PagesMenu/Statut_Chef.html')
def Pagechef(request):
    return render(request,'PagesMenu/chef.html')
def liste_commandes(request):
    commandes = Commande.objects.all()
   # data = [{"id": cmd.id, "num_commande": cmd.num_commande, "statut_preparation": cmd.statut_preparation,"temps": timesince(cmd.created_at) + " ago"} for cmd in commandes]
    data = [{"id":cmd.id,"statut_preparation": cmd.statut,"temps": timesince(cmd.created_at) + " ago"} for cmd in commandes]
    return JsonResponse(data, safe=False)
def menu_chef(request):
    categories = Categorie.objects.all()
    return render(request ,'PagesMenu/menuchef.html',{'categories': categories})
def plat_chef(request):
    
    
    slug = request.GET.get('categorie')  # Ex: "fast-food"
    if slug:
        categorie_nom = slug.replace('-', ' ')  # ← déslugifie
    else:
        categorie_nom = None
        
    # Passer la date d'aujourd'hui au template
   
    
    return render(request, 'pagesMenu/plat_chef.html', {
        'categorie': categorie_nom,
       
    })
@csrf_exempt
def update_statut_commande(request, commande_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            commande = Commande.objects.get(id=commande_id)
            
            if "statut" in data:
                commande.statut = data["statut"]
                commande.save()
                return JsonResponse({"message": "Statut mis à jour", "nouveau_statut": commande.statut}, status=200)
            else:
                return JsonResponse({"error": "Champ 'statut_preparation' manquant"}, status=400)

        except Commande.DoesNotExist:
            return JsonResponse({"error": "Commande non trouvée"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
def commande_details(request, id):
    if request.method == "GET":
        try:
            commande = Commande.objects.get(id=id)
            plats = [
                {
                    #"nom": cp.plat.nom,
                    #"quantite": cp.quantite,
                    "nom": cp.plat.name,
                    "quantite": cp.quantity,
                    "prix": cp.plat.price
                }
                for cp in commande.commandeplat_set.all()
            ]
            return JsonResponse({"num_commande": commande.id,"plats": plats})
        except Commande.DoesNotExist:
            return JsonResponse({"error": "Commande introuvable"}, status=404)
def GestionTable(request):
   
      tables = Table.objects.all()
      return render(request, 'pagesMenu/Gestion_Table.html', {'tables': tables})

def ajouter_table(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        capacite = request.POST.get('capacite')
        available = request.POST.get('available_tables')

        try:
            table = Table.objects.create(
                numéro=numero,
                capacité=capacite,
                available_tables=available
            )
            return JsonResponse({
                'success': True,
                'table': {
                    'id': table.id,
                    'numéro': table.numéro,
                    'capacité': table.capacité,
                    'available_tables': table.available_tables
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False})

def supprimer_table(request, table_id):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            table.delete()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})
def modifier_table(request, table_id):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            table.numéro = request.POST.get('numero')
            table.capacité = request.POST.get('capacite')
            table.available_tables = request.POST.get('available_tables')
            table.save()

            return JsonResponse({
                'success': True,
                'table': {
                    'id': table.id,
                    'numéro': table.numéro,
                    'capacité': table.capacité,
                    'available_tables': table.available_tables
                }
            })
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': "Table introuvable."})
from django.contrib.auth.decorators import login_required        
@login_required
def restaurant_admin_dashboard(request, restaurant_id):
    # Vérifier que l'utilisateur est bien admin et qu'il a accès à ce restaurant
    if not request.user.is_staff or request.user.role != 'admin':
        return redirect('access_denied')
    
    if not hasattr(request.user, 'restaurant') or request.user.restaurant.id != restaurant_id:
        return redirect('access_denied')
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Récupérer toutes les données spécifiques à ce restaurant
    categories = Categorie.objects.filter(restaurant=restaurant)
    plats_count = Plat.objects.filter(restaurant=restaurant).count()
    
    # Vous pouvez ajouter d'autres statistiques spécifiques au restaurant ici
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'plats_count': plats_count,
        # Ajoutez d'autres données au contexte selon vos besoins
    }
    
    return render(request, 'PagesMenu/menu.html', context)



 # Pour afficher des messages sur la page

