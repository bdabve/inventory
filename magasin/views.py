from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.db.models import Q
from django.db.models import Count, Sum, F
from . import forms
from . import models
from . import functions
import pandas as pd
from datetime import date


@login_required
def dashboard(request):
    hijri = functions.hijri_()
    nbar = 'dashboard'
    total_command = models.Command.objects.aggregate(command_count=Count('command_id'))
    total_articles = models.Article.objects.aggregate(article_count=Count('art_id'))
    total_valeur = models.Article.objects.aggregate(total_valeur=Sum('valeur'))
    stock_alarm = models.Article.objects.filter(qte=0).aggregate(stock_alarm=Count('art_id'))
    pending_command = models.Command.objects.filter(status=0)
    latest_movement = models.Movement.objects.all().order_by('-movement_date')[:5]

    context = {
        'nbar': nbar, 'hijri': hijri,
        'total_articles': total_articles,
        'total_valeur': total_valeur,
        'stock_alarm': stock_alarm,
        'total_command': total_command,
        'pending_command': pending_command,
        'latest_movement': latest_movement
    }
    return render(request, 'magasin/article/dashboard.html', context)


@login_required
def article_list(request, category_slug=None, stock_alarm=False, art_sans_prix=False):
    hijri = functions.hijri_()
    nbar = 'magasin'
    category = None
    categories = models.Category.objects.all()
    articles = models.Article.objects.all()

    if stock_alarm:
        articles = models.Article.objects.filter(qte=0)

    if art_sans_prix:
        articles = models.Article.objects.filter(prix=0)

    if category_slug:
        category = get_object_or_404(models.Category, slug=category_slug)
        articles = articles.filter(category=category)

    # Search for an article
    if request.method == 'POST':
        search_article_form = forms.SearchArticleForm(request.POST)     # PdrSearchForm comme from forms.py file
        if search_article_form.is_valid():
            search_word = search_article_form.cleaned_data['search_word']
            articles = models.Article.objects.filter(
                Q(designation__icontains=search_word) |
                Q(code__icontains=search_word) |
                Q(ref__icontains=search_word)
            ).select_related('category')
    else:
        search_article_form = forms.SearchArticleForm()

    # Add pagination to our site
    paginator = Paginator(articles, 30)     # instantiate the Paginator with the number of objects to display
    page = request.GET.get('page')          # indicate the current page number.

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        articles = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver last page of results
        articles = paginator.page(paginator.num_pages)

    context = {
        'nbar': nbar, 'hijri': hijri,
        'category': category,
        'categories': categories,
        'articles': articles,
        'search_article_form': search_article_form,
        'page': page,
        'stock_alarm': stock_alarm
    }
    return render(request, 'magasin/article/list.html', context)


