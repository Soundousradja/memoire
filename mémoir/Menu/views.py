import datetime
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from SuperAdmin.models import HistoriqueIngredient, HistoriquePlat
from restaurant.models import Commande
from SuperAdmin.models import Admin, PlatIngredient
from SuperAdmin.models import Plat
from SuperAdmin.models import Categorie
from SuperAdmin.models import Ingredient
from restaurant.models import  total_journee
from django.utils.timesince import timesince
from restaurant.models import CommandePlat
from django.shortcuts import render, redirect
from .models import  Depense
from datetime import datetime
from SuperAdmin.models import Restaurant

from django.contrib.auth import logout
#from .models import total_paye, total_non_paye

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, date
from django.db.models import Sum
from django.utils.timesince import timesince

from restaurant.models import Table

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from datetime import datetime, date
from home.views import get_restaurant_for_user

# 🔵 Utilitaire pour récupérer le restaurant lié à l'utilisateur


# ✅ Get plats filtrés par restaurant
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, date

import json
from django.utils.timesince import timesince

# ✅ Afficher les plats, éventuellement par catégorie
@csrf_exempt
@login_required
def get_plats(request):
    categorie = request.GET.get("categorie")
    date_str = request.GET.get("date")

    plats = Plat.objects.all()
    if categorie:
        plats = plats.filter(categorie__name=categorie)

    data = []
    if date_str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        restaurant = get_restaurant_for_user(request.user)
        if not restaurant:
            return JsonResponse({"error": "Aucun restaurant associé à cet utilisateur."}, status=403)

        for plat in plats:
            plat_info = {"id": plat.id, "name": plat.name}
            try:
                historique = HistoriquePlat.objects.get(plat=plat, restaurant=restaurant, date=date_obj)
                plat_info["quantite_historique"] = historique.quantite
            except HistoriquePlat.DoesNotExist:
                plat_info["quantite_historique"] = 0
            data.append(plat_info)
    else:
        data = [{"id": plat.id, "name": plat.name} for plat in plats]

    return JsonResponse(data, safe=False)

