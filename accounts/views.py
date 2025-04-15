from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import LoginForm, UserEditForm, ProfileEditForm, UserAddForm, ProfileAddForm
from bootstrap_modal_forms.generic import BSModalReadView, BSModalDeleteView

from .models import Profile
from magasin import functions


def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        login_form = LoginForm()

    context = {'login_form': login_form}
    return render(request, 'accounts/login.html', context)


# ------------------------------------------------
# ==| Add User
# -----------------
@login_required
def add_user(request):
    hijri = functions.hijri_()
    if request.method == 'POST':
        user_form = UserAddForm(data=request.POST)
        profile_form = ProfileAddForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # username = user_form.cleaned_data['username']
            new_user = user_form.save(commit=False)

            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])

            # Save the User object
            new_user.save()
            cd_profile = profile_form.cleaned_data
            Profile.objects.create(user=new_user, poste_travaille=cd_profile['poste_travaille'], groupe=cd_profile['groupe'])
            messages.info(request, 'User Added Successfuly')
            return redirect('accounts:manage_users')
    else:
        user_form = UserAddForm()
        profile_form = ProfileAddForm()

    context = {'hijri': hijri, 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/add_user.html', context)


# ------------------------------------------------
# ==| Edit Profile
# -----------------
@login_required
def edit_profile(request, id):
    hijri = functions.hijri_()
    user = get_object_or_404(User, id=id)
    profile = get_object_or_404(Profile, user_id=id)

    if request.method == 'POST':
        user_form = UserEditForm(instance=user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.info(request, 'Profile Modifier avec Succés')
            return redirect('accounts:manage_users')
        else:
            messages.error(request, 'Error updating profile.')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=user.profile)

    context = {'hijri': hijri, 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/edit_profile.html', context)


# ------------------------------------------------
# ==| Manage users
# -----------------
@login_required
def manage_users(request):
    hijri = functions.hijri_()
    users = User.objects.all().exclude(id='1')

    context = {'hijri': hijri, 'users': users}
    return render(request, 'accounts/manage_users.html', context)


# ----------------------------------------------------------------------
# ==> Read Article View (django-bootstrap-modal-form)
# -----------------------------------------------------
class ReadProfile(BSModalReadView):
    model = User
    template_name = 'accounts/read_profile.html'


# ----------------------------------------------------------------------
# ==> Delete User View (django-bootstrap-modal-form)
# -----------------------------------------------------
class DeleteUserView(BSModalDeleteView):
    model = User
    template_name = 'accounts/delete_user.html'
    success_message = 'Success: Utilisateur Supprimer.'
    success_url = reverse_lazy('accounts:manage_users')
