from django.shortcuts import render
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from .forms import AdminForm 
from .models import Restaurant
from .models import Admin
from django.utils.text import slugify
from .forms import PlatForm

from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import render
from SuperAdmin.models import Plat, Categorie, Ingredient, PlatIngredient
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .forms import RestaurantForm
from .forms import RestaurantForm  

def supadmin(request):
 return render(request, 'app/supadmin.html')


def gestion_restaurants(request): # Restaurant.objects.all() returns a QuerySet containing every restaurant stored in the database.
    restaurants = Restaurant.objects.all()
    return render(request, 'app/gestion_restaurants.html', {'restaurants': restaurants})

def supprimer_restaurant(request, id):
    if request.method == "POST":  # On utilise POST au lieu de DELETE
        restaurant = get_object_or_404(Restaurant, id=id)
        restaurant.delete()
        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False}, status=400)





def ajouter_restaurant(request):
    if request.method == "POST":
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save()
            return JsonResponse({"success": True, "restaurant_id": restaurant.id})
        return JsonResponse({"success": False, "errors": form.errors})

    return render(request, "app/ajouter_restaurant.html")

from django.shortcuts import render, get_object_or_404

def modifier_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)

    if request.method == "POST":
        restaurant.name = request.POST.get("name", restaurant.name)
        restaurant.address = request.POST.get("address", restaurant.address)
        
        if "image" in request.FILES:
            restaurant.image = request.FILES["image"]

        restaurant.save()
        return JsonResponse({"success": True})

    return render(request, "app/modifier_restaurant.html", {"restaurant": restaurant})



def gestion_admin(request): 
    admins = Admin.objects.all()
    return render(request, 'app/gestion_admin.html', {'admins': admins})




from django.http import JsonResponse

def ajouter_admin(request):
    if request.method == "POST":
        form = AdminForm(request.POST, request.FILES)
        if form.is_valid():
            admin = form.save()
            return JsonResponse({"success": True, "admin_id": admin.id})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = AdminForm()
        restaurants = Restaurant.objects.all()
        return render(request, "app/ajouter_admin.html", {
            "form": form,
            "restaurants": restaurants
        })

def supprimer_admin(request, id):
    # Retrieve the admin object to delete
    admin = get_object_or_404(Admin, id=id)

    # Check if the request method is POST
    if request.method == "POST":
        try:
            # Attempt to delete the admin
            admin.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False}, status=400)



def modifier_admin(request, id):
    admin = get_object_or_404(Admin, id=id)

    if request.method == "POST":
        # Update admin details
        admin.name = request.POST.get("name", admin.name)
        admin.phone = request.POST.get("phone", admin.phone)
        
        # Check for new image upload
        if "image" in request.FILES:
            admin.image = request.FILES["image"]

        admin.save()

        # After saving the admin, redirect to the admin list page (this prevents form resubmission)
        return redirect('gestion_admin')  # Redirect to the page that shows the list of admins

    return render(request, "app/modifier_admin.html", {"admin": admin})

def modifier_admin(request, id):
    admin = get_object_or_404(Admin, id=id)
    restaurants = Restaurant.objects.all()  # Fetch all restaurants

    if request.method == "POST":
        form = AdminForm(request.POST, request.FILES, instance=admin)  # Initialize form with instance
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return render(request, "app/modifier_admin.html", {
                "admin": admin,
                "restaurants": restaurants,
                "form": form,
            })
    else:
        form = AdminForm(instance=admin)  # Initialize form for GET request

    return render(request, "app/modifier_admin.html", {
        "admin": admin,
        "restaurants": restaurants,
        "form": form,
    })

def supprimer_restaurant(request, id):
    if request.method == "POST":
        restaurant = get_object_or_404(Restaurant, id=id)
        restaurant.delete()
        return JsonResponse({"success": True})  # ✅ Réponse JSON correcte
    return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=400)

def menu_interface(request):
    return render(request, 'app/menuinterface.html')
 

from .models import Plat, PlatIngredient

def menu_view(request):
    plats = Plat.objects.all()
    plats_data = []

    for plat in plats:
        ingredients_data = []
        for pi in PlatIngredient.objects.filter(plat=plat):
            ingredients_data.append({
                'name': pi.ingredient.name,
                'quantite': pi.quantite_par_plat  # Utilisez ici `quantite_par_plat`
            })

        plats_data.append({
            'id': plat.id,
            'name': plat.name,
            'image': plat.image,
            'price': plat.price,
            'description':plat.description,
            'ingredients': ingredients_data,
            'is_available' : plat.is_available
        })

    return render(request, 'app/menu_management.html', {'plats': plats_data})