# ✅ Calculer les ingrédients nécessaires pour un plat
@csrf_exempt
@login_required
def calculer_ingredients(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plat_id = data.get("plat_id")
            quantite = int(data.get("quantite", 1))
            date_str = data.get("date")
            
            if not date_str:
                date_obj = date.today()
            else:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            if not plat_id:
                return JsonResponse({"error": "ID du plat requis"}, status=400)

            # Récupérer le restaurant de l'utilisateur
            restaurant = get_restaurant_for_user(request.user)
            if not restaurant:
                return JsonResponse({"error": "Aucun restaurant associé à cet utilisateur."}, status=403)

            plat = Plat.objects.get(id=plat_id)
            ingredients = PlatIngredient.objects.filter(plat=plat)

            resultats = []
            for ing in ingredients:
                # Calcul par défaut
                qte_par_plat = ing.quantite_par_plat
                qte_total = qte_par_plat * quantite
                
                # Vérifier s'il existe une entrée historique pour cet ingrédient ce jour-là
                try:
                    historique = HistoriqueIngredient.objects.get(
                        ingredient=ing.ingredient,
                        date=date_obj,
                        restaurant=restaurant
                    )
                    # Si l'historique existe, utiliser sa valeur à la place
                    qte_total = historique.quantite
                except HistoriqueIngredient.DoesNotExist:
                    # Pas d'historique, on garde la valeur calculée
                    pass
                
                resultats.append({
                    "name": ing.ingredient.name,
                    "qteParPlat": qte_par_plat,
                    "qteTotal": qte_total
                })

            return JsonResponse({"ingredients": resultats})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
# ✅ Afficher toutes les catégories (globales)
@login_required
def categories_view(request):
    categories = Categorie.objects.all()
    return render(request, 'PagesMenu/menu.html', {'categories': categories})

# ✅ Ajouter un plat
@csrf_exempt
@login_required
def ajouter_plat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nom_plat = data.get("name")
        ingredients = data.get("ingredients", [])

        if not nom_plat:
            return JsonResponse({"error": "Nom du plat requis"}, status=400)

        plat = Plat.objects.create(name=nom_plat)

        for ing in ingredients:
            try:
                ingredient_obj = Ingredient.objects.get(name=ing["name"])
                PlatIngredient.objects.create(plat=plat, ingredient=ingredient_obj, quantite_par_plat=ing["qteParPlat"])
            except Ingredient.DoesNotExist:
                return JsonResponse({"error": f"Ingrédient {ing['name']} non trouvé"}, status=400)

        return JsonResponse({"message": "Plat ajouté avec succès"})

# ✅ Enregistrer historique des plats et ingrédients pour un restaurant donné
@csrf_exempt
@login_required
def enregistrer_ingredients(request):
    if request.method == "POST":
        try:
            restaurant = get_restaurant_for_user(request.user)
            if not restaurant:
                return JsonResponse({"error": "Aucun restaurant associé."}, status=403)

            data = json.loads(request.body)
            date_str = data.get("date")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

            plat_id = data.get("plat_id")
            quantite_plat = int(data.get("quantite_plat", 0))

            if plat_id and quantite_plat > 0:
                plat = Plat.objects.get(id=plat_id)
                historique_plat, _ = HistoriquePlat.objects.get_or_create(
                    plat=plat, restaurant=restaurant, date=date_obj,
                    defaults={'quantite': 0}
                )
                historique_plat.quantite = quantite_plat
                historique_plat.save()
                
                # Mettre à jour les quantités totales utilisées pour chaque ingrédient de ce plat
                for plat_ingredient in PlatIngredient.objects.filter(plat=plat):
                    plat_ingredient.ingredient.update_qte_total_utilisee()
            
            # Le reste de votre code existant pour les ingrédients individuels...
            for item in data.get("ingredients", []):
                ingredient = Ingredient.objects.get(name=item["name"])
                qte_total = float(item["qteTotal"])

                historique_ing, _ = HistoriqueIngredient.objects.get_or_create(
                    ingredient=ingredient, restaurant=restaurant, date=date_obj,
                    defaults={'quantite': 0}
                )
                historique_ing.quantite = qte_total
                historique_ing.save()

            return JsonResponse({"message": "Historique enregistré avec succès."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
# ✅ Gérer Plat page
@login_required
def afficher_plats(request):
    slug = request.GET.get('categorie')
    categorie_name = slug.replace('-', ' ') if slug else None
    today_date = date.today().strftime('%Y-%m-%d')
    return render(request, 'pagesMenu/GérerPlat.html', {'categorie': categorie_name, 'today_date': today_date})

# ✅ Liste ingrédients
@login_required
def get_ingredients(request):
    # Récupérer le restaurant associé à l'utilisateur connecté
    restaurant = get_restaurant_for_user(request.user)
    if not restaurant:
        return JsonResponse({"error": "Aucun restaurant associé à cet utilisateur."}, status=403)
    
    # Récupérer tous les ingrédients
    ingredients = Ingredient.objects.all()
    
    # Préparer les données avec les quantités spécifiques au restaurant
    data = []
    for ingredient in ingredients:
        ingredient_info = {
            'id': ingredient.id,
            'name': ingredient.name,
            'qte_total_utilisee': 0  # Valeur par défaut
        }
        
        # Calculer la quantité totale utilisée pour cet ingrédient dans ce restaurant
        # en utilisant les historiques
        try:
            # Obtenir tous les plats utilisant cet ingrédient
            plat_ingredients = PlatIngredient.objects.filter(ingredient=ingredient)
            total_quantite = 0
            
            for pi in plat_ingredients:
                # Pour chaque relation, récupérer l'historique du plat spécifique à ce restaurant
                historiques = HistoriquePlat.objects.filter(plat=pi.plat, restaurant=restaurant)
                
                for hist in historiques:
                    total_quantite += pi.quantite_par_plat * hist.quantite
                    
            ingredient_info['qte_total_utilisee'] = total_quantite
        except Exception:
            pass  # En cas d'erreur, garde la valeur par défaut
            
        data.append(ingredient_info)
    
    return JsonResponse(data, safe=False)


# ✅ Formulaire ingrédients
@login_required
def formulaire_ingredients(request):
    return render(request, 'PagesMenu/ListeAchat.html')

# ✅ Gestion commandes


# ✅ Statut Chef
@login_required
def chef(request):
    return render(request, 'PagesMenu/Statut_Chef.html')

# ✅ Page Chef
@login_required
def Pagechef(request):
    return render(request, 'PagesMenu/chef.html')

# ✅ Liste commandes
@login_required
def liste_commandes(request):
    restaurant = get_restaurant_for_user(request.user)
    commandes = Commande.objects.filter(restaurant=restaurant)
    data = [{"id": cmd.id, "statut_preparation": cmd.statut, "temps": timesince(cmd.created_at) + " ago"} for cmd in commandes]
    return JsonResponse(data, safe=False)

# ✅ Menu chef
@login_required
def menu_chef(request):
    categories = Categorie.objects.all()
    return render(request, 'PagesMenu/menuchef.html', {'categories': categories})

# ✅ Page Plat chef
@login_required
def plat_chef(request):
    slug = request.GET.get('categorie')
    categorie_nom = slug.replace('-', ' ') if slug else None
    
    # Récupérer la catégorie par son nom
    try:
        if categorie_nom:
            categorie = Categorie.objects.get(name=categorie_nom)
            # Récupérer tous les plats de cette catégorie
            plats = Plat.objects.filter(categorie=categorie)
        else:
            plats = []
    except Categorie.DoesNotExist:
        plats = []
    
    return render(request, 'pagesMenu/plat_chef.html', {
        'categorie': categorie_nom,
        'plats': plats
    })
# ✅ Update statut commande
@csrf_exempt
@login_required
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
                return JsonResponse({"error": "Champ 'statut' manquant"}, status=400)
        except Commande.DoesNotExist:
            return JsonResponse({"error": "Commande non trouvée"}, status=404)

# ✅ Détail commande
@login_required
def commande_details(request, id):
    try:
        commande = Commande.objects.get(id=id)
        plats = [{"nom": cp.plat.name, "quantite": cp.quantity, "prix": cp.plat.price} for cp in commande.commandeplat_set.all()]
        return JsonResponse({"num_commande": commande.id, "plats": plats})
    except Commande.DoesNotExist:
        return JsonResponse({"error": "Commande introuvable"}, status=404)

# ✅ Gestion des tables
@login_required
def GestionTable(request):
    restaurant = get_restaurant_for_user(request.user)  # Récupérer le restaurant de l'utilisateur
    if not restaurant:
        return JsonResponse({'error': 'Aucun restaurant associé à cet utilisateur.'}, status=403)

    tables = Table.objects.filter(restaurant=restaurant)  # Récupérer les tables pour ce restaurant
    return render(request, 'pagesMenu/Gestion_Table.html', {'tables': tables})


# ✅ Ajouter table
@csrf_exempt
@login_required
def ajouter_table(request):
    if request.method == "POST":
        restaurant = get_restaurant_for_user(request.user)
        if not restaurant:
            return JsonResponse({"success": False, "error": "Aucun restaurant associé à cet utilisateur."}, status=403)

        try:
            numero = request.POST.get("numero")
            capacite = request.POST.get("capacite")
            available = request.POST.get("available_tables")
            
            # Vérifier que tous les champs sont fournis
            if not (numero and capacite and available):
                return JsonResponse({"success": False, "error": "Tous les champs sont obligatoires."}, status=400)

            # Utilise les noms de champs tels qu'ils sont définis dans le modèle (avec accents)
            table = Table.objects.create(
                numéro=numero,
                capacité=capacite,
                available_tables=available,
                restaurant=restaurant
            )

            return JsonResponse({
                "success": True,
                "message": "Table ajoutée avec succès.",
                "table": {
                    "id": table.id,
                    "numéro": table.numéro,
                    "capacité": table.capacité,
                    "available_tables": table.available_tables,
                    "restaurant_id": restaurant.id,
                }
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

@csrf_exempt
@login_required
def modifier_table(request, table_id):
    if request.method == 'POST':
        table = Table.objects.get(id=table_id)
        table.numéro = request.POST.get('numero')
        table.capacité = request.POST.get('capacite')
        table.available_tables = request.POST.get('available_tables')

        restaurant_id = request.POST.get('restaurant_id')
        if restaurant_id:
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
                table.restaurant = restaurant
            except Restaurant.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Restaurant not found'})

        table.save()
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'numéro': table.numéro,
                'capacité': table.capacité,
                'available_tables': table.available_tables,
                'restaurant_id': table.restaurant.id,
            }
        })
    return JsonResponse({'success': False})

# ✅ Supprimer table
@csrf_exempt
@login_required
def supprimer_table(request, table_id):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            # Vérifier si l'utilisateur est autorisé à supprimer la table (facultatif)
            if table.restaurant != get_restaurant_for_user(request.user):
                return JsonResponse({'success': False, 'error': 'Vous n\'êtes pas autorisé à supprimer cette table.'})

            table.delete()
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Table non trouvée'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
def logout_view(request):
    # Stocker le chemin actuel avant la déconnexion
    current_url = request.META.get('HTTP_REFERER', '')
    
    # Déconnecter l'utilisateur
    logout(request)
    
    # Rediriger vers la même page
    if current_url:
        return redirect(current_url)
    else:
        return redirect('menu:Gestiontable')  
  
@login_required
def commande_et_depenses(request):
    restaurant = get_restaurant_for_user(request.user)
    if not restaurant:
        return JsonResponse({'error': 'Aucun restaurant associé à cet utilisateur.'}, status=403)

    success = False
    erreur = None

    # Traitement formulaire dépenses
    if request.method == 'POST':
        produit = request.POST.get('produit')
        prix = request.POST.get('prix')
        date_str = request.POST.get('date')

        if not produit or not prix:
            erreur = "Veuillez remplir tous les champs."
        else:
            try:
                prix = Decimal(prix)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

                Depense.objects.create(
                    produit=produit,
                    prix=prix,
                    date=date_obj,
                    restaurant=restaurant
                )
                success = True
            except ValueError:
                erreur = "Format de prix invalide. Utilisez un nombre décimal."

    commandes = Commande.objects.filter(restaurant=restaurant)
    depenses = Depense.objects.filter(restaurant=restaurant).order_by('-date')
    total = sum(depense.prix for depense in depenses)

    context = {
        'commandes': commandes,
        'total_journee': total_journee(),
        'depenses': depenses,
        'total': total,
        'success': success,
        'erreur': erreur,
    }

    return render(request, 'PagesMenu/Commande.html', context)

# Fonction à ajouter dans views.py
@csrf_exempt
@login_required
def enregistrer_tous_plats(request):
    if request.method == "POST":
        try:
            restaurant = get_restaurant_for_user(request.user)
            if not restaurant:
                return JsonResponse({"success": False, "error": "Aucun restaurant associé."}, status=403)

            data = json.loads(request.body)
            date_str = data.get("date")
            plats = data.get("plats", [])
            
            if not date_str or not plats:
                return JsonResponse({"success": False, "error": "Date ou plats manquants."}, status=400)
                
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Enregistrer chaque plat dans l'historique
            for plat_data in plats:
                plat_id = plat_data.get("id")
                quantite = int(plat_data.get("quantite", 0))
                
                if plat_id and quantite > 0:
                    try:
                        plat = Plat.objects.get(id=plat_id)
                        # Créer ou mettre à jour l'historique du plat
                        historique_plat, created = HistoriquePlat.objects.update_or_create(
                            plat=plat,
                            restaurant=restaurant,
                            date=date_obj,
                            defaults={'quantite': quantite}
                        )
                        
                        # Pour chaque ingrédient du plat, mettre à jour l'historique
                        # uniquement si aucun historique n'existe déjà
                        plat_ingredients = PlatIngredient.objects.filter(plat=plat)
                        for pi in plat_ingredients:
                            # Vérifier si un historique existe déjà pour cet ingrédient ce jour-là
                            ing_history_exists = HistoriqueIngredient.objects.filter(
                                ingredient=pi.ingredient,
                                restaurant=restaurant,
                                date=date_obj
                            ).exists()
                            
                            # Seulement créer l'historique si aucun n'existe
                            if not ing_history_exists:
                                qte_total = pi.quantite_par_plat * quantite
                                HistoriqueIngredient.objects.create(
                                    ingredient=pi.ingredient,
                                    restaurant=restaurant,
                                    date=date_obj,
                                    quantite=qte_total
                                )
                        
                        # Mettre à jour les quantités totales utilisées pour chaque ingrédient
                        for pi in plat_ingredients:
                            pi.ingredient.update_qte_total_utilisee()
                            
                    except Plat.DoesNotExist:
                        continue  # Passer au plat suivant si celui-ci n'existe pas
            
            return JsonResponse({"success": True, "message": "Toutes les quantités ont été enregistrées avec succès."})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
            
    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)