# ----------------------------------------------------------------------
# ==> Articles Views
# ------------------------
#
# ==> Article Details View
@login_required
def article_detail(request, art_id, slug, history=False, movement=False):
    hijri = functions.hijri_()
    article = get_object_or_404(models.Article, art_id=art_id, slug=slug)
    article_movement = models.Movement.objects.filter(art_id=art_id)
    article_command = models.Command.objects.filter(art_id=art_id)

    # if movment; than display all command related with article
    if article_movement:
        article_mov = article_movement
    else:
        article_mov = 'empty'

    # if commande; than display all command related with article
    if article_command:
        art_cmd = article_command
    else:
        art_cmd = 'empty'

    art_history = models.MagasinLog.objects.filter(art_id=art_id)
    art_movement = models.Movement.objects.filter(art_id=art_id)

    # Search for article with code
    if request.method == 'POST' and 'search_form' in request.POST:
        search_form = forms.SearchArticleForm(request.POST)
        if search_form.is_valid():
            code = search_form.cleaned_data['search_word'].upper()
            try:
                art = models.Article.objects.get(code=code)
                return redirect('magasin:article_detail', art_id=art.art_id, slug=art.slug)
            except models.Article.DoesNotExist:
                messages.warning(request, f'Aucun article trouvé avec le code « {code} »')
                return redirect('magasin:article_detail', art_id=art_id, slug=slug)
    else:
        search_form = forms.SearchArticleForm()

    # ----------------------------------------------------------------
    # Entree form
    # ----------------
    if request.method == 'POST' and 'entree_form' in request.POST:
        entree_form = forms.EntreeForm(request.POST)     # PdrSearchForm comme from forms.py file
        if entree_form.is_valid():
            # form fields passed validation
            new_qte = entree_form.cleaned_data['qte']      # retrieve the user input form
            new_prix = entree_form.cleaned_data['prix']
            entree_date = entree_form.cleaned_data['entree_date']

            # Save movement in Movement table
            models.Movement.objects.create(
                art_id=article,
                movement_date=entree_date,
                user_id=request.user,
                movement="Entree",
                qte=new_qte,
                prix=new_prix,
            )

            # save in main Article table
            if article.prix == new_prix:
                # if prix is equal to old prix; only add quantity
                article.qte = F('qte') + new_qte
                article.save()

            else:
                # if prix is not equal to old prix; modify prix
                # prix = ( sum(valeur) / sum(qte)); cout moyen penduré
                total_val = (new_qte * new_prix) + (article.valeur or 0)
                total_qte = article.qte + new_qte
                article.prix = total_val / total_qte
                article.qte = F('qte') + new_qte
                article.save()

            messages.info(request, 'Entree Ajouter avec Succés')
            return redirect('magasin:article_detail', art_id=article.art_id, slug=article.slug)
    else:
        entree_form = forms.EntreeForm()
    # ----------------------------------------------------------------
    # Sortie form
    # ----------------
    if request.method == 'POST' and 'sortie_form' in request.POST:
        sortie_form = forms.SortieForm(request.POST)     # PdrSearchForm comme from forms.py file
        if sortie_form.is_valid():
            # form fields passed validation
            sortie_qte = sortie_form.cleaned_data['qte']      # retrieve the user input form
            article.qte = F('qte') - sortie_qte
            sortie_date = sortie_form.cleaned_data['sortie_date']
            # Save movement in Movement table
            models.Movement.objects.create(
                art_id=article,
                user_id=request.user,
                movement_date=sortie_date,
                movement="Sortie",
                qte=sortie_qte,
                prix=article.prix,
            )
            article.save()
            messages.info(request, 'Sortie Enregistrés avec Succés.')
            return redirect('magasin:article_detail', art_id=article.art_id, slug=article.slug)
    else:
        sortie_form = forms.SortieForm()

    # ----------------------------------------------------------------
    # Modification form
    # ----------------
    if request.method == 'POST' and 'update_art' in request.POST:
        update_art_form = forms.ArticalForm(request.POST, instance=article)
        if update_art_form.is_valid():
            update_art_form.save()
            # article.save()
            messages.info(request, 'Article Modifier avec Succés')
            return redirect('magasin:article_detail', art_id=article.art_id, slug=article.slug)
    else:
        update_art_form = forms.ArticalForm(instance=article)

    # ----------------------------------------------------------------
    # commande form
    # this is the place where create a new commande
    # ----------------
    if request.method == 'POST' and 'cmnd_form' in request.POST:
        command_form = forms.CreateCommandForm(request.POST)     # PdrSearchForm comme from forms.py file
        if command_form.is_valid():
            # form fields passed validation
            cd = command_form.cleaned_data
            models.Command.objects.create(
                art_id=article,
                user_id=request.user,
                command_date=cd['cmnd_date'],
                qte=cd['cmnd_qte']
            )

            messages.info(request, 'Commande Ajouter avec Succés')
            return redirect('magasin:article_detail', art_id=article.art_id, slug=article.slug)
    else:
        command_form = forms.CreateCommandForm()

    if art_history: history = True
    if art_movement: movement = True

    context = {
        'hijri': hijri,
        'article': article,
        'history': history,
        'movement': movement,
        'article_mov': article_mov,
        'art_cmd': art_cmd,             # commande
        'search_form': search_form,
        'entree_form': entree_form,
        'sortie_form': sortie_form,
        'update_art_form': update_art_form,
        'command_form': command_form
    }

    return render(request, 'magasin/article/detail.html', context)


# -----------------------------------------------------
# ==> Create Category View
@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        form = forms.CreateCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return JsonResponse({'success': True, 'message': f"✅ Category {category.name} Enregistrés avec succés"})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.CreateCategoryForm()

    return render(request, 'magasin/article/create_category.html', {'form': form})


# == Delete Category
def delete_category(request, cat_id):
    if request.method == 'POST':
        category = get_object_or_404(models.Category, cat_id=cat_id)
        cat_name = category.name
        category.delete()
        return JsonResponse({'success': True, 'message': f"✅ Catégorie {cat_name} supprimée avec succés."})
    else:
        return JsonResponse({'success': False, 'error': "❌ Une erreur s’est produite"})