from .models import Categorie  # Assure-toi que ce modèle est bien importé

from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import render
from .models import Plat, Ingredient, Categorie, PlatIngredient


from .models import Plat, PlatIngredient

def plats_par_categorie(request, categorie):
    categorie_nom = categorie.replace('-', ' ')  # ← déslugifie
    # Correction ici: utiliser "name" au lieu de "nom"
    plats_queryset = Plat.objects.filter(categorie__name__iexact=categorie_nom)
   
    plats_data = []

    for plat in plats_queryset:
        ingredients_data = []
        for pi in PlatIngredient.objects.filter(plat=plat):
            ingredients_data.append({
                'name': pi.ingredient.name,
                'quantite': pi.quantite_par_plat
            })

        plats_data.append({
            'id': plat.id,
            'name': plat.name,
            'image': plat.image,
            'price': plat.price,
            'description': plat.description,
            'ingredients': ingredients_data,
            'is_available': plat.is_available
        })

    return render(request, 'app/menu_management.html', {
        'plats': plats_data,
        'categorie': categorie
    })

def categories_view(request):
    if request.method == "POST":
        nom = request.POST.get("name")
        image = request.FILES.get("image")

        if nom:
            # Correction: utiliser "name" au lieu de "nom"
            Categorie.objects.create(name=nom, image=image)
            return redirect("category_selection")
    categories = Categorie.objects.all()
    return render(request, 'app/category_selection.html', {'categories': categories})


from django.shortcuts import render, redirect
from .models import Categorie

