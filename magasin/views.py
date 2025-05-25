import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, Http404
from django.utils.timezone import now

from django.db import transaction
from django.db.models import Q, Count, Sum, F
from django.contrib.auth.models import User
from accounts.models import Profile

from . import forms
from . import models
from . import functions
import pandas as pd
from datetime import date


@login_required
def dashboard(request):
    hijri = functions.hijri_()
    nbar = 'dashboard'

    # Articles Statistics
    total_command = models.Command.objects.count()
    total_articles = models.Article.objects.count()
    stock_alarm = models.Article.objects.filter(qte=0).count()
    total_valeur = models.Article.objects.aggregate(total_valeur=Sum('valeur'))['total_valeur']
    pending_command = models.Command.objects.filter(status=0).select_related('user_id')
    latest_movement = models.Movement.objects.order_by('-movement_date')[:5]
    # Users Statistics
    today = now().date()
    current_month = now().month

    # total users
    total_users = User.objects.count()
    users_today = User.objects.filter(date_joined__date=today).count()
    users_month = User.objects.filter(date_joined__month=current_month).count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    group_counts = list(Profile.objects.values('groupe').annotate(count=Count('groupe')))
    job_title_counts = list(Profile.objects.values('poste_travaille').annotate(count=Count('poste_travaille')))

    from django.core.serializers.json import DjangoJSONEncoder
    import json

    context = {
        'nbar': nbar, 'hijri': hijri,
        'total_articles': total_articles,
        'total_valeur': total_valeur,
        'stock_alarm': stock_alarm,
        'total_command': total_command,
        'pending_command': pending_command,
        'latest_movement': latest_movement,
        # users
        'total_users': total_users,
        'users_today': users_today,
        'users_this_month': users_month,
        'active_users': active_users,
        'inactive_users': inactive_users,
    }
    context['group_counts_json'] = json.dumps(group_counts, cls=DjangoJSONEncoder)
    context['job_title_counts_json'] = json.dumps(job_title_counts, cls=DjangoJSONEncoder)

    return render(request, 'magasin/article/dashboard.html', context)


