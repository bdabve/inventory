from django import forms
from .models import Fournisseur


class FournisseurForm(forms.ModelForm):
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

    def clean(self):
        super(FournisseurForm, self).clean()
        nom = self.cleaned_data.get('nom').lower()
        telephone = self.cleaned_data.get('telephone').lower()
        email = self.cleaned_data.get('email').lower()

        instance = self.instance
        if Fournisseur.objects.exclude(pk=instance.pk).filter(nom=nom).exists():
            self._errors['nom'] = self.error_class(['Ce nom existe déjà pour un autre fournisseur.'])

        if Fournisseur.objects.exclude(pk=instance.pk).filter(telephone=telephone).exists():
            self._errors['telephone'] = self.error_class(['Ce téléphone existe déjà pour un autre fournisseur.'])

        if Fournisseur.objects.exclude(pk=instance.pk).filter(email=email).exists():
            self._errors['email'] = self.error_class(['Ce email existe déjà pour un autre fournisseur.'])

        return self.cleaned_data


class SearchForm(forms.Form):
    search_word = forms.CharField(max_length=50, label=False)
    search_word.widget.attrs.update({'class': 'form-control col-sm-12', 'size': '30'})
