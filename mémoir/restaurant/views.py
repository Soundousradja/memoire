from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect,get_object_or_404


from SuperAdmin.models import HistoriquePlat

from django.contrib.auth import logout


from home.models import Offre
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import render
from .models import Categorie, Evaluation, Plat
from .models import Reservation, Table,Commande,CommandePlat
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from SuperAdmin.models import Restaurant
from datetime import date 

#Acceuil
def acceuil(request):
    return render(request,'acceuil.html')

#Menu

def menu_view(request):
    # Récupérer tous les restaurants
    restaurants = Restaurant.objects.all()
    
    # Récupérer l'ID du restaurant sélectionné
    restaurant_id = request.GET.get('restaurant')
    
    # Pour tous les restaurants, afficher toutes les catégories et tous les plats
    # indépendamment du restaurant sélectionné
    if restaurant_id:
        # Récupérer toutes les catégories disponibles
        categories = Categorie.objects.all()
        
        # Récupérer tous les plats disponibles
        plats = Plat.objects.filter(is_available=True)
        
        # Filtrer par catégorie si spécifiée
        categorie_id = request.GET.get('categorie')
        if categorie_id:
            plats = plats.filter(categorie_id=categorie_id)
    else:
        # Si aucun restaurant n'est sélectionné, afficher toutes les catégories et aucun plat
        categories = Categorie.objects.all()
        plats = Plat.objects.none()

    return render(request, 'menu.html', {
        'restaurants': restaurants,
        'categories': categories,
        'plats': plats,
    })

#Réservation


@login_required(login_url='/login')
def réservation(request):
    reservation_success = None
    reservation_error = None
    user = request.user

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        telephone = request.POST.get("phone")
        guests = int(request.POST.get("guests"))
        date = request.POST.get("date")
        time = request.POST.get("time")
        restaurant_id = request.POST.get("restaurant_id")

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)

            # Vérifier si le téléphone de l'utilisateur est enregistré (dans modèle personnalisé)
            if hasattr(user, 'telephone') and not user.telephone:
                user.telephone = telephone
                user.save()

            # Rechercher les tables disponibles dans le restaurant sélectionné
            tables_disponibles = Table.objects.filter(
                capacité__gte=guests,
                restaurant=restaurant
            ).order_by('capacité')

            if not tables_disponibles:
                reservation_error = f"Aucune table disponible pour {guests} personnes dans ce restaurant."
                return render(request, 'table.html', {
                    'reservation_error': reservation_error,
                    'user_name': user.username,
                    'user_email': user.email,
                    'user_phone': getattr(user, 'telephone', ''),
                    'restaurants': Restaurant.objects.all()
                })

            # Tables déjà réservées à cette date et heure
            tables_reservees = Reservation.objects.filter(
                date=date,
                time=time,
                statut__in=['en_attente', 'acceptee']
            ).values_list('table_id', flat=True)

            table = tables_disponibles.exclude(id__in=tables_reservees).first()
            if not table:
                reservation_error = "Toutes les tables appropriées sont déjà réservées à cette heure."
                return render(request, 'table.html', {
                    'reservation_error': reservation_error,
                    'user_name': user.username,
                    'user_email': user.email,
                    'user_phone': getattr(user, 'telephone', ''),
                    'restaurants': Restaurant.objects.all()
                })

            # Créer la réservation
            reservation = Reservation.objects.create(
                client=user,
                table=table,
                restaurant=restaurant,
                guests=guests,
                date=date,
                time=time,

            )

            reservation_success = f"Réservation réussie ! Table {table.numéro} (capacité : {table.capacité} personnes)"
            return render(request, 'table.html', {
                'reservation_success': reservation_success,
                'user_name': user.username,
                'user_email': user.email,
                'user_phone': getattr(user, 'telephone', ''),
                'restaurants': Restaurant.objects.all()
            })

        except Restaurant.DoesNotExist:
            reservation_error = "Restaurant sélectionné invalide."
        except Exception as e:
            reservation_error = f"Erreur lors de la réservation : {str(e)}"

        return render(request, 'table.html', {
            'reservation_error': reservation_error,
            'user_name': user.username,
            'user_email': user.email,
            'user_phone': getattr(user, 'telephone', ''),
            'restaurants': Restaurant.objects.all()
        })

    # GET request : afficher formulaire
    return render(request, 'table.html', {
        'user_name': user.username,
        'user_email': user.email,
        'user_phone': getattr(user, 'telephone', ''),
        'restaurants': Restaurant.objects.all()
    })

