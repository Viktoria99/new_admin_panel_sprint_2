import sys
from functools import wraps

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from rest_framework import status

from ..params import DEFAULT_PAGE_NUMBER, PAGE_COUNT

sys.path.insert(0, '/docker_compose/movies_project/movies')

from django.http import HttpResponse

from movies.models import Filmwork


def is_int(s):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def exception(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    return wrapper


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    @exception
    def get_queryset(self):
        queryset = self.model.objects.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        )
        queryset = queryset.annotate(
            genres=ArrayAgg('persons__full_name', distinct=True),
            actors=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(personfilmwork__role='actor'),
            ),
            directors=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(personfilmwork__role='director'),
            ),
            writers=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(personfilmwork__role='writer'),
            ),
        )
        return queryset

    @exception
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListPaginatorApi(MoviesApiMixin, BaseListView):
    paginate_by = PAGE_COUNT
    previous_page = None
    next_page = None

    @exception
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        page_request = self.request.GET.get('page', DEFAULT_PAGE_NUMBER)

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )

        if is_int(page_request):
            if int(page_request) < paginator.num_pages:
                self.next_page = page.next_page_number()
            if int(page_request) > DEFAULT_PAGE_NUMBER:
                self.previous_page = page.previous_page_number()
        else:
            self.previous_page = page.previous_page_number()

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': self.previous_page,
            'next': self.next_page,
            'results': list(queryset.values()),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return self.object