def category_selection(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')  # récupérer l'image envoyée
        
        if name:
            Categorie.objects.create(name=name, image=image)
        
        return redirect('categories')  # Rediriger pour recharger la page proprement

    # Si GET : juste afficher la liste
    categories = Categorie.objects.all()
    return render(request, 'app/category_selection.html', {
        'categories': categories
    })



    


# Vue pour afficher les plats d'une catégorie dans un restaurant
def categorie_plats(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    # Récupérer les plats de cette catégorie
    plats = Plat.objects.filter(categorie=categorie)
    
    plats_data = []
    for plat in plats:
        ingredients_data = []
        for pi in PlatIngredient.objects.filter(plat=plat):
            ingredients_data.append({
                'name': pi.ingredient.name,
                'quantite': pi.quantite_par_plat
            })
        
        plats_data.append({
            'id': plat.id,
            'name': plat.name,
            'image': plat.image,
            'price': plat.price,
            'description': plat.description,
            'ingredients': ingredients_data,
            'is_available': plat.is_available
        })
    
    return render(request, 'app/category_selection.html', {
        'categorie': categorie,
        'categorie_id': categorie.id,
        'plats': plats_data
    })

# Vue pour modifier un plat
def ajouter_plat(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            etape = request.POST.get('etape')
            price = request.POST.get('price')
            is_available = request.POST.get('is_available') == 'true'
            
            plat = Plat(
                name=name,
                description=description,
                etape=etape,
                price=price,
                is_available=is_available,
                categorie=categorie
            )
            
            if 'image' in request.FILES:
                plat.image = request.FILES['image']
            
            plat.save()
            
            for key in request.POST:
                if key.startswith("ingredients[") and key.endswith("][ingredient]"):
                    index = key.split("[")[1].split("]")[0]
                    ingredient_id = request.POST.get(f"ingredients[{index}][ingredient]")
                    quantity = request.POST.get(f"ingredients[{index}][quantity]")
                    
                    if ingredient_id and quantity:
                        PlatIngredient.objects.create(
                            plat=plat,
                            ingredient_id=int(ingredient_id),
                            quantite_par_plat=int(quantity)
                        )

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('categorie_plats', kwargs={
                    'categorie_id': categorie_id
                })
            })
            
        except Exception as e:
            import traceback
            print(f"Error adding dish: {e}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'errors': {'general': str(e)}})
            
    else:  # GET request
        ingredients = Ingredient.objects.all()
        
        return render(request, 'app/ajouter_plat.html', {
            'ingredients': ingredients,
            'categorie_id': categorie_id,
            'categorie': categorie
        })


def modifier_plat(request, plat_id):
    plat = get_object_or_404(Plat, id=plat_id)
    categorie_id = plat.categorie.id
    
    if request.method == "POST":
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            form.save()
            # Rediriger vers la page des plats de cette catégorie
            return JsonResponse({
    'success': True,
    'redirect_url': reverse('categorie_plats', kwargs={'categorie_id': plat.categorie.id})
})
        else:
            all_ingredients = Ingredient.objects.all()
            return render(request, 'app/modifier_plat.html', {
                'form': form, 
                'plat': plat,
                'all_ingredients': all_ingredients,
                'errors': form.errors
            })
    else:
        form = PlatForm(instance=plat)
        all_ingredients = Ingredient.objects.all()
        return render(request, 'app/modifier_plat.html', {
            'form': form, 
            'plat': plat,
            'all_ingredients': all_ingredients
        })
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def supprimer_plat(request, plat_id):
    if request.method == "POST":
        plat = get_object_or_404(Plat, id=plat_id)
        plat.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


    
from django.http import JsonResponse
from .models import Ingredient

def ajouter_ingredient(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()

        if not nom:
            return JsonResponse({"success": False, "error": "Nom requis."})

        # Empêcher les doublons (optionnel)
        if Ingredient.objects.filter(nom__iexact=nom).exists():
            return JsonResponse({"success": False, "error": "Ingrédient déjà existant."})

        Ingredient.objects.create(nom=nom)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Méthode non autorisée."})
def ajouter_ingredient(request):
 return render(request, 'app/ingredient_management.html')
 
def ajouter_ing(request):
    if request.method == "POST":
        name = request.POST.get("plat_name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        plat = Plat.objects.create(nom=name, prix=price, description=description, image=image)

        for key in request.POST:
            if key.startswith("ingredients[") and key.endswith("][id]"):
                index = key.split("[")[1].split("]")[0]
                ingredient_id = request.POST.get(f"ingredients[{index}][id]")
                quantity = request.POST.get(f"ingredients[{index}][quantity]")

                ingredient = Ingredient.objects.get(id=ingredient_id)
                

        return JsonResponse({"success": True})

    else:
        ingredients = Ingredient.objects.all()
        return render(request, "app/ajouter_plat.html", {"ingredients": ingredients})
def ajouter_plat_complet(request):
    if request.method == "POST":
        # Traitement à ajouter ici
        return JsonResponse({"success": True})
    return render(request, "app/ajouter_plat_complet.html")
def gestion_ingredient(request):
    # Get all ingredients
    ingredients = Ingredient.objects.all()
    
    if request.method == 'POST':
        # Check if it's an AJAX request to add a new ingredient
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            nom = request.POST.get('nom')
            if nom:
                # Create new ingredient
                ingredient = Ingredient.objects.create(nom=nom)
                # Return JSON response with the new ingredient details
                return JsonResponse({
                    'success': True,
                    'id': ingredient.id,
                    'nom': ingredient.nom
                })
            return JsonResponse({'success': False, 'error': 'Le nom de l\'ingrédient est requis'})
    
    # Render the template with all ingredients
    return render(request, 'app/ingredient_management.html', {'ingredients': ingredients})


def ajouter_ingredient(request):
    if request.method == "POST":
        nom = request.POST.get("name")
        if nom:
            ingredient, created = Ingredient.objects.get_or_create(name=nom)
            return JsonResponse({"success": True, "id": ingredient.id, "name": ingredient.name})
        else:
            return JsonResponse({"success": False, "error": "Nom d'ingrédient manquant."})
    return JsonResponse({"success": False, "error": "Méthode non autorisée."})

def gestion_ingredients(request):
    if request.method == 'POST':
        ingredient_name = request.POST.get('name')
        # Effectue des actions avec ingredient_name (par exemple, enregistrer l'ingrédient)
        return JsonResponse({'message': 'Ingrédient ajouté', 'name': ingredient_name})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def ingredient_management(request):
    if request.method == 'POST':
        ingredient_name = request.POST.get('name')
        if ingredient_name:
            # Enregistre l'ingrédient dans la base de données (ou autre logique)
            return JsonResponse({'message': 'Ingrédient ajouté', 'ingredient': ingredient_name})
        return JsonResponse({'error': 'Nom de l\'ingrédient manquant'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
def ingredient_management(request):
    if request.method == 'POST':
        # Récupérer le nom de l'ingrédient envoyé via le formulaire
        ingredient_name = request.POST.get('name', '').strip()

        if ingredient_name:
            # Créer et enregistrer l'ingrédient dans la base de données
            ingredient = Ingredient(name=ingredient_name)
            ingredient.save()

            # Retourner la réponse JSON avec le message et l'ingrédient
            return JsonResponse({
                'message': 'Ingrédient ajouté',
                'ingredient': ingredient.name  # Nom de l'ingrédient ajouté
            })
        else:
            return JsonResponse({'message': 'Nom d\'ingrédient invalide'}, status=400)

    # Si c'est une requête GET, récupérer tous les ingrédients et les passer au template
    ingredients = Ingredient.objects.all()  # Récupérer tous les ingrédients
    return render(request, 'ingredient_management.html', {'ingredients': ingredients})
def pizza_view(request):
    return render(request, 'app/pizza.html')  

def dessert_view(request):
    return render(request, 'app/dessert.html')  

def boisson_view(request):
    return render(request, 'app/boisson.html') 



# Ajoutez ces importations en haut de votre fichier SuperAdmin/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from restaurant.models import Commande
from .models import Restaurant
from home.views import get_restaurant_for_user
from Menu.models import Depense  
from django.http import HttpResponse

from django.shortcuts import render
from django.http import HttpResponse
from Menu.models import Depense
from .models import Restaurant
from restaurant.models import Commande
from datetime import datetime, timedelta
from home.views import get_restaurant_for_user

from django.http import HttpResponse
from datetime import datetime

from decimal import Decimal

def tableau_ventes(request):
    # Récupérer toutes les dépenses sans filtrage
    depenses = Depense.objects.all()
    
    # Calculer le total des dépenses (c'est un Decimal)
    total_depenses = sum(depense.prix for depense in depenses)
    
    # Convertir les valeurs en Decimal pour éviter l'erreur de type
    total_commandes = Decimal('150000.00')  # Utiliser Decimal au lieu de float
    benefice = total_commandes - total_depenses  # Maintenant la soustraction fonctionnera
    
    # HTML avec le design original
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tableau de Ventes</title>
        <style>
            /* Styles généraux */
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #fafafa;
                color: #222;
            }}

            h1, h2 {{
                color: #222;
                border-bottom: 2px solid #FFD700; /* Bordure jaune sous les titres */
                padding-bottom: 10px;
            }}

            /* Boîte de filtres */
            .filter-box {{
                background-color: #222;
                color: #fff;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}

            .filter-box label {{
                margin-right: 10px;
                font-weight: bold;
                color: #FFD700; /* Labels en jaune */
            }}

            .filter-box select, .filter-box input {{
                padding: 8px 12px;
                margin-right: 15px;
                border: 2px solid #FFD700;
                border-radius: 4px;
                background-color: #fff;
                color: #222;
            }}

            .filter-box button {{
                padding: 8px 20px;
                background-color: #FFD700; /* Bouton jaune */
                color: #222;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }}

            .filter-box button:hover {{
                background-color: #F5CC00; /* Jaune légèrement plus foncé au survol */
                transform: translateY(-2px);
            }}

            /* Cartes de résumé */
            .summary {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}

            .card {{
                flex: 1;
                min-width: 250px;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                text-align: center;
                background-color: #fff;
                border-top: 4px solid #FFD700;
                transition: transform 0.3s ease;
            }}

            .card:hover {{
                transform: translateY(-5px);
            }}

            .card h3 {{
                margin-top: 0;
                color: #222;
                font-size: 16px;
            }}

            .card p {{
                font-size: 28px;
                font-weight: bold;
                margin: 10px 0;
            }}

            /* Tableau des dépenses */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                background-color: #fff;
            }}

            th, td {{
                padding: 12px 15px;
                text-align: left;
            }}

            th {{
                background-color: #222;
                color: #FFD700;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 14px;
            }}

            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            tr:hover {{
                background-color: #fff9e0; /* Légère teinte jaune au survol */
            }}

            /* Couleurs pour les montants */
            .montant {{
                color: #222;
            }}

            .depense {{
                color: #222;
            }}

            .benefice {{
                color: #FFD700;
                font-weight: bold;
            }}

            /* Message "aucune dépense" */
            .no-data {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-style: italic;
            }}

            /* Responsive design */
            @media (max-width: 768px) {{
                .summary {{
                    flex-direction: column;
                }}
                
                .filter-box {{
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                
                .filter-box select, .filter-box input {{
                    width: 100%;
                    margin-right: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Tableau de Ventes</h1>
        
        <div class="filter-box">
            <form method="get">
                <label for="restaurant">Restaurant:</label>
                <select name="restaurant" id="restaurant">
                    <option value="1">The LFS Spot Constantine</option>
                    <option value="2" selected>The LFS Spot Alger</option>
                    <option value="3">The LFS Spot Oran</option>
                </select>
                
                <label for="date_debut">Du:</label>
                <input type="date" name="date_debut" id="date_debut" value="2025-04-01">
                
                <label for="date_fin">Au:</label>
                <input type="date" name="date_fin" id="date_fin" value="2025-05-02">
                
                <button type="submit">Filtrer</button>
            </form>
        </div>
        
        <div class="summary">
            <div class="card">
                <h3>Montant Total (DA)</h3>
                <p class="montant">{total_commandes} DA</p>
            </div>
            <div class="card">
                <h3>Total Dépenses (DA)</h3>
                <p class="depense">{total_depenses} DA</p>
            </div>
            <div class="card">
                <h3>Bénéfice Net (DA)</h3>
                <p class="benefice">{benefice} DA</p>
            </div>
        </div>
        
        <h2>Liste des Dépenses (Toutes)</h2>
        
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Produit</th>
                    <th>Prix (DA)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Si aucune dépense n'est trouvée
    if not depenses:
        html += '<tr><td colspan="3" class="no-data">Aucune dépense trouvée</td></tr>'
    else:
        # Ajouter chaque dépense au tableau
        for dep in depenses:
            try:
                # Formater la date au format JJ/MM/AAAA
                formatted_date = dep.date.strftime('%d/%m/%Y')
            except:
                # En cas d'erreur, utiliser la date brute
                formatted_date = str(dep.date)
                
            html += f"""
            <tr>
                <td>{formatted_date}</td>
                <td>{dep.produit}</td>
                <td>{dep.prix} DA</td>
            </tr>
            """
    
    # Fermer le HTML
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return HttpResponse(html)

    
 
@login_required
def get_donnees_ventes(request):
    """
    API pour récupérer les données de ventes et dépenses
    """
    restaurant_id = request.GET.get('restaurant')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Valider les paramètres
    if not restaurant_id:
        return JsonResponse({'error': 'Restaurant non spécifié'}, status=400)
    
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant introuvable'}, status=404)
    
    # Filtres de base pour les requêtes
    depenses_filter = {'restaurant': restaurant}
    commandes_filter = {'restaurant': restaurant}
    
    # Ajouter les filtres de date si fournis
    if date_debut:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            depenses_filter['date__gte'] = date_debut_obj
            commandes_filter['created_at__date__gte'] = date_debut_obj
        except ValueError:
            return JsonResponse({'error': 'Format de date invalide'}, status=400)
    
    if date_fin:
        try:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            depenses_filter['date__lte'] = date_fin_obj
            commandes_filter['created_at__date__lte'] = date_fin_obj
        except ValueError:
            return JsonResponse({'error': 'Format de date invalide'}, status=400)
    
    # Récupérer les dépenses et commandes
    depenses = Depense.objects.all()
    commandes = Commande.objects.filter(**commandes_filter)
    
    # Calculer les montants
    total_depenses = sum(depense.prix for depense in depenses)
    
    # Calculer le total des commandes
    # Assurez-vous que cette méthode existe dans votre modèle Commande
    try:
        total_commandes = sum(commande.calculer_prix_total() for commande in commandes)
    except AttributeError:
        # Alternative si la méthode n'existe pas
        total_commandes = sum(commande.prix_total for commande in commandes if hasattr(commande, 'prix_total'))
    
    # Profit = Montant - Dépenses
    profit = total_commandes - total_depenses
    
    # Préparer les données des dépenses pour l'affichage
    depenses_data = []
    for depense in depenses:
        depenses_data.append({
            'id': depense.id,
            'produit': depense.produit,
            'prix': float(depense.prix),
            'date': depense.date.strftime('%Y-%m-%d')
        })
    
    # Retourner toutes les données
    return JsonResponse({
        'montant': float(total_commandes),
        'depense': float(total_depenses),
        'retenu': float(profit),
        'depenses': depenses_data
    })