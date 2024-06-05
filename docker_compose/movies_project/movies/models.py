import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from psqlextra.models import PostgresModel


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name_genre'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=100)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'content"."person'
        verbose_name = _('person')
        verbose_name_plural = _('persons')


class Filmwork(UUIDMixin, TimeStampedMixin, PostgresModel):
    TYPE_CHOICES = [('MV', 'movie'), ('TV', 'tv_show')]
    title = models.CharField(_('title'), max_length=150)
    description = models.CharField(_('description'), max_length=300)
    creation_date = models.DateField(_('created_date'), auto_now_add=False)
    rating = models.FloatField(
        _('rating'),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_('type'), max_length=100, choices=TYPE_CHOICES)
    file_path = models.FileField(
        _('file'), blank=True, null=True, upload_to='movies/'
    )

    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(
        Person,
        through='PersonFilmwork',
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'content"."film_work'
        indexes = [
            models.Index(
                name='film_creation_date_type_rating',
                fields=['creation_date', 'type', 'rating'],
            )
        ]
        verbose_name = _('film')
        verbose_name_plural = _('films')


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        constraints = [
            models.UniqueConstraint(
                fields=['film_work_id', 'genre_id'],
                name='film_genre',
            )
        ]
        indexes = [
            models.Index(
                name='film_genre_idx',
                fields=['film_work_id', 'genre_id'],
            )
        ]
        verbose_name = _('genre_film')
        verbose_name_plural = _('genres_film')


class PersonFilmwork(UUIDMixin):
    ROLE_CHOICES = [('ac', 'actor'), ('sc', 'screenwriter'), ('mg', 'manager')]
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    role = models.CharField(_('role'), max_length=100, choices=ROLE_CHOICES)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            models.UniqueConstraint(
                fields=['film_work_id', 'person_id', 'role'],
                name='film_person_role',
            )
        ]
        indexes = [
            models.Index(
                name='film_person_role_idx',
                fields=['film_work_id', 'person_id', 'role'],
            )
        ]
        verbose_name = _('film_person')
        verbose_name_plural = _('film_persons')
