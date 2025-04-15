from django.urls import path
from . import views

app_name = 'fournisseur'

urlpatterns = [
    path('fournisseur', views.fourniss_list, name='fourniss_list'),
    path('fournisseur/add_fourniss', views.add_fournisseur, name='add_fourniss'),
    path('fournisseur/fournisseur_detail/<int:fourniss_id>', views.fourniss_detail, name='fourniss_detail'),

    path('read-fourniss/<int:pk>', views.ReadFourniss.as_view(), name='read_fourniss'),    # article detail boots modal
    path('create-fourniss/', views.CreateFournissView.as_view(), name='create_fourniss'),  # create article
]
