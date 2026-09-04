from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
