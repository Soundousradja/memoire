from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect,get_object_or_404


from SuperAdmin.models import HistoriquePlat

from django.contrib.auth import logout
from django.db import transaction

from home.models import Offre
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import render

from home.views import get_restaurant_for_user
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
    today = date.today()
    restaurants = Restaurant.objects.all()
    restaurant_id = request.GET.get('restaurant')

    categories = Categorie.objects.all()
    plats = Plat.objects.none()

    if restaurant_id:
        categorie_id = request.GET.get('categorie')

        # Filtrer HistoriquePlat pour aujourd'hui, le restaurant sélectionné et quantité > 0
        historique_qs = HistoriquePlat.objects.filter(
            date=today,
            quantite__gt=0,
            restaurant_id=restaurant_id
        )

        # Optionnel : filtrer par catégorie si précisée
        if categorie_id:
            historique_qs = historique_qs.filter(plat__categorie_id=categorie_id)

        # Obtenir les plats correspondants
        plats = Plat.objects.filter(
            id__in=historique_qs.values_list('plat_id', flat=True),
            is_available=True
        )

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
            # Utiliser une transaction pour garantir la cohérence des données
            with transaction.atomic():
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

                # Vérifier la disponibilité des plats avant de créer la commande
                today = date.today()
                for plat_info in plats_commandes:
                    plat_id = plat_info.get("id")
                    quantite_demandee = plat_info.get("quantite", 1)

                    try:
                        plat = Plat.objects.get(id=plat_id)
                        # Vérifier la quantité disponible dans l'historique
                        try:
                            historique = HistoriquePlat.objects.get(
                                plat=plat,
                                date=today,
                                restaurant=restaurant
                            )
                            if historique.quantite < quantite_demandee:
                                return JsonResponse({
                                    "error": f"Quantité insuffisante pour {plat.name}. Disponible: {historique.quantite}, Demandée: {quantite_demandee}",
                                    "success": False
                                }, status=400)
                        except HistoriquePlat.DoesNotExist:
                            return JsonResponse({
                                "error": f"Plat {plat.name} non disponible aujourd'hui dans ce restaurant",
                                "success": False
                            }, status=400)
                    except Plat.DoesNotExist:
                        return JsonResponse({"error": f"Plat avec l'ID {plat_id} introuvable", "success": False}, status=400)

                # Création de la commande
                commande = Commande.objects.create(
                    client=user,
                    restaurant=restaurant,
                    mode_paiement=mode_paiement,
                    adresse=adresse,
                    telephone=telephone
                )

                # Ajouter les plats à la commande et décrémenter les quantités
                for plat_info in plats_commandes:
                    plat_id = plat_info.get("id")
                    quantite_commandee = plat_info.get("quantite", 1)

                    plat = Plat.objects.get(id=plat_id)
                    commande.plats.add(plat, through_defaults={'quantity': quantite_commandee})

                    # Décrémenter la quantité dans HistoriquePlat
                    historique = HistoriquePlat.objects.get(
                        plat=plat,
                        date=today,
                        restaurant=restaurant
                    )
                    historique.quantite -= quantite_commandee
                    historique.save()

                return JsonResponse({"message": "Commande passée avec succès", "success": True}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON invalide", "success": False}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erreur lors du traitement de la commande: {str(e)}", "success": False}, status=500)

    return JsonResponse({"error": "Méthode non autorisée", "success": False}, status=405)
#offre


def afficher_offres(request):
   
    offres_actives = Offre.objects.filter(statut='active')
    
   
    for offre in offres_actives:
        offre.mettre_a_jour_statut()
        offre.save()
    
   
    offres_actives = Offre.objects.filter(statut='active')
    
    return render(request, 'offres.html', {'offres': offres_actives})

#Serveur

@login_required
def serveur_interface(request):
    utilisateur = request.user
    name=utilisateur.username
    if hasattr(utilisateur, 'restaurant'):
        adresse = utilisateur.restaurant.address
       
    else:
        adresse = "Aucun restaurant associé"

    return render(request, 'serveuracceuil.html', {
        'adresse_restaurant': adresse ,
        'serveur_restaurant':name
        })

def serveurmenu(request):
    serveur = request.user
    restaurant = serveur.restaurant
    
    categories = Categorie.objects.all()
    plats = Plat.objects.all()
    
    tables = Table.objects.filter(restaurant=restaurant)
    
    return render(request, 'serveurmenu.html', {
        'categories': categories,
        'tables': tables,
        'plats': plats
    })

