from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/', views.post_status, name='post_status'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<str:username>/', views.send_message, name='send_message'),
]