# -----------------------------------------------------
# ==> Create Article View
@csrf_exempt
def create_article(request):
    today = date.today()
    if request.method == 'POST':
        form = forms.ArticalForm(request.POST)
        if form.is_valid():
            article = form.save()
            # Save initial movement in Movement table
            models.Movement.objects.create(
                art_id=article,
                movement_date=today,
                user_id=request.user,
                movement="Initial",
                qte=form.cleaned_data['qte'],
                prix=form.cleaned_data['prix'],
            )
            return JsonResponse({'success': True, 'message': f'✅ Article {article.code} Enregistrés avec succés'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.ArticalForm()

    return render(request, 'magasin/article/create_article.html', {'form': form})


def upload_articles_from_excel(request):
    """Multiple article from excel"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)

            required_columns = ['category', 'code', 'designation', 'ref', 'qte', 'prix']  # example
            if not all(col in df.columns for col in required_columns):
                return JsonResponse({'success': False, 'message': '❌ Fichier invalide. Vérifiez les colonnes.'})

            for _, row in df.iterrows():
                category_name = row.get('category')  # Or adjust based on your column name
                if category_name:
                    try:
                        category = models.Category.objects.get(name__iexact=category_name)
                    except models.Category.DoesNotExist:
                        return JsonResponse({'success': False, 'message': f"Catégorie « {category_name} » introuvable."})
                else:
                    return JsonResponse({'success': False, 'message': "La catégorie est requise."})

                models.Article.objects.create(
                    category=category,
                    code=row['code'],
                    designation=row['designation'],
                    ref=row['ref'],
                    qte=row['qte'],
                    prix=row['prix'],
                )

            return JsonResponse({'success': True, 'message': '✅ Articles ajoutés avec succès.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})

    return render(request, 'magasin/article/multiple_articles.html')  # HTML for the modal content


# ==> Read Article View (bootstrap-modal-form)
def read_article(request, art_id, slug):
    article = get_object_or_404(models.Article, art_id=art_id, slug=slug)
    return render(request, 'magasin/article/read_article.html', {'article': article})


# ==> Update Article View (bootstrap-modal-form)
def update_article(request, art_id, slug):
    article = get_object_or_404(models.Article, art_id=art_id, slug=slug)
    if request.method == 'POST':
        form = forms.ArticalForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save()
            return JsonResponse({'success': True, 'message': f'✅ Article {updated_article.code} Modifier avec succés.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.ArticalForm(instance=article)

    return render(request, 'magasin/article/update_article.html', {'form': form, 'article': article})


# ==> Delete Article View (bootstrap-modal-form)
def delete_article(request, art_id):
    if request.method == 'POST':
        article = get_object_or_404(models.Article, art_id=art_id)
        article.delete()
        return JsonResponse({'success': True, 'message': f'✅ Article {article.code} supprimé avec succés.'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# -----------------------------
# ==> New Entree Ajax Bs-modal
@login_required
def entree_article_ajax(request, art_id):
    article = get_object_or_404(models.Article, art_id=art_id)
    if request.method == 'POST':
        form = forms.EntreeForm(request.POST)     # PdrSearchForm comme from forms.py file

        if form.is_valid():
            # form fields passed validation
            new_qte = form.cleaned_data['qte']      # retrieve the user input form
            new_prix = form.cleaned_data['prix']
            entree_date = form.cleaned_data['entree_date']

            # Save movement in Movement table
            models.Movement.objects.create(
                art_id=article,
                movement_date=entree_date,
                user_id=request.user,
                movement="Entree",
                qte=new_qte,
                prix=new_prix,
            )

            # save in database
            if article.prix == new_prix:
                # if prix is equal to old prix; only add quantity
                article.qte = F('qte') + new_qte
            else:
                # if prix is not equal to old prix; than prix = ( sum(valeur) / sum(qte)); cout moyen penduré
                total_val = (new_qte * new_prix) + (article.valeur or 0)
                total_qte = article.qte + new_qte
                article.prix = total_val / total_qte
                article.qte = F('qte') + new_qte

            article.save()
            return JsonResponse({'success': True, 'message': f'✅ Entrée ajoutée avec succès code article {article.code}.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.EntreeForm()
    return render(request, 'magasin/article/entree.html', {'article': article, 'form': form})


# -----------------------------
# ==> New Sortie AJAX Bs-modal
@login_required
def sortie_article_ajax(request, art_id):
    article = get_object_or_404(models.Article, art_id=art_id)
    if request.method == 'POST':
        form = forms.SortieForm(request.POST)     # PdrSearchForm comme from forms.py file
        if form.is_valid():
            # form fields passed validation
            sortie_qte = form.cleaned_data['qte']      # retrieve the user input form
            sortie_date = form.cleaned_data['sortie_date']
            article.qte = F('qte') - sortie_qte

            # Save movement in Movement table
            models.Movement.objects.create(
                art_id=article,
                user_id=request.user,
                movement_date=sortie_date,
                movement="Sortie",
                qte=sortie_qte,
                prix=article.prix,
            )

            article.save()
            return JsonResponse({'success': True, 'message': f'✅ Sortie ajoutée avec succès code article {article.code}.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.SortieForm()
    return render(request, 'magasin/article/sortie.html', {'article': article, 'form': form})


# ----------------------------------------------------------------------
# ==> History view
# -----------------
@login_required
def magasin_log(request, art_id=None):
    hijri = functions.hijri_()
    nbar = 'history'
    if art_id:
        articles = get_list_or_404(models.MagasinLog, art_id=art_id)
    else:
        articles = models.MagasinLog.objects.all()

    context = {'articles': articles, 'hijri': hijri, 'nbar': nbar}
    return render(request, 'magasin/article/history.html', context)


# -------------------------------------------------------------------
# ==> Movement view
# ----------------------------
@login_required
def movement(request, art_id=None):
    hijri = functions.hijri_()
    nbar = 'movement'
    if art_id:
        articles = get_list_or_404(models.Movement, art_id=art_id)
    else:
        articles = models.Movement.objects.select_related('art_id', 'user_id').all()

    # Search for an article
    if request.method == 'POST' and 'search_mov_form' in request.POST:
        search_movement_form = forms.SearchMovementForm(request.POST)
        if search_movement_form.is_valid():
            code = search_movement_form.cleaned_data.get('search_code')
            operation = search_movement_form.cleaned_data.get('operation')
            day = search_movement_form.cleaned_data.get('day')
            month = search_movement_form.cleaned_data.get('month')
            year = search_movement_form.cleaned_data.get('year')

            filters = Q()

            if code:
                article_qs = models.Article.objects.filter(code__icontains=code)
                if article_qs.exists():
                    filters &= Q(art_id__in=article_qs)
                else:
                    messages.warning(request, f"Aucun article trouvé avec le code « {code} »")
                    return redirect('magasin:movement')

            if operation:
                filters &= Q(movement=operation)

            if day:
                filters &= Q(movement_date=day)
            elif month and year:
                filters &= Q(movement_date__month=month, movement_date__year=year)
            elif year:
                filters &= Q(movement_date__year=year)

            articles = models.Movement.objects.filter(filters).order_by('-movement_date')
    else:
        search_movement_form = forms.SearchMovementForm()
        articles = models.Movement.objects.all()
    # ----------------------------------------------------------------
    # Etats
    if request.method == 'POST' and 'etat' in request.POST:
        etat_form = forms.Etats(request.POST)

        if etat_form.is_valid():
            par = etat_form.cleaned_data['par']
            date_ = etat_form.cleaned_data['etat_date']

            fields = ['movement_date', 'art_id__code', 'art_id__designation', 'movement', 'qte', 'prix', 'valeur']

            export_config = {
                'journalier': {
                    'queryset': models.Movement.objects.filter(movement_date=date_),
                    'filename': date_.strftime('%d_%B_%Y'),
                    'message': 'État journalier généré avec succès.'
                },
                'mensuel': {
                    'queryset': models.Movement.objects.filter(
                        movement_date__month=date_.month,
                        movement_date__year=date_.year
                    ),
                    'filename': date_.strftime('%m_%Y'),  # Format: 03_2025
                    'message': 'État mensuel généré avec succès.'
                },
                'tous': {
                    'queryset': models.Movement.objects.all(),
                    'filename': 'Tous_Les_Mouvements',
                    'message': 'État global généré avec succès.'
                }
            }

            config = export_config.get(par)
            if config:
                functions.write_to_excel_g(fields, config['queryset'], config['filename'])
                messages.success(request, config['message'])
                return redirect('magasin:movement')
    else:
        etat_form = forms.Etats()

    # Add pagination to our site
    paginator = Paginator(articles, 30)     # instantiate the Paginator with the number of objects to display
    page = request.GET.get('page')          # indicate the current page number.

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        articles = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver last page of results
        articles = paginator.page(paginator.num_pages)

    context = {
        'hijri': hijri, 'nbar': nbar,
        'articles': articles,
        'search_movement_form': search_movement_form,
        'etat_form': etat_form
    }
    return render(request, 'magasin/article/movement.html', context)


# --------------------
# ==> Delete Movement
@login_required
@require_POST
def delete_movement(request, pk):
    movement = get_object_or_404(models.Movement, movement_id=pk)
    try:
        movement.delete()
        return JsonResponse({'success': True, 'message': f'✅ Commande {pk} supprimé avec succés.'})
    except Exception as err:
        return JsonResponse({'success': False, 'error': f'Invalid request {err}'})


# ----------------------------------------------------------------------
# ==> Etats Des Stocks
# --------------------
@login_required
def etats(request):
    hijri = functions.hijri_()
    nbar = 'movement'
    if request.method == 'POST':
        etat_form = forms.Etats(request.POST)
        if etat_form.is_valid():
            par = etat_form.cleaned_data['par']
            date_ = etat_form.cleaned_data['date']
            # art_id__code, and art_id__designation: retrieve many_to_many fields
            desc = ['movement_date', 'art_id__code', 'art_id__designation', 'movement', 'qte', 'prix', 'valeur']

            if par == 'journalier':
                articles = models.Movement.objects.filter(movement_date__contains=date_).values_list(*desc)
                functions.write_to_excel(desc, articles, date_.strftime('%d_%B_%Y'))
                messages.info(request, 'Etat Journalier Ajouter')

            elif par == 'mensuel':
                articles = models.Movement.objects.filter(movement_date__month=date_.month).values_list(*desc)
                functions.write_to_excel(desc, articles, date_.strftime('%B_%Y'))
                messages.info(request, 'Etat Mensuel Ajouter')

            elif par == 'tous':
                articles = models.Movement.objects.all().values_list(*desc)
                functions.write_to_excel(desc, articles, 'Tous Les Movement')
                messages.info(request, 'Etat Tous Ajouter')
    else:
        etat_form = forms.Etats()

    context = {'etat_form': etat_form, 'hijri': hijri, 'nbar': nbar}
    return render(request, 'magasin/article/etats_.html', context)


# @login_required
# def gestion_stocks(request):
    # hijri = functions.hijri_()
    # articles = GestionStocks.objects.select_related('art_id').all()
    # context = {'hijri': hijri, 'articles': articles}
    # return render(request, 'magasin/article/gestion_stocks.html', context)


@login_required
def total_articles(request):
    hijri = functions.hijri_()
    total_article = models.Article.objects.aggregate(article_count=Count('art_id'))
    total_article_qte = models.Article.objects.aggregate(total_article_qte=Sum('qte'))
    total_valeur = models.Article.objects.aggregate(total_valeur=Sum('valeur'))

    context = {
        'hijri': hijri,
        'total_article': total_article,
        'total_article_qte': total_article_qte,
        'total_valeur': total_valeur
    }
    return render(request, 'magasin/article/total_article.html', context)


# ----------------------------------------------------------------------
# ==> Commande Page
# ------------------
@login_required
@require_POST
def activate_commande(request, pk):
    commande = get_object_or_404(models.Command, command_id=pk)
    commande.status = 1
    try:
        commande.save()
        return JsonResponse({'success': True, 'message': f'✅ Commande {commande.command_id} Modifier avec succés.'})
    except Exception as err:
        return JsonResponse({'success': False, 'errors': err})


@login_required
def manage_command(request):
    hijri = functions.hijri_()
    nbar = 'command'
    commandes = models.Command.objects.select_related('art_id', 'user_id').all()

    context = {'hijri': hijri, 'nbar': nbar, 'commandes': commandes}
    return render(request, 'magasin/article/manage_command.html', context)


# ==> Read Command (bootstrap-modal-form)
def read_commande(request, pk):
    commande = get_object_or_404(models.Command, command_id=pk)
    return render(request, 'magasin/article/read_command.html', {'commande': commande})


# ==> Update Commande AJAX
@login_required
def update_commande(request, pk):
    commande = get_object_or_404(models.Command, command_id=pk)
    if request.method == 'POST':
        form = forms.EditCommandeForm(request.POST, instance=commande)
        if form.is_valid():
            updated_commande = form.save()
            return JsonResponse(
                {
                    'success': True, 'message':
                    f'✅ Commande {updated_commande.command_id} Modifier avec succés.'
                }
            )
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.EditCommandeForm(instance=commande)
    return render(request, 'magasin/article/update_commande.html', {'form': form, 'commande': commande})


# ==> Delete Commande
def delete_commande(request, pk):
    commande = get_object_or_404(models.Command, command_id=pk)
    try:
        commande.delete()
        return JsonResponse({'success': True, 'message': f'✅ Commande {commande.command_id} supprimé avec succés.'})
    except Exception as err:
        return JsonResponse({'success': False, 'error': f'Invalid request {err}'})