#panier

def ajouter_au_panier(request, plat_id):
    """ Ajoute un plat au panier stocké dans la session Django """
    plat = get_object_or_404(Plat, id=plat_id)
    
    # Récupérer ou initialiser le panier dans la session
    panier = request.session.get("panier", {})
    
    if str(plat_id) in panier:
        panier[str(plat_id)]['quantity'] += 1
    else:
        panier[str(plat_id)] = {
            "name": plat.name,
            "price": float(plat.price),
            "quantity": 1
        }
    
    request.session["panier"] = panier
    request.session.modified = True
    
    return JsonResponse({"message": "Plat ajouté au panier."})
 

def voir_panier(request):
    """ Affiche le contenu du panier """
    panier = request.session.get("panier", {})
    
    # Récupérer les détails complets des plats pour l'affichage
    items_panier = []
    total = 0
    
    for plat_id, item_info in panier.items():
        try:
            plat = Plat.objects.get(id=int(plat_id))
            quantite = item_info['quantity']
            prix_total = item_info['price'] * quantite
            total += prix_total
            
            items_panier.append({
                'plat': plat,
                'quantity': quantite,
                'prix_total': prix_total
            })
        except Plat.DoesNotExist:
            # Gérer le cas où le plat n'existe plus
            pass
    
    restaurants = Restaurant.objects.all()
    
  
    
    return render(request, "panier.html", {
        "panier": items_panier,
        "total": total,
        "restaurants": restaurants
    })

def supprimer_du_panier(request, plat_id):
    """ Supprime un plat du panier """
    panier = request.session.get("panier", {})
    
    if str(plat_id) in panier:
        del panier[str(plat_id)]
        request.session["panier"] = panier
        request.session.modified = True
    
    return redirect("voir_panier")

def modifier_panier(request, plat_id, quantity):
    """Modifie la quantité d'un plat dans le panier"""
    panier = request.session.get("panier", {})
    
    if str(plat_id) in panier:
        panier[str(plat_id)]['quantity'] = quantity
        request.session["panier"] = panier
        request.session.modified = True
        
    return JsonResponse({"success": True})



