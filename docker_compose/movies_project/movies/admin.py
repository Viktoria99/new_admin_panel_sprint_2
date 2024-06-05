from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created', 'modified')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ['person']


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = [GenreFilmworkInline, PersonFilmworkInline]
    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
        'created',
        'modified',
    )
    list_filter = ('type',)
    search_fields = ['title', 'id']

    def get_queryset(self, request):
        queryset = super(FilmworkAdmin, self).get_queryset(request)
        queryset.prefetch_related('persons')
        return queryset


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created', 'modified')
    search_fields = ['full_name', 'id']
