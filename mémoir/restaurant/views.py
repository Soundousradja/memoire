from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect,get_object_or_404

from Menu.models import HistoriquePlat
from home.models import Offre
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import render
from .models import Categorie, Evaluation, Plat
from .models import Reservation, Table, Client,Commande,CommandePlat
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from SuperAdmin.models import Restaurant
from datetime import date 
# Create your views here.
#Acceuil
def acceuil(request):
    return render(request,'acceuil.html')

#Menu

def menu_view(request):
    categories = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    restaurants = Restaurant.objects.all()
    restaurant_id = request.GET.get('restaurant')

    today = date.today()

    plats_disponibles = HistoriquePlat.objects.filter(date=today, quantite__gte=1).values_list('plat_id', flat=True)

    if restaurant_id:
        categories = Categorie.objects.filter(restaurant_id=restaurant_id)
        if categorie_id:
            plats = Plat.objects.filter(categorie_id=categorie_id, id__in=plats_disponibles)
        else:
            plats = Plat.objects.filter(categorie__restaurant_id=restaurant_id, id__in=plats_disponibles)
            if categories and not categorie_id:
                first_category = categories.first()
                if first_category:
                    plats = plats.filter(categorie_id=first_category.id)
    else:
        categories = []
        plats = []

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'plats.html', {'plats': plats})

    return render(request, 'menu.html', {
        'restaurants': restaurants,
        'categories': categories,
        'plats': plats,
        'selected_restaurant': restaurant_id
    })



#Réservation
def réservation(request):
    reservation_success = None
    reservation_error = None

    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        guests = int(request.POST.get("guests"))
        date = request.POST.get("date")
        time = request.POST.get("time")

        try:
            # Vérification ou création du client
            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={'username': name, 'email': email}
            )

            if not created:
                # Si le client existe déjà, vérifier si le username est le même
                if client.username != name:
                    # Le client a un autre nom d'utilisateur, le mettre à jour
                    client.username = name
                    client.save()

            # Rechercher une table disponible avec une capacité suffisante
            tables_disponibles = Table.objects.filter(capacité__gte=guests).order_by('capacité')
            if not tables_disponibles:
                reservation_error = f"Aucune table disponible pour {guests} personnes."
                return render(request, 'table.html', {'reservation_error': reservation_error})

            # Vérifier les tables déjà réservées à cette date et heure
            tables_reservees = Reservation.objects.filter(
                date=date, 
                time=time, 
                statut__in=['en_attente', 'acceptee']
            ).values_list('table_id', flat=True)
                    
            # Trouver une table disponible qui n'est pas déjà réservée
            # On prend la plus petite table qui peut accueillir le nombre de personnes
            table = tables_disponibles.exclude(id__in=tables_reservees).first()
            if not table:
                reservation_error = "Toutes les tables appropriées sont déjà réservées à cette heure."
                return render(request, 'table.html', {'reservation_error': reservation_error})

            # Créer la réservation
            reservation = Reservation.objects.create(
                client=client,
                table=table,
                guests=guests,
                date=date,
                time=time,
            )

            reservation_success = f"Réservation réussie ! Table {table.numéro} (capacité: {table.capacité} personnes)"
            return render(request, 'table.html', {
                'reservation_success': reservation_success
            })
        
        except Exception as e:
            reservation_error = f"Erreur lors de la réservation : {str(e)}"
            return render(request, 'table.html', {
                'reservation_error': reservation_error
            })

    return render(request, 'table.html')