def serveur_reservations(request):

    
    serveur = request.user
    restaurant = serveur.restaurant
    tables = Table.objects.filter(restaurant=restaurant)
    
    reservation=Reservation.objects.filter(restaurant=restaurant)
    reservations = reservation.order_by('-date', '-time')
    
  
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
        
        
        if reservation.statut != 'en_attente':
            messages.error(request, "Cette réservation a déjà été traitée.")
            return redirect('serveur_reservations')
        
       
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
    serveur = request.user

    # Vérifie que le serveur est lié à un restaurant
    if not hasattr(serveur, 'restaurant'):
        return JsonResponse({'error': 'Aucun restaurant lié au serveur.'}, status=400)

    restaurant = serveur.restaurant

    if request.method == "GET":
        
        tables = Table.objects.filter(restaurant=restaurant)
        data = []
        for table in tables:
            data.append({
                'id': table.id,
                'numero': table.numéro,
                'capacite': table.capacité,
            })
        return JsonResponse({'tables': data})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            table_id = data.get("table_id")
            plats = data.get("plats")

            if not table_id or not plats:
                return JsonResponse({'error': 'Données manquantes'}, status=400)

            # Vérifie que la table appartient au restaurant du serveur
            try:
                table = Table.objects.get(id=table_id, restaurant=restaurant)
            except Table.DoesNotExist:
                return JsonResponse({'error': 'Table non trouvée pour ce restaurant.'}, status=404)

            # Crée la commande
            commande = Commande.objects.create(
                table=table,
                restaurant=restaurant

                )

            for plat_data in plats:
                plat_id = plat_data.get("id")
                quantite = plat_data.get("quantite", 1)

                try:
                    plat = Plat.objects.get(id=plat_id)
                    CommandePlat.objects.create(commande=commande, plat=plat, quantity=quantite)
                except Plat.DoesNotExist:
                    continue

            return JsonResponse({'success': True, 'commande_id': commande.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)

    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



def verifier_reservation(request):
    """Vue permettant aux clients de vérifier l'état de leur réservation"""
    reservation_details = None
    message = None
    
    if request.user.is_authenticated:
       
        try:
            
            reservations = Reservation.objects.filter(
                client=request.user
            ).order_by('-created_at')
            
            
            if reservations:
                reservation_details = reservations
            else:
                message = "Vous n'avez aucune réservation."
        except Exception as e:
            message = f"Une erreur s'est produite: {str(e)}"
    else:
        message = "Veuillez vous connecter pour voir vos réservations."
    
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
    
    # Si la méthode n'est pas POST, rediriger vers l'
    # 
    # historique
    return redirect('historique_commandes')


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Livreur, Livraison, Commande
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json


    
def landing_page(request):
    return render(request, 'landing_page.html')


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
@login_required
def interface_livreur(request):
    if not request.user.is_authenticated or request.user.role != 'livreur':
        return redirect('access_denied')
        
    # Récupérer les informations du livreur connecté
    livreur_user = request.user
    restaurant = livreur_user.restaurant
    restaurant_name = restaurant.name if restaurant else "Non assigné"
    
    # Récupérer ou créer l'objet Livreur correspondant
    try:
        livreur = Livreur.objects.get(id_livr=livreur_user.id)
    except Livreur.DoesNotExist:
        livreur = Livreur.objects.create(
            id_livr=livreur_user.id,
            nom_livr=f"{livreur_user.first_name} {livreur_user.last_name}" if livreur_user.first_name else livreur_user.username,
            statut_dispo=True
        )
    
    context = {
        'livreur': livreur,
        'livreur_name': f"{livreur_user.first_name} {livreur_user.last_name}" if livreur_user.first_name else livreur_user.username,
        'livreur_id': livreur_user.id,
        'restaurant': restaurant,
        'restaurant_name': restaurant_name
    }
    
    return render(request, 'interface_livreur.html', context)

@login_required
def get_commandes(request):
    livreur_id = request.GET.get('livreur_id')
    status_filter = request.GET.get('status', 'all')

    # Obtenir le restaurant lié à l'utilisateur connecté
    restaurant = get_restaurant_for_user(request.user)
    if not restaurant:
        return JsonResponse({'error': 'Aucun restaurant associé.'}, status=403)

    # Commandes prêtes à livrer (non assignées), pour ce restaurant uniquement
    commandes_pretes = Commande.objects.filter(statut='Prête', restaurant=restaurant)

    # Commandes déjà assignées au livreur dans ce restaurant
    mes_livraisons = []
    if livreur_id:
        mes_livraisons = Livraison.objects.filter(
            id_livr_id=livreur_id,
            id_cmd__restaurant=restaurant
        ).select_related('id_cmd')

    result = []

    # Ajouter les commandes prêtes
    if status_filter in ['all', 'ready']:
        for commande in commandes_pretes:
            result.append({
                'id': commande.id,
                'client': commande.client.username if commande.client else "Client inconnu",
                'adresse': commande.adresse,
                'telephone': commande.telephone,
                'restaurant': {
                    'id': commande.restaurant.id,
                    'name': commande.restaurant.name
                },
                'date': commande.date.strftime("%Y-%m-%d %H:%M"),
                'statut': commande.statut,
                'mode_paiement': commande.mode_paiement,
                'prix_total': str(commande.calculer_prix_total()),
            })

    # Ajouter les commandes en cours / livrées
    if status_filter in ['all', 'inprogress', 'delivered']:
        for livraison in mes_livraisons:
            commande = livraison.id_cmd

            # Filtrage selon état
            if status_filter == 'inprogress' and livraison.etat_livraison != 'en_cours':
                continue
            if status_filter == 'delivered' and livraison.etat_livraison != 'livree':
                continue

            result.append({
                'id': commande.id,
                'client': commande.client.username if commande.client else "Client inconnu",
                'adresse': commande.adresse,
                'telephone': commande.telephone,
                'restaurant': {
                    'id': commande.restaurant.id,
                    'name': commande.restaurant.name
                },
                'date': commande.date.strftime("%Y-%m-%d %H:%M"),
                'statut': livraison.etat_livraison,
                'mode_paiement': commande.mode_paiement,
                'prix_total': str(commande.calculer_prix_total()),
                'livraison_id': livraison.id,
                'livreur_id': int(livreur_id)  # Ajouter l'ID du livreur pour savoir si la commande lui est assignée
            })

    return JsonResponse({'commandes': result})

@csrf_exempt
def update_livreur_disponibilite(request):
    """
    API pour mettre à jour la disponibilité d'un livreur.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        livreur_id = data.get('livreur_id')
        disponible = data.get('disponible', True)
        
        livreur = get_object_or_404(Livreur, id_livr=livreur_id)
        livreur.set_disponible(disponible)
        
        return JsonResponse({'success': True, 'disponible': disponible})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def update_commande_status(request):
    """
    API pour mettre à jour le statut d'une commande par le livreur.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        commande_id = data.get('commande_id')
        livreur_id = data.get('livreur_id')
        nouveau_statut = data.get('nouveau_statut')
        
        if not commande_id or not livreur_id or not nouveau_statut:
            return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)
        
        commande = get_object_or_404(Commande, id=commande_id)
        livreur = get_object_or_404(Livreur, id_livr=livreur_id)
        
        # Vérifier si le livreur est disponible
        if not livreur.is_available() and nouveau_statut in ['en_cours', 'Prête']:
            return JsonResponse({'success': False, 'error': 'Vous n\'êtes pas disponible pour accepter des livraisons'}, status=400)
        
        # Gérer les différents cas selon le nouveau statut
        if nouveau_statut == 'en_cours':
            # Créer ou mettre à jour une livraison
            livraison, created = Livraison.objects.get_or_create(
                id_cmd=commande,
                id_livr=livreur,
                defaults={
                    'etat_livraison': 'en_cours',
                    'adresse': commande.adresse,
                    'date': timezone.now()
                }
            )
            
            if not created:
                livraison.etat_livraison = 'en_cours'
                livraison.save()
                
        elif nouveau_statut == 'livree':
            # Chercher la livraison existante
            try:
                livraison = Livraison.objects.get(id_cmd=commande, id_livr=livreur)
                livraison.mark_as_delivered()
            except Livraison.DoesNotExist:
                # Si pas de livraison, en créer une et la marquer comme livrée
                livraison = Livraison.objects.create(
                    id_cmd=commande,
                    id_livr=livreur,
                    etat_livraison='livree',
                    adresse=commande.adresse,
                    date=timezone.now()
                )
                commande.statut = 'livree'
                commande.save()
        
        else:
            # Pour les autres statuts, simplement mettre à jour le statut de la commande
            commande.statut = nouveau_statut
            commande.save()
            
            # Mettre à jour la livraison si elle existe
            livraison = Livraison.objects.filter(id_cmd=commande, id_livr=livreur).first()
            if livraison:
                # Mapper les statuts de commande aux statuts de livraison
                if nouveau_statut == 'en_attente':
                    livraison.etat_livraison = 'attente'
                elif nouveau_statut == 'annulee':
                    livraison.etat_livraison = 'annulee'
                elif nouveau_statut == 'Prête':
                    livraison.etat_livraison = 'attente'
                else:
                    livraison.etat_livraison = nouveau_statut
                livraison.save()
        
        return JsonResponse({
            'success': True, 
            'statut': nouveau_statut,
            'message': f'Statut mis à jour avec succès: {nouveau_statut}'
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def mark_as_delivered(request):
    """
    API pour marquer une livraison comme livrée.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        commande_id = data.get('commande_id')
        livreur_id = data.get('livreur_id')
        
        if not commande_id or not livreur_id:
            return JsonResponse({'success': False, 'error': 'commande_id et livreur_id sont requis'}, status=400)
        
        # Find the command
        commande = get_object_or_404(Commande, id=commande_id)
        
        # Find the livraison
        try:
            livraison = Livraison.objects.filter(
                id_cmd_id=commande_id,
                id_livr_id=livreur_id
            ).first()
            
            if not livraison:
                # If no livraison exists, try to create one
                livreur = Livreur.objects.get(id_livr=livreur_id)
                livraison = Livraison.objects.create(
                    id_livr=livreur,
                    id_cmd=commande,
                    etat_livraison='en_cours',
                    adresse=commande.adresse,
                    date=timezone.now()
                )
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erreur lors de la recherche de la livraison: {str(e)}'}, status=500)
        
        # Update using the model's method for consistency
        livraison.mark_as_delivered()
        
        return JsonResponse({'success': True})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
