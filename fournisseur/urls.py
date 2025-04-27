from django.urls import path
from . import views

app_name = 'fournisseur'

urlpatterns = [
    path('fournisseur', views.fourniss_list, name='fourniss_list'),
    path('fournisseur/create_fournis', views.create_fournis, name='create_fournis'),
    path('fournisseur/read-fourniss/<int:pk>', views.read_fournisseur, name='read_fournis'),
    path('fournisseur/update-fourniss/<int:pk>', views.update_fourniss, name='update_fourniss'),
    path('fournisseur/delete-fourniss/<int:pk>', views.delete_fourniss, name='delete_fourniss'),

    path('fournisseur/fournisseur_detail/<int:fourniss_id>', views.fourniss_detail, name='fourniss_detail'),
]
