from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import AddFournisseurForm, CreateFournissForm, SearchFournissForm
from bootstrap_modal_forms.generic import BSModalReadView, BSModalCreateView
from .models import Fournisseur
from magasin import functions


@login_required
def fourniss_list(request):
    hijri = functions.hijri_()
    fourniss_list = Fournisseur.objects.all()

    if request.method == 'POST':
        search_fourniss_form = SearchFournissForm(request.POST)
        if search_fourniss_form.is_valid():
            fourniss_list = Fournisseur.objects.filter(email=search_fourniss_form.cleaned_data['fourniss_search'])

    else:
        search_fourniss_form = SearchFournissForm()

    context = {'hijri': hijri, 'fourniss_list': fourniss_list, 'search_fourniss_form': search_fourniss_form}
    return render(request, 'fournisseur/fourniss/fourniss_list.html', context)


# ----------------------------------------------------------------------
# ==> Read Article View (django-bootstrap-modal-form)
# -----------------------------------------------------
class ReadFourniss(BSModalReadView):
    model = Fournisseur
    template_name = 'fournisseur/fourniss/read_fourniss.html'


# ----------------------------------------------------------------------
# ==> Create Fournisseur View (django-bootstrap-modal-form)
# -----------------------------------------------------
class CreateFournissView(BSModalCreateView):
    template_name = 'fournisseur/fourniss/create_fourniss.html'
    form_class = CreateFournissForm
    success_message = 'Success: Fournisseur Ajouter.'
    success_url = reverse_lazy('fournisseur:fourniss_list')


@login_required
def fourniss_detail(request, fourniss_id):
    hijri = functions.hijri_()
    fourniss_detail = get_object_or_404(Fournisseur, fourrnis_id=fourniss_id)

    context = {'hijri': hijri, 'fourniss_detail': fourniss_detail}
    return render(request, 'fournisseur/fourniss/fourniss_detail.html', context)


@login_required
def add_fournisseur(request):
    hijri = functions.hijri_()
    if request.method == 'POST':
        # form was submited
        add_fourniss_form = AddFournisseurForm(request.POST)
        if add_fourniss_form.is_valid():
            fourniss_detail = add_fourniss_form.cleaned_data      # retrieve the user input form
            print(fourniss_detail)
            add_fourniss_form.save()
    else:
        add_fourniss_form = AddFournisseurForm()

    context = {'hijri': hijri, 'add_fourniss_form': add_fourniss_form}

    return render(request, 'fournisseur/fourniss/add_fourniss.html', context)