def check_availability(request):
    """Vérifie la disponibilité des tables pour une date et heure données"""
    date = request.GET.get('date')
    time = request.GET.get('time')
    
    if not (date and time):
        return JsonResponse({'error': 'Date et heure requises'}, status=400)
    
    # Tables déjà réservées à cette date et heure (uniquement les réservations en attente ou acceptées)
    tables_reservees = Reservation.objects.filter(
        date=date, 
        time=time,
        statut__in=['en_attente', 'acceptee']
    ).values_list('table_id', flat=True)
    
    # Récupérer toutes les capacités distinctes de tables dans le système
    capacites_distinctes = Table.objects.values_list('capacité', flat=True).distinct().order_by('capacité')
    
    # Créer un dictionnaire de disponibilité dynamique
    disponibilite = {}
    for capacite in capacites_distinctes:
        count = Table.objects.filter(capacité=capacite).exclude(id__in=tables_reservees).count()
        disponibilite[f'disponibles_{capacite}'] = count
    
    return JsonResponse(disponibilite)

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
    restaurants =Restaurant.objects.all()
    return render(request, "panier.html", {
        "panier": items_panier,
        "total": total,
        "restaurants":restaurants
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


@csrf_exempt
def passer_commande(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Récupération du panier depuis la session
            panier = request.session.get("panier", {})
            if not panier:
                return JsonResponse({"error": "Votre panier est vide"}, status=400)
            
            # Vérification des champs obligatoires
            nom = data.get("nom")  # Récupère le nom saisi dans le formulaire
            adresse = data.get("adresse")
            telephone = data.get("telephone")
            
            mode_paiement = data.get("mode_paiement", "cash")
            restaurant_id = data.get("restaurant")
            try:
                  restaurant_obj = Restaurant.objects.get(id=restaurant_id)
                  restaurant_address = restaurant_obj.address # Ajustez selon votre modèle
            except Restaurant.DoesNotExist:
              return JsonResponse({"error": "Restaurant introuvable"}, status=400)

                          
            
            if not (nom and adresse and telephone and restaurant_id):
                return JsonResponse({"error": "Tous les champs sont obligatoires"}, status=400)
            
            # Créer un client basé sur le nom saisi dans le formulaire
            try:
                # Essayer de trouver un client avec ce numéro de téléphone
                client = Client.objects.get(phone=telephone)
                
                # Mettre à jour le nom si nécessaire
                if client.username != nom:
                    client.username = nom
                    client.save()
                    
            except Client.DoesNotExist:
                # Créer un nouveau client avec le nom saisi dans le formulaire
                # Assurez-vous que le nom d'utilisateur est unique
                username_base = nom.replace(" ", "_").lower()
                
                # Vérifier si ce nom d'utilisateur existe déjà
                username_count = Client.objects.filter(username__startswith=username_base).count()
                if username_count > 0:
                    username = f"{username_base}_{username_count + 1}"
                else:
                    username = username_base
                
                client = Client.objects.create_user(
                    username=username,
                    password="password123",  # Mot de passe par défaut
                    email=f"{username}@example.com",  # Email temporaire
                    phone=telephone,
                    address=adresse
                )
            
            # Création de la commande
            commande = Commande.objects.create(
                client=client,
                adresse=adresse,
                telephone=telephone,
                restaurant=restaurant_address,
                statut='en_attente',
                mode_paiement=mode_paiement
            )
            
            # Ajouter les plats à la commande
            for plat_id, item_info in panier.items():
                try:
                    plat = Plat.objects.get(id=int(plat_id))
                    CommandePlat.objects.create(
                        commande=commande,
                        plat=plat,
                        quantity=item_info['quantity']
                    )
                except Plat.DoesNotExist:
                    continue
            
            # Vider le panier après la commande
            request.session["panier"] = {}
            request.session.modified = True
            
            return JsonResponse({
                "success": True,
                "commande_id": commande.id,
                "message": "Commande passée avec succès!"
            })
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Format de données invalide"}, status=400)
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Afficher l'erreur complète pour débogage
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
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

def serveuracceuil(request):
    return render(request,'serveuracceuil.html')

def serveurmenu(request):
    categories = Categorie.objects.all()
    tables = Table.objects.all()
    return render(request, 'serveurmenu.html', {
        'categories': categories,
        'tables': tables
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


def historique_commandes(request):
    # Si vous avez un système d'authentification, utilisez ceci
    # commandes = Commande.objects.filter(client=request.user).order_by('-date')
    
    # Sinon, utilisez le numéro de téléphone stocké en session ou envoyé via formulaire
    telephone = request.GET.get('telephone')
    
    if telephone:
        try:
            client = Client.objects.get(phone=telephone)
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
                'commandes_details': commandes_details,
                'telephone': telephone
            })
            
        except Client.DoesNotExist:
            return render(request, 'historique.html', {
                'message': 'Aucun client trouvé avec ce numéro de téléphone',
                'telephone': telephone
            })
    
    # Si aucun téléphone n'est fourni, afficher le formulaire de recherche
    return render(request, 'historique.html')


@csrf_exempt
def serveur_envoyer_commande(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Vérifier les données reçues
            table_id = data.get('table_id')
            plats = data.get('plats')
            
            if not table_id or not plats:
                return JsonResponse({"error": "Informations incomplètes"}, status=400)
            
            # Récupérer la table
            try:
                table = Table.objects.get(id=table_id)
            except Table.DoesNotExist:
                return JsonResponse({"error": "Table introuvable"}, status=400)
            
            # Créer la commande (sans informations client)
            commande = Commande.objects.create(
                # Pas de client_id ou utiliser un client générique
                client=None,  # Si votre modèle permet client=null
                adresse="Sur place", 
                telephone="",
                restaurant="Sur place",
                statut='en_cours',
                mode_paiement='sur_place',
                # Stocker la référence à la table
                table_id=table_id
            )
            
            # Ajouter les plats à la commande
            for plat_info in plats:
                try:
                    plat = Plat.objects.get(id=plat_info['id'])
                    CommandePlat.objects.create(
                        commande=commande,
                        plat=plat,
                        quantity=plat_info['quantité']
                    )
                except Plat.DoesNotExist:
                    continue
            
            return JsonResponse({
                "success": True,
                "commande_id": commande.id,
                "message": "Commande passée avec succès!"
            })
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Format de données invalide"}, status=400)
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

