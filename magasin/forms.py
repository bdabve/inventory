from django import forms
from django.shortcuts import get_object_or_404
from .models import Category, Article       # , Command
from bootstrap_modal_forms.forms import BSModalModelForm
from datetime import date


class CreateCategoryForm(BSModalModelForm):
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
class CreateArticleForm(BSModalModelForm):
    class Meta:
        model = Article
        exclude = ['art_id', 'slug', 'valeur']
        labels = {'ref': 'Reference', 'umesure': 'U Mesure', 'emp': 'Emplacement', 'qte': 'Quantité', }
        widgets = {'observation': forms.Textarea(attrs={'rows': 3})}

    def clean(self):
        super(CreateArticleForm, self).clean()
        # category must not be empty
        category = self.cleaned_data.get('category')
        if not category:
            self._errors['category'] = self.error_class(['Ce champ est obligatoire'])

        # UNIQUE validation
        code = self.cleaned_data.get('code').upper()
        art_code = Article.objects.filter(code=code)
        if len(art_code) > 0:
            self._errors['code'] = self.error_class(['Article avec ce CODE exist deja'])

        return self.cleaned_data


class UpdateArticleForm(BSModalModelForm):
    class Meta:
        model = Article
        exclude = ['art_id', 'slug', 'qte', 'prix', 'valeur']


class UpdateArticleForm_(forms.ModelForm):
    # UpdateArticleFrom_: to update article from article detail
    class Meta:
        model = Article
        exclude = ['art_id', 'slug', 'qte', 'prix', 'valeur']

        widgets = {'category': forms.Select(attrs={'class': 'form-select'}), 'observation': forms.Textarea(attrs={'rows': 3})}


class SearchArticleForm(forms.Form):
    search_word = forms.CharField(max_length=100, label=False)
    CHOICES = [('code', 'Code'), ('ref', 'Reference'), ('designation', 'Designation')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label=False, required=False, initial='code')

    search_word.widget.attrs.update({'class': 'form-control', 'size': '35'})


class EntreeForm(forms.ModelForm):
    tday = date.today()
    # FIXME: empty_label dont work with required=True
    entree_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'col form-select'}), required=True, initial=tday)

    class Meta:
        model = Article
        fields = ['qte', 'prix']

    def clean(self):
        super(EntreeForm, self).clean()
        qte = self.cleaned_data.get('qte')
        if qte < 1:
            self._errors['qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data


class SortieForm(forms.Form):
    tday = date.today()
    sortie_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'col form-select'}), required=True, initial=tday)
    slug = forms.CharField(max_length="100")
    sortie_qte = forms.IntegerField(min_value=1)
    sortie_prix = forms.DecimalField()

    # add class name to inputs
    sortie_qte.widget.attrs.update({'class': 'form-control'})
    sortie_prix.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        super(SortieForm, self).clean()
        slug = self.cleaned_data.get('slug')
        article = get_object_or_404(Article, slug=slug)
        qte = self.cleaned_data.get('sortie_qte')

        if qte > article.qte:
            self._errors['sortie_qte'] = self.error_class(['Cette Quantité N\'exist Pas Dans le Stock'])
        elif qte < 1:
            self._errors['sortie_qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data


# --------- | Movement Forms |------------------------------
class SearchMovementForm(forms.Form):
    tday = date.today()
    search_code = forms.CharField(max_length=50, label=False, required=False)
    OPERATION = [('entree', 'Entree'), ('sortie', 'Sortie'), ('', 'Tous')]
    date = forms.DateField(widget=forms.SelectDateWidget(empty_label=('Année', 'Mois', 'Jour')), required=False, initial=tday)
    operation = forms.ChoiceField(widget=forms.Select, choices=OPERATION, label=False, required=False, initial='tous')


class Etats(forms.Form):
    tday = date.today()
    PAR = [('journalier', 'Journalier'), ('mensuel', 'Mensuel'), ('tous', 'Tous')]
    etat_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'col form-select'}), required=True, initial=tday)
    par = forms.ChoiceField(widget=forms.Select, choices=PAR, label=False, required=True, initial='journalier')


# --------- | Commands Forms |------------------------------
class CreateCommandForm(forms.Form):
    tday = date.today()
    cmnd_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'form-control'}), required=False, initial=tday)
    cmnd_qte = forms.IntegerField(min_value=1)

    cmnd_qte.widget.attrs.update({'class': 'form-control'})
    cmnd_date.widget.attrs.update({'class': 'form-select'})

    def clean(self):
        super(CreateCommandForm, self).clean()
        qte = self.cleaned_data.get('cmnd_qte')

        if qte < 1:
            self._errors['cmnd_qte'] = self.error_class(['Valeur doit être superieur ou égale a 1'])
        return self.cleaned_data
