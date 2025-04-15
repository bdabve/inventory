from django import forms
from .models import Fournisseur
from bootstrap_modal_forms.forms import BSModalModelForm


class AddFournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        exclude = ['frns_id']
        widgets = {'note': forms.Textarea(attrs={'cols': 100, 'rows': 5})}
        # labels = {'': ''}
        help_texts = {
            'nom': 'Nom du Domain',
            'address': 'Addresse',
            'fourniture': 'Produit Du Fournisseur',
            'code_postal': 'Code Postal',
            'pays': 'Pays',
            'telephone': 'Telephone',
            'fax': 'Fax',
            'email': 'Email',
            'note': 'Ajouter une note',
        }
        # error_messages = {'Nom': {'max_length': 'Name can only be 20 characters in length'}}


class CreateFournissForm(BSModalModelForm):
    class Meta:
        model = Fournisseur
        fields = '__all__'
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class SearchFournissForm(forms.Form):
    fourniss_search = forms.CharField(max_length=50, label=False)
    fourniss_search.widget.attrs.update({'class': 'form-control', 'size': '35'})
