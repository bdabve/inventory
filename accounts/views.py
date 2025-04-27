from django.shortcuts import render, get_object_or_404   # , redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Profile
from .forms import LoginForm, UserEditForm, ProfileEditForm, UserAddForm, ProfileAddForm
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
# ==| Manage users
# -----------------
@login_required
def manage_users(request):
    hijri = functions.hijri_()
    users = User.objects.all().exclude(id='1').order_by('-date_joined')
    context = {'hijri': hijri, 'users': users}
    return render(request, 'accounts/manage_users.html', context)


# ------------------------------------------------
# ==| Create User
@login_required
def create_user(request):
    if request.method == 'POST':
        user_form = UserAddForm(data=request.POST)
        profile_form = ProfileAddForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])   # Set the chosen password
            new_user.save()                                             # Save the User object
            cd_profile = profile_form.cleaned_data
            Profile.objects.create(
                user=new_user,
                poste_travaille=cd_profile['poste_travaille'],
                groupe=cd_profile['groupe']
            )
            return JsonResponse({'success': True, 'message': '✅ Utilisateur ajouté avec succès.'})
        else:
            errors = {
                'user_form': user_form.errors.get_json_data(),
                'profile_form': profile_form.errors.get_json_data()
            }
            return JsonResponse({'success': False, 'errors': errors})
    else:
        user_form = UserAddForm()
        profile_form = ProfileAddForm()

    return render(request, 'accounts/create_user.html', {'user_form': user_form, 'profile_form': profile_form})


# ----------------------------------------------------------------------
# ==> Read User Profile
# ---------------------
def read_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/read_profile.html', {'user': user})


# ------------------------------------------------
# ==| Edit Profile
@login_required
def edit_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(Profile, user_id=pk)

    if request.method == 'POST':
        user_form = UserEditForm(instance=user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return JsonResponse({'success': True, 'message': '✅ Utilisateur Modifier avec succès.'})
        else:
            errors = {
                'user_form': user_form.errors.get_json_data(),
                'profile_form': profile_form.errors.get_json_data()
            }
            return JsonResponse({'success': False, 'errors': errors})
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileAddForm(instance=profile)

    context = {'user': user, 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/edit_profile.html', context)


@login_required
@require_POST
def change_user_group(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user:
        groupe = user.profile.groupe
        user.profile.groupe = 'other' if groupe == 'admin' else 'admin'
        user.profile.save()
        return JsonResponse(
            {
                'success': True,
                'message': f'✅ Utilisateur {user.username} modifie avec succés {user.profile.groupe}.'
            }
        )
    else:
        return JsonResponse({'success': False, 'error': 'User Not Found'})


# ----------------------------------------------------------------------
# ==> Delete User View (bootstrap-modal-form)
# -----------------------------------------------------
@login_required
@require_POST
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return JsonResponse({'success': True, 'message': f'✅ Utilisateur {user.username} supprimé avec succés.'})
