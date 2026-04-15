from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .forms import RoomForm

from .models import Room, Booking
from .forms import BookingForm, LoginForm, RegisterForm

# ==========================================
# ОСНОВНЫЕ СТРАНИЦЫ
# ==========================================

def index(request):
    """Главная страница со списком номеров"""
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'core/index.html', {'rooms': rooms})

def book_room(request, room_id):
    """Страница бронирования номера"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            if request.user.is_authenticated:
                booking.user = request.user
            
            try:
                booking.save()
                messages.success(request, f'Заявка на номер "{room.title}" успешно создана!')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {e}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = BookingForm()
    
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

def analytics(request):
    """Страница аналитики (доступна всем, но лучше ограничить админами)"""
    
    # --- БЛОК АНАЛИТИКИ (НОВОЕ) ---
    # Общая выручка
    total_revenue = Booking.objects.filter(status='CONFIRMED').aggregate(
        total=Sum('room__price')
    )['total'] or 0

    # Данные для графика по месяцам
    bookings_by_month = Booking.objects.filter(
        status__in=['NEW', 'CONFIRMED']
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Преобразуем данные для Chart.js
    chart_labels = [item['month'].strftime('%B %Y') for item in bookings_by_month]
    chart_data = [item['count'] for item in bookings_by_month]
    # -----------------------------

    context = {
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='CONFIRMED').count(),
        'pending_bookings': bookings.filter(status='NEW').count(),
        'form': form,
        # Добавляем данные графиков в контекст
        'total_revenue': total_revenue,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    
    return render(request, 'core/admin_dashboard.html', context)
# ==========================================
# АВТОРИЗАЦИЯ
# ==========================================

def user_login(request):
    # Если пользователь уже вошел, перенаправляем его на главную
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Проверяем логин и пароль
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                
                # === ИЗМЕНЕНИЕ ЗДЕСЬ ===
                # Теперь ВСЕХ (и админов тоже) кидаем на главную страницу
                return redirect('index') 
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def user_register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать.')
            return redirect('profile')
    else:
        form = RegisterForm()
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def user_profile(request):
    """Личный кабинет пользователя"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {'bookings': bookings})

def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')

# ==========================================
# АДМИН-ПАНЕЛЬ (КАСТОМНАЯ)
# ==========================================

def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin, login_url='/admin/')
def admin_dashboard(request):
    # 1. Обработка формы добавления номера
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Номер успешно добавлен!')
            return redirect('admin_dashboard')
    else:
        form = RoomForm()

    # 2. Получаем все брони
    bookings = Booking.objects.all().select_related('room', 'user').order_by('-created_at')
    
    # 3. Считаем статистику для карточек
    total_bookings_count = bookings.count()
    confirmed_bookings_count = bookings.filter(status='CONFIRMED').count()
    pending_bookings_count = bookings.filter(status='NEW').count()
    
    # 4. Считаем ВЫРУЧКУ (для новой карточки)
    total_revenue = Booking.objects.filter(status='CONFIRMED').aggregate(
        total=Sum('room__price')
    )['total'] or 0

    # 5. Готовим данные для ГРАФИКА (по месяцам)
    bookings_by_month = Booking.objects.filter(
        status__in=['NEW', 'CONFIRMED']
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    chart_labels = [item['month'].strftime('%B %Y') for item in bookings_by_month]
    chart_data = [item['count'] for item in bookings_by_month]

    context = {
        'bookings': bookings,
        'total_bookings': total_bookings_count,
        'confirmed_bookings': confirmed_bookings_count,
        'pending_bookings': pending_bookings_count,
        'total_revenue': total_revenue,      # Передаем выручку
        'chart_labels': chart_labels,        # Передаем метки графика
        'chart_data': chart_data,            # Передаем данные графика
        'form': form,
    }
    
    return render(request, 'core/admin_dashboard.html', context)

@user_passes_test(is_admin, login_url='/admin/')
def change_booking_status(request, booking_id, status):
    """Изменение статуса брони"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = status
    booking.save()
    messages.success(request, f'Статус брони изменен на {status}')
    return redirect('admin_dashboard')