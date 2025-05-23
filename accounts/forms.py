from django import forms
from .models import Profile
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# ------------------------------------------------
# ==| Add User
# -----------------
class UserAddForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    field_order = ['username', 'password', 'password2', 'first_name', 'last_name', 'email']

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class ProfileAddForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['poste_travaille', 'groupe']
        widgets = {'groupe': forms.Select(attrs={'class': 'form-select'})}


# ------------------------------------------------
# ==| Edit User
# -----------------
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('poste_travaille', 'groupe')
        widgets = {'groupe': forms.Select(attrs={'class': 'form-select'})}
