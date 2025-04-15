from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name', )}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['code', 'designation', 'ref', 'umesure', 'emp', 'qte', 'prix', 'valeur', 'category']
    search_fields = ['code']
    prepopulated_fields = {'slug': ('code', )}
    # list_filter = ['code', 'designation', 'ref']
    # list_editable = ['code', 'designation', 'ref', 'umesure', 'emp', 'qte', 'prix', 'valeur']

    # fields for CRUD forms order
    fields = ['category', ('code', 'slug'), ('designation', 'ref'), ('umesure', 'emp'), ('qte', 'prix', 'valeur')]

    list_per_page = 20  # pagination 20 article per page
