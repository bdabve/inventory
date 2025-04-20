from django.urls import path
from . import views

app_name = 'magasin'

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),                                           # dashboard

    # Magasin URLS
    path('magasin', views.article_list, name='article_list'),
    path('magasin/<slug:category_slug>/', views.article_list, name='article_list_by_category'),
    # STOCK ALARM
    path('magasin/stock_alarm/<int:stock_alarm>', views.article_list, name='stock_alarm'),
    # Article Sans Prix
    path('magasin/art_sans_prix/<int:art_sans_prix>', views.article_list, name='art_sans_prix'),
    # Total des Articles
    path('magasin/total_article', views.total_articles, name='total_articles'),

    # Article Details
    path('magasin/<int:art_id>/<slug:slug>/', views.article_detail, name='article_detail'),

    # Category
    path('magasin/category/form/', views.category_form_partial, name='category_form_partial'),
    path('magasin/create-category', views.create_category, name='create_category'),
    path('magasin/delete-category/<slug:slug>', views.delete_category, name="delete_category"),

    # Read Article
    path('magasin/read-article/<int:art_id>/<slug:slug>', views.read_article, name='read_article'),

    # Edit Article
    path('magasin/edit-article/form/<int:art_id>/<slug:slug>', views.update_form_partial, name='update_form_partial'),
    path('magasin/update-article/<int:art_id>/<slug:slug>', views.update_article, name='update_article'),

    # Article
    path('magasin/article/form/', views.article_form_partial, name='article_form_partial'),
    path('magasin/create-article', views.create_article, name='create_article'),
    # Delete Article
    path('magasin/delete-article/<int:art_id>/<slug:slug>', views.delete_article, name='delete_article'),

    # Entree, Sortie Article Bs-Model
    path('magasin/entree/form/<int:art_id>/<slug:slug>', views.entree_form_partial, name='entree_form_partial'),
    path('magasin/entree-article/<int:art_id>/<slug:slug>', views.entree_article_ajax, name='entree_ajax'),      # new entry
    path('magasin/sortie/form/<int:art_id>/<slug:slug>', views.sortie_form_partial, name='sortie_form_partial'),
    path('magasin/sortie-article/<int:art_id>/<slug:slug>', views.sortie_article_ajax, name='sortie_ajax'),      # new sortie

    # -----------------------------------------------------------
    # History
    path('magasin/history', views.magasin_log, name='magasin_log'),                         # article history
    path('magasin/history/<int:art_id>/', views.magasin_log, name='magasin_log_article'),   # article history

    # -----------------------------------------------------------
    # Movement
    path('magasin/movement', views.movement, name='movement'),                          # All movement
    path('magasin/movement/<int:art_id>/', views.movement, name='movement_article'),    # Movement by article.
    path('magasin/movement/etats', views.etats, name='etats'),                          # etats journalier, mensuel

    # TODO:
    path('magasin/delete-movement/<int:pk>', views.delete_movement, name='delete_movement'),  # delete movement

    # -----------------------------------------------------------
    # Commands urls
    path('magasin/commands', views.manage_command, name='manage_command'),                    # all commands
    path('magasin/commands/<int:pk>', views.activate_commande, name='activate_commande'),   # Active Command
    path('read-command/<int:pk>', views.read_commande, name='read_commande'),   # Commande Details

    path('magasin/edit-commande/form/<int:pk>', views.edit_commande_form, name='edit_commande_form'),
    path('magasin/update-commande/<int:pk>', views.update_commande, name='update_commande'),

    path('magasin/delete-commande/<int:pk>', views.delete_commande, name='delete_commande'),

    # Gestion Stocks
    # path('magasin/gestion_stocks', views.gestion_stocks, name='gestion_stocks'),                          # all movement
]
