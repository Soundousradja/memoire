import secrets
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login

from django.contrib.auth.forms import UserCreationForm

from SuperAdmin.models import Restaurant

from .models import  CustomUser
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CustomUser
from .models import Offre
from django.shortcuts import get_object_or_404
from datetime import datetime
#ta3 lamisse
from django.contrib.auth import authenticate, login
from .forms import ClientRegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group  # Import Group model
from django.contrib.auth.hashers import make_password


# Create your views here.
def home(request):
    return render(request,'pages/index.html')
def utilisateur(request):
    return render(request,'pages/Utilisateur.html')
def client_page(request):
    return render(request, 'pages/client.html')
#def users_by_role(request, role):
    #users = CustomUser.objects.filter(role=role)  # Filtrer par rôle
    #return render(request, 'pages/user_by_role.html', {'users': users, 'role': role})
    from django.http import JsonResponse
from .models import CustomUser

def users_by_role(request, role):
    restaurant = get_restaurant_for_user(request.user)
    if restaurant:
        users = CustomUser.objects.filter(restaurant=restaurant, role=role)
    else:
        users = CustomUser.objects.none()

    if not users.exists():
        return JsonResponse({"utilisateurs": []}, status=200)  # Retourne une liste vide

    users_data = [
        {
            "id": user.id,
            "nom": user.username,
            "email": user.email,
            "adresse": user.adresse if user.adresse else "Non renseignée",
            "telephone": user.telephone if user.telephone else "Non renseigné",
            "mot_de_passe_clair": user.mot_de_passe_clair if user.mot_de_passe_clair else ""
        }
        for user in users
    ]
    return JsonResponse({"utilisateurs": users_data})
@csrf_exempt
def ajouter_utilisateur(request):
    if request.method == "POST":
       restaurant = get_restaurant_for_user(request.user)
       if not restaurant:
            return JsonResponse({"success": False, "error": "Pas de restaurant associé."}, status=403)
       try:
            data = json.loads(request.body)
            nom = data.get("nom")
            email = data.get("email")
            password = data.get("password")
            adresse = data.get("adresse")
            telephone = data.get("telephone")
            role = data.get("role")
              # Nouveau paramètre pour l'ID du restaurant

            if not (nom and email and password and adresse and telephone and role):
                return JsonResponse({"success": False, "error": "Tous les champs sont obligatoires."}, status=400)

            # Créer un nom d'utilisateur à partir du nom
            username = nom.lower().replace(" ", "_")
            
            # Vérifier si l'utilisateur existe déjà
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "error": "Un utilisateur avec cet email existe déjà."}, status=400)
            
            # Créer l'utilisateur
            user = CustomUser.objects.create(
                username=username,
                email=email,
                role=role,
                adresse=adresse,
                telephone=telephone,
                is_staff=True if role != 'client' else False,  # Marquer comme staff tous les utilisateurs sauf clients
                restaurant=restaurant
            )
            
           
            user.set_password(password)
            user.mot_de_passe_clair = password
            
            # Ajouter l'utilisateur au groupe correspondant à son rôle
            from django.contrib.auth.models import Group
            if role in ['chef', 'serveur', 'livreur', 'fournisseur', 'admin']:
                # Convertir le nom du rôle pour correspondre au nom du groupe (première lettre majuscule)
                group_name = role.capitalize()
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    # Créer le groupe s'il n'existe pas
                    group = Group.objects.create(name=group_name)
                    user.groups.add(group)
            
            user.save()
            return JsonResponse({"success": True})
       except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)
@csrf_exempt
def modifier_utilisateur(request, user_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = CustomUser.objects.get(id=user_id)  # 🔹 Récupérer l'utilisateur

            # Mise à jour seulement des champs modifiés
            user.username = data.get("nom", user.username) or user.username
            user.adresse = data.get("adresse", user.adresse) or user.adresse
            user.telephone = data.get("telephone", user.telephone) or user.telephone
            user.role = data.get("role", user.role) or user.role

            email = data.get("email")
            if email:  # 🔹 Modifier l'email seulement s'il est renseigné
                user.email = email

            user.save()  # 🔹 Enregistrer les modifications
            return JsonResponse({"success": True})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "Utilisateur introuvable."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)
