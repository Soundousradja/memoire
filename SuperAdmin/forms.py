from django import forms
from .models import Restaurant
from .models import Admin

from .models import Plat, Ingredient
from django.forms import modelformset_factory
from .models import  Ingredient, Plat

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'image']

class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin  # The form is based on the Admin model.
        fields = ['name', 'phone', 'image' ,'restaurant']  # Only include these fields in the form.

from .models import Plat

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['name', 'image', 'price', 'ingredients']
        widgets = {
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class FiltreVenteForm(forms.Form):
    restaurant = forms.ModelChoiceField(queryset=Restaurant.objects.all(), required=True)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)


