from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/manage-users/', views.manage_users, name="manage_users"),
    path('accounts/add_user/', views.add_user, name="add_user"),
    path('accounts/profile/edit-profile/<int:id>/', views.edit_profile, name="edit_profile"),

    path('read-article/<int:pk>', views.ReadProfile.as_view(), name='read_profile'),   # article detail boots modal
    path('delete-user/<int:pk>', views.DeleteUserView.as_view(), name='delete_user'),  # delete article
]
