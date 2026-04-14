from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('analytics/', views.analytics, name='analytics'),  # <-- Добавлено
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('analytics/', views.analytics, name='analytics'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('booking/<int:booking_id>/<str:status>/', views.change_booking_status, name='change_status'),
    
    # Новые пути для авторизации
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)