@csrf_exempt
def supprimer_utilisateur(request, user_id):
    if request.method == "DELETE":
        try:
            user = CustomUser.objects.get(id=user_id)  # 🔹 Trouver l'utilisateur
            user.delete()  # 🔹 Supprimer
            return JsonResponse({"success": True})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "Utilisateur introuvable."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)
def liste_utilisateurs(request):
    utilisateurs = CustomUser.objects.all()
    return render(request, 'pages/liste_utilisateur.html', {'utilisateurs': utilisateurs})
@login_required
def utilisateurs_par_role(request):
    role = request.GET.get('role', '')
    restaurant = get_restaurant_for_user(request.user)

    if restaurant:
        utilisateurs = CustomUser.objects.filter(role=role, restaurant=restaurant)
    else:
        utilisateurs = CustomUser.objects.none()

    return render(request, 'pages/index.html', {
        'role': role,
        'utilisateurs': utilisateurs,
    })


# ✅ Vue pour afficher la page des offres (protégée)
@login_required
def offre(request):
    restaurant = get_restaurant_for_user(request.user)
    if restaurant:
        offres = Offre.objects.filter(restaurant=restaurant)
    else:
        offres = Offre.objects.none()
    return render(request, 'Pages_Offre/offre.html', {'offres': offres})

