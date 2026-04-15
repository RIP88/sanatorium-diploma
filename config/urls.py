from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),
    
    # Основные страницы сайта
    path('', views.index, name='index'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('analytics/', views.analytics, name='analytics'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Управление бронированиями (для админки/профилей)
    path('booking/<int:booking_id>/<str:status>/', views.change_booking_status, name='change_status'),

    # Авторизация и профиль пользователя
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),

    # Удаление номера (новое)
    path('room/<int:room_id>/delete/', views.delete_room, name='delete_room'),
]

# Настройка раздачи медиа-файлов только в режиме отладки (DEBUG=True)
# В продакшене (на Timeweb) это обрабатывается веб-сервером, а не Django
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Для статики админки и других файлов в режиме DEBUG тоже полезно добавить:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)