from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/manage-users/', views.manage_users, name="manage_users"),

    path('accounts/create-user/form/', views.add_user_form, name='add_user_form'),
    path('accounts/add_user/', views.add_user, name="add_user"),

    path('accounts/edit-profile/form/<int:pk>', views.edit_profile_form, name='edit_profile_form'),
    path('accounts/edit-profile/<int:pk>/', views.edit_profile, name="edit_profile"),

    path('accounts/read-user/<int:pk>', views.read_profile, name='read_profile'),
    path('accounts/delete-user/<int:pk>', views.delete_user, name='delete_user'),
]
