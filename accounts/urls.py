from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/manage-users/', views.manage_users, name="manage_users"),
    path('accounts/search-users/', views.ajax_search_users, name='ajax_search_users'),

    path('accounts/create-user/', views.create_user, name="create_user"),
    path('accounts/edit-profile/<int:pk>/', views.edit_profile, name="edit_profile"),
    path('accounts/read-user/<int:pk>', views.read_profile, name='read_profile'),
    path('accounts/change-user-group/<int:pk>', views.change_user_group, name='change_user_group'),

    path('accounts/delete-user/<int:pk>', views.delete_user, name='delete_user'),
]
