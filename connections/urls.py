from django.urls import path

from . import views

urlpatterns = [
    path('search', views.SearchUsersView.as_view(), name='search-user'),
    path('create', views.CreateConnectionRequestView.as_view(), name='create-connection-request'),
    path('', views.ConnectionRequestView.as_view(), name='list-connection-request'),
    path('<int:connection_id>', views.ConnectionRequestView.as_view(), name='connection-request')
]
