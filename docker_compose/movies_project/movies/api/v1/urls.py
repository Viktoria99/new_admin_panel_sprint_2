from django.urls import path, re_path

from .views import MoviesDetailApi, MoviesListPaginatorApi

urlpatterns = [
    path('movies/', MoviesListPaginatorApi.as_view()),
    path('movies/<uuid:pk>/', MoviesDetailApi.as_view()),
]