@login_required
@csrf_exempt
def passer_commande(request):
    if request.method == 'POST':
        user = request.user

        if not user.is_authenticated or user.role != 'client':
            return JsonResponse({"error": "Utilisateur non autorisé", "success": False}, status=403)

        telephone = user.telephone
        adresse = user.adresse

        if not telephone or not adresse:
            return JsonResponse({"error": "Adresse ou téléphone manquant dans le profil utilisateur", "success": False}, status=400)

        try:
            data = json.loads(request.body)
            plats_commandes = data.get("plats", [])

            if not plats_commandes:
                return JsonResponse({"error": "Aucun plat sélectionné", "success": False}, status=400)

            # Récupération de l'ID du restaurant et du mode de paiement
            restaurant_id = data.get('restaurant')
            mode_paiement = data.get('mode_paiement')

            if not restaurant_id or not mode_paiement:
                return JsonResponse({"error": "Restaurant ou mode de paiement manquant", "success": False}, status=400)

            # Récupérer l'objet restaurant
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Restaurant.DoesNotExist:
                return JsonResponse({"error": "Restaurant introuvable", "success": False}, status=400)

            # Création de la commande
            commande = Commande.objects.create(
                client=user,
                restaurant=restaurant,  # Utilise 'restaurant' au lieu de 'restaurant_id'
                mode_paiement=mode_paiement,
                adresse=adresse,
                telephone=telephone
            )

            for plat_info in plats_commandes:
                plat_id = plat_info.get("id")
                quantite = plat_info.get("quantite", 1)

                try:
                    plat = Plat.objects.get(id=plat_id)
                    commande.plats.add(plat, through_defaults={'quantity': quantite})
                except Plat.DoesNotExist:
                    return JsonResponse({"error": f"Plat avec l'ID {plat_id} introuvable", "success": False}, status=400)

            return JsonResponse({"message": "Commande passée avec succès", "success": True}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON invalide", "success": False}, status=400)

    return JsonResponse({"error": "Méthode non autorisée", "success": False}, status=405)

#offre


def afficher_offres(request):
    # Récupérer uniquement les offres actives
    offres_actives = Offre.objects.filter(statut='active')
    
    # Pour s'assurer que les statuts sont à jour avant l'affichage
    for offre in offres_actives:
        offre.mettre_a_jour_statut()
        offre.save()
    
    # Récupérer à nouveau les offres actives après mise à jour
    offres_actives = Offre.objects.filter(statut='active')
    
    return render(request, 'offres.html', {'offres': offres_actives})

#Serveur

def serveur_interface(request):
    return render(request,'serveuracceuil.html')

def serveurmenu(request):
    categories = Categorie.objects.all()
    plats=Plat.objects.all()
    tables = Table.objects.all()
    return render(request, 'serveurmenu.html', {
        'categories': categories,
        'tables': tables,
        'plats' :plats
    })

def serveur_reservations(request):
    """Vue pour afficher la liste des réservations au serveur"""
    
    # Récupérer toutes les tables pour le filtre
    tables = Table.objects.all()
    
    # Filtrer les réservations selon les paramètres
    reservations = Reservation.objects.all().order_by('-date', '-time')
    
    # Filtrer par date si spécifiée
    date_filter = request.GET.get('date')
    if date_filter:
        reservations = reservations.filter(date=date_filter)
    
    # Filtrer par statut si spécifié
    statut_filter = request.GET.get('statut')
    if statut_filter:
        reservations = reservations.filter(statut=statut_filter)
    
    # Filtrer par table si spécifiée
    table_filter = request.GET.get('table')
    if table_filter:
        reservations = reservations.filter(table_id=table_filter)
    
    # Par défaut, afficher les réservations d'aujourd'hui et futures
    if not date_filter:
        from django.utils import timezone
        today = timezone.now().date()
        reservations = reservations.filter(date__gte=today)
    
    return render(request, 'réservation.html', {
        'reservations': reservations,
        'tables': tables,
    })

def repondre_reservation(request, reservation_id, reponse):
    """Vue pour accepter ou refuser une réservation"""
    if request.method == "POST":
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        # Vérifier que la réservation est bien en attente
        if reservation.statut != 'en_attente':
            messages.error(request, "Cette réservation a déjà été traitée.")
            return redirect('serveur_reservations')
        
        # Mettre à jour le statut
        if reponse == 'acceptee':
            reservation.statut = 'acceptee'
            messages.success(request, f"La réservation de {reservation.client.username} a été acceptée.")
        elif reponse == 'refusee':
            reservation.statut = 'refusee'
            messages.success(request, f"La réservation de {reservation.client.username} a été refusée.")
        else:
            messages.error(request, "Action non reconnue.")
            return redirect('serveur_reservations')
        
        reservation.save()
    
    return redirect('serveur_reservations')


@login_required
def historique_commandes(request):
    # Récupérer le client associé à l'utilisateur connecté
    try:
        client = request.user
        commandes = Commande.objects.filter(client=client).order_by('-date')
        
        # Préparer les données détaillées des commandes
        commandes_details = []
        for commande in commandes:
            plats_commande = CommandePlat.objects.filter(commande=commande)
            
            # Calculer le total de la commande
            total = 0
            plats_details = []
            
            for item in plats_commande:
                prix_total_item = item.plat.price * item.quantity
                total += prix_total_item
                
                plats_details.append({
                    'nom': item.plat.name,
                    'prix_unitaire': item.plat.price,
                    'quantite': item.quantity,
                    'prix_total': prix_total_item
                })
            
            try:
                evaluation = Evaluation.objects.get(commande=commande)
            except Evaluation.DoesNotExist:
                evaluation = None
            
            commandes_details.append({
                'commande': commande,
                'plats': plats_details,
                'total': total,
                'evaluation': evaluation
            })
        
        return render(request, 'historique.html', {
            'commandes_details': commandes_details
        })
        
    except client.DoesNotExist:
        return render(request, 'historique.html', {
            'message': 'Aucun profil client associé à votre compte utilisateur.'
        })
    
    # Si une erreur se produit, retourner le template avec un message approprié
    except Exception as e:
        return render(request, 'historique.html', {
            'message': f'Une erreur s\'est produite: {str(e)}'
        })

@csrf_exempt
@login_required
def serveur_envoyer_commande(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_id = data.get('table_id')
            restaurant_id = data.get('restaurant_id')  # Nouveau champ dans la requête
            plats = data.get('plats')
            
            print("Données reçues:", data)
            
            if not table_id or not plats or not restaurant_id:
                return JsonResponse({"error": "Informations incomplètes (table_id, restaurant_id et plats requis)"}, status=400)
            
            # Convertir les IDs en entiers si ce sont des chaînes
            if isinstance(table_id, str):
                table_id = int(table_id)
            if isinstance(restaurant_id, str):
                restaurant_id = int(restaurant_id)
                    
            try:
                table = Table.objects.get(id=table_id)
            except Table.DoesNotExist:
                return JsonResponse({"error": f"Table avec ID {table_id} introuvable"}, status=400)
                
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Restaurant.DoesNotExist:
                return JsonResponse({"error": f"Restaurant avec ID {restaurant_id} introuvable"}, status=400)
            
            # Vérifier si la table appartient au restaurant (si relation existante)
            if hasattr(table, 'restaurant') and table.restaurant and table.restaurant.id != restaurant.id:
                return JsonResponse({"error": f"La table {table_id} n'appartient pas au restaurant {restaurant_id}"}, status=400)
            
            commande = Commande.objects.create(
                client=None,
                adresse="Sur place",
                telephone="",
                restaurant=restaurant,
                statut='en_attente',
                mode_paiement='sur_place',
                table=table
            )
            
            # Reste du code inchangé pour traiter les plats...
            
            return JsonResponse({
                "success": True,
                "commande_id": commande.id,
                "message": "Commande passée avec succès!"
            })
                
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def verifier_reservation(request):
    """Vue permettant aux clients de vérifier l'état de leur réservation"""
    reservation_details = None
    message = None
    
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        date = request.POST.get("date")
        
        if not (name and phone and date):
            message = "Veuillez remplir tous les champs."
        else:
            try:
                # Chercher le client par téléphone et nom
                clients = Client.objects.filter(phone=phone, username__icontains=name)
                
                if not clients.exists():
                    message = "Aucun client trouvé avec ce nom et ce numéro de téléphone."
                else:
                    # Chercher les réservations de ces clients à cette date
                    reservations = Reservation.objects.filter(
                        client__in=clients,
                        date=date
                    ).order_by('-created_at')
                    
                    if reservations:
                        reservation_details = reservations
                    else:
                        message = "Aucune réservation trouvée pour ce nom, ce numéro et cette date."
            except Exception as e:
                message = f"Une erreur s'est produite: {str(e)}"
    
    return render(request, 'verifier_reservation.html', {
        'reservation_details': reservation_details,
        'message': message
    })
@csrf_exempt
def evaluer_commande(request, commande_id):
    """Vue pour permettre aux clients d'évaluer une commande livrée"""
    if request.method == "POST":
        try:
            commande = get_object_or_404(Commande, id=commande_id)
            
            # Vérifier que la commande est bien livrée
            if commande.statut != 'livree':
                messages.error(request, "Vous ne pouvez évaluer que les commandes livrées.")
                return redirect('historique_commandes')
            
            # Récupérer les données du formulaire
            note = int(request.POST.get('note', 5))  # Par défaut 5 étoiles
            commentaire = request.POST.get('commentaire', '')
            
            # Vérifier si une évaluation existe déjà pour cette commande
            try:
                evaluation = commande.evaluation
                evaluation.note = note
                evaluation.commentaire = commentaire
                evaluation.save()
                messages.success(request, "Votre évaluation a été mise à jour!")
            except Evaluation.DoesNotExist:
                # Créer une nouvelle évaluation
                Evaluation.objects.create(
                    commande=commande,
                    note=note,
                    commentaire=commentaire
                )
                messages.success(request, "Merci pour votre évaluation!")
            
            # Rediriger vers la page d'historique avec le téléphone en paramètre
            telephone = request.GET.get('telephone', '')
            if telephone:
                return redirect(f'/restaurant/historique/?telephone={telephone}')
            return redirect('historique_commandes')
            
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
            return redirect('historique_commandes')
    
    # Si la méthode n'est pas POST, rediriger vers l'historique
    return redirect('historique_commandes')


@login_required
def profile_view(request):
    return render(request, 'profile.html')

def logout_view(request):
    logout(request)
    return redirect('acceuil')

def logout_serveur(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')

      
        user.username = username
        user.email = email
        user.adresse = adresse
        user.telephone = telephone

        user.save()  

        return redirect('profile')  

    return render(request, 'profile.html', {'user': user})