from django.urls import path, include
from . import views

app_name = 'learn'
urlpatterns = [
    path('', views.learn_view, name='learn'),
    path('oz/', views.oz_view, name='learn'),
    path('logout', views.logout, name='learn'),
    path('thumbs-up', views.thumbs_up, name='learn'),
    path('thumbs-down', views.thumbs_down, name='learn'),
    path('written-feedback', views.written_feedback, name='learn'),
    # path('', include('application.urls', namespace='application')),
]