@login_required
def article_list(request, category_slug=None, stock_alarm=False, art_sans_prix=False):
    nbar = 'magasin'
    hijri = functions.hijri_()
    search_word = None
    categories = models.Category.objects.all()

    # Search for an article
    if request.method == 'POST':
        search_article_form = forms.SearchForm(request.POST)
        if search_article_form.is_valid():
            search_word = search_article_form.cleaned_data['search_word']
    else:
        search_article_form = forms.SearchForm()

    # filtering and searching for article
    articles, category, count = functions.filter_articles(
        search_word=search_word,
        category_slug=category_slug,
        stock_alarm=stock_alarm,
        art_sans_prix=art_sans_prix
    )

    # Add pagination to our site
    # instantiate the Paginator with the number of objects to display
    paginator = Paginator(articles, 30)
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
        'stock_alarm': stock_alarm,
        'count': count,
        'search_word': search_word
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

    # art_movement = models.Movement.objects.filter(art_id=art_id) or ''
    art_movement = models.Movement.objects.filter(art_id=art_id) or 'empty'
    art_cmd = models.Command.objects.filter(art_id=art_id) or 'empty'
    art_history = models.MagasinLog.objects.filter(art_id=art_id) or 'empty'

    if art_history != 'empty': history = True
    if art_movement: movement = True

    # Search for article with code
    if request.method == 'POST' and 'search_form' in request.POST:
        search_form = forms.SearchForm(request.POST)
        if search_form.is_valid():
            code = search_form.cleaned_data['search_word'].upper()
            try:
                art = models.Article.objects.get(code=code)
                return redirect('magasin:article_detail', art_id=art.art_id, slug=art.slug)
            except models.Article.DoesNotExist:
                messages.warning(request, f'Aucun article trouvé avec le code « {code} »')
                return redirect('magasin:article_detail', art_id=art_id, slug=slug)
    else:
        search_form = forms.SearchForm()

    # ----------------------------------------------------------------
    # Entree form
    # ----------------
    # ----------------------------------------------------------------
    # Modification form
    # ----------------
    if request.method == 'POST' and 'update_art' in request.POST:
        update_art_form = forms.ArticalForm(request.POST, instance=article)
        if update_art_form.is_valid():
            article.save()
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
                art_id=article, user_id=request.user,
                command_date=cd['cmnd_date'], qte=cd['cmnd_qte']
            )

            messages.info(request, 'Commande Ajouter avec Succés')
            return redirect('magasin:article_detail', art_id=article.art_id, slug=article.slug)
    else:
        command_form = forms.CreateCommandForm()

    context = {
        'hijri': hijri,
        'article': article,
        'history': history,
        'movement': movement,
        'search_form': search_form,
        'article_mov': art_movement,
        'art_history': art_history,
        'art_cmd': art_cmd,             # commande
        'update_art_form': update_art_form,
        'command_form': command_form,
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


# == Edit Category
def update_category(request, cat_id):
    category = get_object_or_404(models.Category, cat_id=cat_id)
    if request.method == 'POST':
        form = forms.CreateCategoryForm(request.POST, instance=category)
        if form.is_valid():
            updated_category = form.save()
            return JsonResponse(
                {
                    'success': True,
                    'message': f'✅ Catégory {updated_category.name} Modifier avec succés.'
                }
            )
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.CreateCategoryForm(instance=category)

    context = {'form': form, 'category': category}
    return render(request, 'magasin/article/update_category.html', context)


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
@login_required
def create_article(request):
    today = date.today()
    if request.method == 'POST':
        form = forms.ArticalForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
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
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Erreur lors de l\'ajout de l\'article: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = forms.ArticalForm()

    return render(request, 'magasin/article/create_article.html', {'form': form})


# 📥 Upload Multiple Articles from Excel
@login_required
def upload_articles_from_excel(request):
    today = date.today()

    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)

            required_columns = ['category', 'code', 'designation', 'ref', 'qte', 'prix']
            if not all(col in df.columns for col in required_columns):
                return JsonResponse({'success': False, 'message': '❌ Fichier invalide. Vérifiez les colonnes.'})

            errors = []
            for idx, row in df.iterrows():
                category_name = row.get('category')
                if not category_name:
                    errors.append(f"Ligne {idx + 2}: La catégorie est manquante.")
                    continue

                try:
                    category = models.Category.objects.get(name__iexact=category_name)
                except models.Category.DoesNotExist:
                    errors.append(f"Ligne {idx + 2}: Catégorie « {category_name} » introuvable.")
                    continue

                try:
                    with transaction.atomic():
                        article = models.Article.objects.create(
                            category=category,
                            code=row['code'],
                            designation=row['designation'],
                            ref=row['ref'],
                            qte=row['qte'],
                            prix=row['prix'],
                        )
                    models.Movement.objects.create(
                        art_id=article,
                        movement_date=today,
                        user_id=request.user,
                        movement="Initial",
                        qte=row['qte'],
                        prix=row['prix'],
                    )
                except Exception as err:
                    errors.append(f"Ligne {idx + 2}: Erreur: {str(err)}")

            if errors:
                return JsonResponse(
                    {
                        'success': False,
                        'message': '❌ Certaines lignes contiennent des erreurs.',
                        'errors': errors
                    }
                )

            return JsonResponse({'success': True, 'message': '✅ Tous les articles ont été ajoutés avec succès.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'❌ Erreur lors de la lecture du fichier: {str(e)}'})

    return render(request, 'magasin/article/multiple_articles.html')


def download_exemple_articles(request):
    file_path = os.path.join(settings.BASE_DIR, 'magasin/static', 'img', 'exemple_articles.ods')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='exemple_articles.xlsx')
    else:
        raise Http404("Fichier non trouvé.")


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
            return JsonResponse(
                {
                    'success': True,
                    'message': f'✅ Article {updated_article.code} Modifier avec succés.'
                }
            )
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
# ==> Article Entree Ajax Bs-modal
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

            result = functions.process_stock_entry(article, new_qte, new_prix, entree_date, request.user)
            if result:
                return JsonResponse({'success': True, 'message': f'✅ Entrée ajoutée avec succès code article {article.code}.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.EntreeForm()
    return render(request, 'magasin/article/entree.html', {'article': article, 'form': form})


# -----------------------------
# ==> Article Sortie AJAX Bs-modal
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

            result = functions.process_stock_sortie(article, sortie_qte, sortie_date, request.user)
            if result:
                return JsonResponse({'success': True, 'message': f'✅ Sortie ajoutée avec succès article {article.code}.'})
            else:
                return JsonResponse({'success': False, 'message': result})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.SortieForm()
    return render(request, 'magasin/article/sortie.html', {'article': article, 'form': form})


def missing_code_finder(request):
    if request.method == 'GET':
        cat_id = request.GET.get('cat_id')
        try:
            category = models.Category.objects.get(pk=cat_id)
            articles = models.Article.objects.filter(category=category)
            existing_codes = articles.values_list('code', flat=True)

            # Extract numbers from codes like 'aro-001'
            existing_numbers = []
            len_numbers = 0
            for code in existing_codes:
                if '-' in code:
                    num_part = code.split('-')[1]
                    len_numbers = len(num_part)
                    if num_part.isdigit():
                        existing_numbers.append(int(num_part))

            # Find the first missing number
            number = 1
            while number in existing_numbers:
                number += 1

            # Generate code
            empty_code = f"{category.slug}-{number:0{len_numbers}d}"
            return JsonResponse({'success': True, 'empty_code': empty_code, 'message': f'✅ Code libre trouvé : {empty_code}'})

        except models.Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': '❌ Catégorie introuvable.'})
    else:
        return JsonResponse({'success': False, 'message': '❌ Requête invalide.'})


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


def create_commande(request, art_id):
    article = get_object_or_404(models.Article, art_id=art_id)
    if request.method == 'POST':
        form = forms.CreateCommandForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            models.Command.objects.create(
                art_id=article, user_id=request.user,
                command_date=cd['cmnd_date'], qte=cd['cmnd_qte']
            )
            return JsonResponse({'success': True, 'message': '✅ Commande Enregistrés avec succés'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = forms.CreateCommandForm()
    context = {'form': form, 'article': article}
    return render(request, 'magasin/article/create_commande.html', context)