# ✅ Vue pour ajouter une offre (protégée, sans csrf_exempt si tu gères bien Fetch)
@login_required
def ajouter_offre(request):
    if request.method == "POST":
        restaurant = get_restaurant_for_user(request.user)
        if not restaurant:
            return JsonResponse({"success": False, "error": "Pas de restaurant associé."}, status=403)

        try:
            Nom_Offre = request.POST.get("Nom_Offre")
            Date_Debut_str = request.POST.get("Date_Debut")
            Date_Fin_str = request.POST.get("Date_Fin")
            image = request.FILES.get("image")

            if not (Nom_Offre and Date_Debut_str and Date_Fin_str):
                return JsonResponse({"success": False, "error": "Tous les champs sont obligatoires."}, status=400)

            Date_Debut = datetime.strptime(Date_Debut_str, "%Y-%m-%d").date()
            Date_Fin = datetime.strptime(Date_Fin_str, "%Y-%m-%d").date()

            if Date_Debut >= Date_Fin:
                return JsonResponse({"success": False, "error": "La date de début doit être avant la date de fin."}, status=400)

            nouvelle_offre = Offre.objects.create(
                Nom_Offre=Nom_Offre,
                Date_Debut=Date_Debut,
                Date_Fin=Date_Fin,
                image=image,
                restaurant=restaurant
            )

            return JsonResponse({"success": True, "message": "Offre ajoutée avec succès."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

# ✅ Vue pour afficher toutes les offres (protégée)
@login_required
def afficher(request):
    restaurant = get_restaurant_for_user(request.user)
    if restaurant:
        offres = Offre.objects.filter(restaurant=restaurant)
    else:
        offres = Offre.objects.none()

    offres_data = [
        {
            "id": offre.id,
            "Nom_Offre": offre.Nom_Offre,
            "Date_Debut": offre.Date_Debut.strftime("%Y-%m-%d"),
            "Date_Fin": offre.Date_Fin.strftime("%Y-%m-%d"),
            "statut": offre.statut,
            "image": offre.image.url if offre.image else None
        }
        for offre in offres
    ]
    return JsonResponse({"offres": offres_data})

# ✅ Vue pour supprimer une offre (protégée)
@csrf_exempt
@login_required
def supprimer_offre(request, offre_id):
    if request.method == "DELETE":
        try:
            offre = Offre.objects.get(id=offre_id)
            offre.delete()
            return JsonResponse({"success": True})
        except Offre.DoesNotExist:
            return JsonResponse({"success": False, "error": "Offre introuvable."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

# ✅ Vue pour modifier une offre (protégée)
@csrf_exempt
@login_required
def modifier_offre(request, id):
    try:
        offre = Offre.objects.get(id=id)
        if request.method == 'POST':
            nom_offre = request.POST.get('Nom_Offre')
            date_debut_str = request.POST.get('Date_Debut')
            date_fin_str = request.POST.get('Date_Fin')
            
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date() if date_debut_str else None
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date() if date_fin_str else None
            
            offre.Nom_Offre = nom_offre
            offre.Date_Debut = date_debut
            offre.Date_Fin = date_fin

            if 'image' in request.FILES:
                offre.image = request.FILES['image']
                
            offre.save()
            return JsonResponse({'success': True})

        else:
            return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

    except Offre.DoesNotExist:
        return JsonResponse({"success": False, "error": "Offre introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

#ta3 lamisse

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print(f"Attempted login for user: {username}")
            if user is not None:
                print(f"Authentication successful for user: {username}")
                login(request, user)
                return redirect(determine_redirect_url(user))
            else:
                print(f"Authentication failed for user: {username}")
                form.add_error(None, 'Invalid username or password.')
        else:
            print(f"Form is invalid: {form.errors}")
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})
from django.urls import reverse

def determine_redirect_url(user):
    print(f"--- Redirect Check for User: {user.username} ---")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Is staff: {user.is_staff}")
    print(f"Role: {user.role}")
    print(f"Groups: {user.groups.all()}")

    # Vérification par superuser, groupes et rôle
    if user.is_superuser:
        print("Redirecting to superadmin_interface")
        return reverse('home')
    elif user.is_staff:
        if user.groups.filter(name='Admin').exists():
            print("Redirecting to gestion_admin")

            return reverse('gestion_admin')

        elif user.groups.filter(name='Chef').exists() or user.role == 'chef':
            print("Redirecting to chef_interface")
            return reverse('menu:pagechef')
        elif user.groups.filter(name='Serveur').exists() or user.role == 'serveur':
            print("Redirecting to serveur_interface")
            return reverse('serveur_interface')
        elif user.groups.filter(name='Livreur').exists() or getattr(user, 'role', None) == 'livreur':
            print("Redirecting to landing_page")
            return reverse('restaurant:landing_page')
        # ... other conditions ...
    
    # ... more conditions ...
    
    elif user.role == 'livreur':
        print("Redirecting to livreur_interface based on role")
# Use absolute URL as a fallback if reverse() doesn't work
        return '/restaurant/landing_page'
    elif user.role == 'fournisseur':
        print("Redirecting to fournisseur_interface based on role")
        return reverse('fournisseur_interface')  
    elif user.role == 'admin':
        print("Redirecting to fournisseur_interface based on role")
        return reverse('gestion_admin')  
    else:
        print("Redirecting to client_interface")
        return reverse('acceuil')
@login_required
def superadmin_interface(request):
    return render(request, 'pages/index.html') # Create this template

@staff_member_required
def admin_interface(request):
     restaurant = request.user.admin_profile.restaurant
     return render(request, 'Pages_Offre/offre.html', {'restaurant': restaurant})       # Create this template

@login_required
def serveur_interface(request):
    # You might want to restrict this further based on group
    if not request.user.is_staff or not request.user.groups.filter(name='Serveur').exists():
        return redirect('access_denied') # Create an access denied page
    return render(request, 'app/serveur_interface.html')     # Create this template

@login_required
def chef_interface(request):
    if not request.user.is_staff or not request.user.groups.filter(name='Chef').exists():
        return redirect('access_denied')
    return render(request, 'PagesMenu/chef.html')        # Create this template

@login_required
def fournisseur_interface(request):
    if not request.user.is_staff or not request.user.groups.filter(name='Fournisseur').exists():
        return redirect('access_denied')
    return render(request, 'app/fournisseur_interface.html')  # Create this template

@login_required
def livreur_interface(request):
    if not request.user.is_staff or not request.user.groups.filter(name='Livreur').exists():
        return redirect('access_denied')
    return render(request, 'restaurant/landing_page.html')    


@login_required
def technicien_interface(request):
    if not request.user.is_staff or not request.user.groups.filter(name='Technicien').exists():
        return redirect('access_denied')
    return render(request, 'app/technicien_interface.html')  # Create this template

@login_required
def client_interface(request):
    return render(request, 'accueil.html')      # Create this template

def access_denied(request):
    return render(request, 'app/access_denied.html')        # Create this template


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# ... your other views ...

@staff_member_required
def staff_default_view(request):
    return render(request, 'app/gestion_admin.html') # Create this template

# your_app/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages

from .forms import ForgotPasswordForm, PasswordResetForm
# Import your PasswordResetToken model (if you created one)

CustomUser = get_user_model() # Get your CustomUser model

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email) # Use CustomUser
                # Generate reset token and expiry
                reset_token = secrets.token_hex(16)

                expiry_at = timezone.now() + timezone.timedelta(hours=1)

                # Store the token (adapt based on your model choice)
                # Example using PasswordResetToken model:
                from .models import PasswordResetToken
                PasswordResetToken.objects.update_or_create(user=user, defaults={'token': reset_token, 'expiry_at': expiry_at})

                # Create reset link
                reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'token': reset_token}))
                subject = "Réinitialisation de votre mot de passe"
                message = f"Cliquez sur le lien suivant pour réinitialiser votre mot de passe: {reset_url}"
                from_email = 'your_email@example.com' # Replace with your sending email
                recipient_list = [user.email]
                send_mail(subject, message, from_email, recipient_list)

                messages.success(request, "Un lien de réinitialisation de mot de passe a été envoyé à votre adresse e-mail.")
                return redirect('forgot_password')

            except CustomUser.DoesNotExist: # Use CustomUser
                messages.error(request, "Aucun utilisateur trouvé avec cette adresse e-mail.")
                return render(request, 'app/forgot_password', {'form': form})

    else:
        form = ForgotPasswordForm()
    return render(request, 'app/forgot_password.html', {'form': form})

