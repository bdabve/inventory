from django.urls import path
from . import views

app_name = 'magasin'

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),                                           # dashboard
    path('magasin', views.article_list, name='article_list'),                                       # list of all articles
    path('magasin/<slug:category_slug>/', views.article_list, name='article_list_by_category'),     # list of articles by category
    path('magasin/stock_alarm/<int:stock_alarm>', views.article_list, name='stock_alarm'),          # stock alarm
    path('magasin/art_sans_prix/<int:art_sans_prix>', views.article_list, name='art_sans_prix'),    # Qte Sans prix

    path('magasin/<int:art_id>/<slug:slug>/', views.article_detail, name='article_detail'),            # article details

    # Django-bootstrap-modal-forms URLS
    path('read-article/<int:art_id>/<slug:slug>', views.read_article, name='read_article'),   # article detail boots modal
    #######
    path('category/form/', views.category_form_partial, name='category_form_partial'),
    path('create-category/', views.create_category, name='create_category'),                       # create category
    ######

    path('article/form/', views.article_form_partial, name='article_form_partial'),
    path('create-article/', views.create_article, name='create_article'),                          # create article

    path('edit-article/form/<int:art_id>/<slug:slug>', views.update_form_partial, name='update_form_partial'),
    path('update-article/<int:art_id>/<slug:slug>', views.update_article, name='update_article'),  # update article

    path('delete-article/<int:art_id>/<slug:slug>', views.delete_article, name='delete_article'),  # delete article

    # Django-bootstrap-modal-forms with custom view
    path('entree-article/<int:art_id>/<slug:slug>', views.entree_article_view, name='entree'),      # new entry
    path('sortie-article/<int:art_id>/<slug:slug>', views.sortie_article_view, name='sortie'),      # new sortie

    # History
    path('magasin/history', views.magasin_log, name='magasin_log'),                         # article history
    path('magasin/history/<int:art_id>/', views.magasin_log, name='magasin_log_article'),   # article history

    # Movement
    path('magasin/movement', views.movement, name='movement'),                          # All movement
    path('magasin/movement/<int:art_id>/', views.movement, name='movement_article'),    # Movement by article.
    path('magasin/movement/etats', views.etats, name='etats'),                          # etats journalier, mensuel
    path('delete-movement/<int:pk>/', views.DeleteMovementView.as_view(), name='delete_movement'),  # delete movement

    # this url is a django-bootstrap-modal with custom view
    path('magasin/total_article', views.total_articles, name='total_articles'),

    # commands urls
    path('magasin/commands', views.manage_command, name='manage_command'),                    # all commands
    path('magasin/commands/<int:command_id>', views.manage_command, name='manage_command'),   # Active Command
    path('create-command/', views.CreateCommandView.as_view(), name='create_command'),        # create command
    path('read-command/<int:pk>', views.ReadCommand.as_view(), name='read_command'),   # Commande Details

    # Gestion Stocks
    # path('magasin/gestion_stocks', views.gestion_stocks, name='gestion_stocks'),                          # all movement
]
