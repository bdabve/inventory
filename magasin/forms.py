from django import forms
from django.shortcuts import get_object_or_404
from .models import Category, Article, Command
from datetime import date
import datetime


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['cat_id', 'slug']

    def clean(self):
        super(CreateCategoryForm, self).clean()
        name = self.cleaned_data.get('name').upper()
        cat_name = Category.objects.filter(name=name).exists()
        if cat_name:
            self._errors['name'] = self.error_class(['Category avec ce NOM exist deja'])
        return self.cleaned_data


# --------- | Articles Forms |------------------------------
class ArticalForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['art_id', 'slug', 'valeur']
        labels = {'ref': 'Référence', 'umesure': 'U.Mesure', 'emp': 'Emplacement', 'qte': 'Quantité', }
        widgets = {'category': forms.Select(attrs={'class': 'form-select'}), 'observation': forms.Textarea(attrs={'rows': 3})}

    def clean(self):
        super(ArticalForm, self).clean()
        # category must not be empty
        category = self.cleaned_data.get('category')
        if not category:
            self._errors['category'] = self.error_class(['Ce champ est obligatoire'])

        # UNIQUE validation
        code = self.cleaned_data.get('code').upper()
        instance = self.instance

        if Article.objects.exclude(pk=instance.pk).filter(code=code).exists():
            self._errors['code'] = self.error_class(['Ce code existe déjà pour un autre article.'])

        return self.cleaned_data


class SearchArticleForm(forms.Form):
    search_word = forms.CharField(max_length=100, label=False)
    search_word.widget.attrs.update({'class': 'form-control', 'size': '35'})


class EntreeForm(forms.ModelForm):
    tday = date.today()
    entree_date = forms.DateField(
        label="Date d'entrée",
        widget=forms.DateInput(attrs={'class': 'col form-control', 'type': 'date'}),
        required=True,
        initial=tday
    )

    class Meta:
        model = Article
        fields = ['slug', 'qte', 'prix']

    def clean(self):
        super(EntreeForm, self).clean()
        qte = self.cleaned_data.get('qte')
        if qte < 1:
            self._errors['qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data


class SortieForm(forms.ModelForm):
    tday = date.today()
    sortie_date = forms.DateField(
        label="Date de sortie",
        widget=forms.DateInput(attrs={'class': 'col form-control', 'type': 'date'}),
        required=True,
        initial=tday
    )

    class Meta:
        model = Article
        fields = ['slug', 'qte', 'prix']

    def clean(self):
        super(SortieForm, self).clean()
        slug = self.cleaned_data.get('slug')
        article = get_object_or_404(Article, slug=slug)
        sortie_qte = self.cleaned_data.get('qte')

        if sortie_qte > article.qte:
            self._errors['qte'] = self.error_class(['Cette Quantité N\'exist Pas Dans le Stock'])
        elif sortie_qte < 1:
            self._errors['qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data


# ============================
# == Movement Forms
# ------------------
class SearchMovementForm(forms.Form):
    current_year = datetime.date.today().year
    YEARS = [(y, y) for y in range(current_year, current_year - 5, -1)]

    search_code = forms.CharField(max_length=50, required=False, label=False)
    OPERATION = [('', 'Tous'), ('Initial', 'Initial'), ('Entree', 'Entree'), ('Sortie', 'Sortie')]

    operation = forms.ChoiceField(choices=OPERATION, required=False, label=False)
    day = forms.DateField(
        label="Date précise", required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    month = forms.ChoiceField(
        choices=[('', 'Mois')] + [(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        required=False, label=False
    )
    year = forms.ChoiceField(
        choices=[('', 'Année')] + YEARS,
        required=False, label=False
    )


class Etats(forms.Form):
    tday = date.today()
    PAR = [('journalier', 'Journalier'), ('mensuel', 'Mensuel'), ('tous', 'Tous')]
    par = forms.ChoiceField(widget=forms.Select, choices=PAR, label=False, required=True, initial='journalier')
    etat_date = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.SelectDateWidget(
            attrs={'class': 'form-select me-2'},
            empty_label=("Année", "Mois", "Jour"),
            years=range(2020, date.today().year + 1),
        )
    )


# --------- | Commands Forms |------------------------------
class CreateCommandForm(forms.Form):
    tday = date.today()
    cmnd_date = forms.DateField(
        label="Date de sortie",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True,
        initial=tday
    )
    cmnd_qte = forms.IntegerField(min_value=1)

    def clean(self):
        super(CreateCommandForm, self).clean()
        qte = self.cleaned_data.get('cmnd_qte')

        if qte < 1:
            self._errors['cmnd_qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data


class EditCommandeForm(forms.ModelForm):
    class Meta:
        model = Command
        exclude = ['art_id']
        labels = {'user_id': 'Utilisateur', 'command_date': 'Date', 'qte': 'Quantité', }
        widgets = {
            'command_date': forms.DateInput(attrs={'class': 'form-select', 'type': 'date'})
        }

    def clean(self):
        super(EditCommandeForm, self).clean()
        status = self.cleaned_data.get('status')
        if status not in (1, 0):
            self._errors['status'] = self.error_class(['Ce champ doit contenir 0 ou 1'])
        return self.cleaned_data