def password_reset_confirm_view(request, token):
    try:
        # Retrieve the token and user (adapt based on your model choice)
        from .models import PasswordResetToken
        reset_token_entry = PasswordResetToken.objects.get(token=token, expiry_at__gt=timezone.now())
        user = reset_token_entry.user

        if request.method == 'POST':
            form = PasswordResetForm(user, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                # Clear the reset token
                reset_token_entry.delete()
                messages.success(request, "Votre mot de passe a été réinitialisé avec succès. Veuillez vous connecter avec votre nouveau mot de passe.")
                return redirect('login')
        else:
            form = PasswordResetForm(user)
        return render(request, 'app/password_reset_confirm.html', {'form': form, 'token': token})

    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Ce lien de réinitialisation de mot de passe est invalide ou a expiré.")
        return render(request, 'app/password_reset_confirm.html', {'error': 'invalid_token'})

# You'll need to import timezone
from django.utils import timezone

from django.http import HttpResponse

def client_register_view(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponse("Registration Successful!")
        else:
            error_message = "Form is invalid. Errors: " + str(form.errors)
            return HttpResponse(error_message, status=400)
    else:
        form = ClientRegistrationForm()
    return render(request, 'app/client_register.html', {'form': form})
def create_user_groups():
    """
    Crée les groupes nécessaires s'ils n'existent pas déjà.
    À exécuter une fois, par exemple dans une migration ou dans le shell Django.
    """
    from django.contrib.auth.models import Group
    
    required_groups = ['Chef', 'Serveur', 'Livreur', 'Fournisseur', 'Admin', 'Technicien']
    
    for group_name in required_groups:
        Group.objects.get_or_create(name=group_name)
        print(f"Groupe '{group_name}' créé ou vérifié.")
def sync_existing_users():
    """
    Synchronise les utilisateurs existants avec leurs groupes et statut staff.
    À exécuter une fois pour corriger les données existantes.
    """
    from django.contrib.auth.models import Group
    from .models import CustomUser
    
    for user in CustomUser.objects.all():
        # Si l'utilisateur a un rôle non-client, il devrait être staff
        if user.role and user.role != 'client':
            user.is_staff = True
            
            # Ajouter au groupe correspondant
            group_name = user.role.capitalize()
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                group = Group.objects.create(name=group_name)
            
            # Vérifier si l'utilisateur est déjà dans ce groupe
            if not user.groups.filter(name=group_name).exists():
                user.groups.add(group)
                print(f"Utilisateur {user.username} ajouté au groupe {group_name}")
            
            user.save()
            print(f"Utilisateur {user.username} mis à jour (staff: {user.is_staff})")        
def get_restaurant_for_user(user):
    if hasattr(user, 'admin_profile') and user.admin_profile:
        return user.admin_profile.restaurant
    return None


  