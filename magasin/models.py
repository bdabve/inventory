from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
# from django.core.exceptions import ValidationError


class Category(models.Model):
    cat_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, db_index=True, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
            self.slug = slugify(self.name.lower())
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('magasin:article_list_by_category', args=[self.slug])


class Article(models.Model):
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE)
    art_id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=200, db_index=True)
    designation = models.CharField(max_length=255, db_index=True, null=True)
    code = models.CharField(max_length=100, db_index=True, unique=True)
    ref = models.CharField(max_length=255, db_index=True, null=True)
    umesure = models.CharField(max_length=50, null=True)
    emp = models.CharField(max_length=50, null=True)
    qte = models.PositiveIntegerField()
    prix = models.DecimalField(decimal_places=2, max_digits=15)
    valeur = models.DecimalField(decimal_places=2, max_digits=20, null=True)
    observation = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('code', 'ref', 'designation')

    def __str__(self):
        return 'CODE: {}; DESIG: {}; REF :{}; QTE :{}; PRIX: {}'.format(self.code, self.designation, self.ref, self.qte, self.prix)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.slug = slugify(self.code.lower())
        self.emp = self.emp.upper()
        self.valeur = (self.qte * self.prix)
        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('magasin:article_detail', args=[self.art_id, self.slug])


class MagasinLog(models.Model):
    log_date = models.DateTimeField()
    operation = models.CharField(max_length=30)
    art_id = models.IntegerField(db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    designation = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    code = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    ref = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    umesure = models.CharField(max_length=50, null=True, blank=True)
    emp = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('log_date', 'slug')

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.slug = self.code.lower()
        self.emp = self.emp.upper()
        super(MagasinLog, self).save(*args, **kwargs)

    def __str__(self):
        return '{}: {} {}'.format(self.log_date, self.art_id, self.operation)


class Movement(models.Model):
    movement_id = models.AutoField(primary_key=True)
    art_id = models.ForeignKey(Article, related_name='article_id', db_index=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='mov_user_id', on_delete=models.CASCADE)
    movement_date = models.DateTimeField()
    movement_choice = (('entree', 'Entree'), ('sortie', 'Sortie'), ('initial', 'Initial'))
    movement = models.CharField(max_length=10, choices=movement_choice)
    qte = models.PositiveIntegerField(null=True)
    prix = models.DecimalField(decimal_places=2, max_digits=15, null=True)
    valeur = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    class Meta:
        ordering = ('-movement_date',)          # order by movement_date DESC

    def __str__(self):
        return 'Movement({}, {})'.format(self.movement_date, self.art_id)

    def save(self, *args, **kwargs):
        self.valeur = (self.qte * self.prix)
        super(Movement, self).save(*args, **kwargs)


class Command(models.Model):
    command_id = models.AutoField(primary_key=True)
    art_id = models.ForeignKey(Article, related_name='command_art_id', db_index=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='command_user_id', on_delete=models.CASCADE)
    command_date = models.DateTimeField()
    qte = models.PositiveIntegerField(null=True)
    status = models.PositiveSmallIntegerField(default=0)


# class GestionStocks(models.Model):
    # gs_id = models.AutoField(primary_key=True)
    # art_id = models.ForeignKey(Article, related_name='gs_art_id', db_index=True, on_delete=models.CASCADE)
    # gs_date = models.DateTimeField()

    # ent_qte = models.PositiveIntegerField(null=True)
    # ent_prix = models.DecimalField(decimal_places=2, max_digits=15, null=True)
    # ent_valeur = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    # srt_qte = models.PositiveIntegerField(null=True)
    # srt_prix = models.DecimalField(decimal_places=2, max_digits=15, null=True)
    # srt_valeur = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    # sf_qte = models.PositiveIntegerField(null=True)
    # sf_prix = models.DecimalField(decimal_places=2, max_digits=15, null=True)
    # sf_valeur = models.DecimalField(decimal_places=2, max_digits=20, null=True)

    # class Meta:
        # ordering = ('gs_date', 'gs_id', 'art_id')

    # def __str__(self):
        # return 'GestionStocks({}, {}, {})'.format(self.gs_id, self.gs_date, self.art_id)

    # def save(self, *args, **kwargs):
        # self.ent_valeur = (self.ent_qte * self.ent_prix)

        # self.srt_valeur = (self.srt_qte * self.srt_prix)

        # self.sf_qte = (self.ent_qte - self.srt_qte)
        # self.sf_valeur = (self.sf_qte * self.sf_prix)
        # super(GestionStocks, self).save(*args, **kwargs)
