from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.db.models import Q
from django.db import transaction
from . import models
from . import forms
from magasin import functions


@login_required
def fourniss_list(request):
    hijri = functions.hijri_()
    fourniss_list = models.Fournisseur.objects.all()
    search_form = forms.SearchForm(request.POST or None)

    if request.method == 'POST' and search_form.is_valid():
        query = search_form.cleaned_data['search_word']
        fourniss_list = models.Fournisseur.objects.filter(
            Q(email__icontains=query) |
            Q(nom__icontains=query) |
            Q(telephone__icontains=query) |
            Q(address__icontains=query) |
            Q(fourniture__icontains=query)
        )

    context = {
        'hijri': hijri,
        'fourniss_list': fourniss_list,
        'search_form': search_form,
    }
    return render(request, 'fournisseur/fourniss/fourniss_list.html', context)


# ----------------------------------------------------------------------
# ==> Read Article View (django-bootstrap-modal-form)
# -----------------------------------------------------
def read_fournisseur(request, pk):
    fournis = get_object_or_404(models.Fournisseur, fourrnis_id=pk)
    return render(request, 'fournisseur/fourniss/read_fourniss.html', {'fournis': fournis})


# ----------------------------------------------------------------------
# ==> Create Fournisseur View (django-bootstrap-modal-form)
# -----------------------------------------------------
@login_required
def create_fournis(request):
    if request.method == 'POST':
        form = forms.FournisseurForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    fournis = form.save()
                return JsonResponse({'success': True, 'message': f'✅ Fournisseur {fournis.nom} Enregistrés avec succés'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Erreur lors de l\'ajout du fournisseur: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = forms.FournisseurForm()

    context = {'form': form}
    return render(request, 'fournisseur/fourniss/create_fourniss.html', context)


def update_fourniss(request, pk):
    fourniss = get_object_or_404(models.Fournisseur, fourrnis_id=pk)
    if request.method == 'POST':
        form = forms.FournisseurForm(request.POST, instance=fourniss)
        if form.is_valid():
            updated_fourniss = form.save()
            return JsonResponse(
                {
                    'success': True,
                    'message': f'✅ Fournisseur {updated_fourniss.nom} Modifier avec succés.'
                }
            )
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.FournisseurForm(instance=fourniss)

    context = {'form': form, 'fourniss': fourniss}
    return render(request, 'fournisseur/fourniss/update_fourniss.html', context)


# ==> Delete Article View (bootstrap-modal-form)
def delete_fourniss(request, pk):
    if request.method == 'POST':
        fourniss = get_object_or_404(models.Fournisseur, fourrnis_id=pk)
        fourniss.delete()
        return JsonResponse({'success': True, 'message': f'✅ Fournisseur {fourniss.nom} supprimé avec succés.'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def fourniss_detail(request, fourniss_id):
    hijri = functions.hijri_()
    fourniss_detail = get_object_or_404(models.Fournisseur, fourrnis_id=fourniss_id)

    context = {'hijri': hijri, 'fourniss_detail': fourniss_detail}
    return render(request, 'fournisseur/fourniss/fourniss_detail.html', context)
