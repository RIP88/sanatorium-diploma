from django.shortcuts import render
from .models import Room

def index(request):
    rooms = Room.objects.filter(is_available=True)  # Показываем только доступные номера
    return render(request, 'core/index.html', {'rooms': rooms})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking
from .forms import BookingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        # Передаем данные POST и файлы (если есть)
        form = BookingForm(request.POST, request.FILES)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            # Если пользователь не авторизован, поле user должно быть nullable в модели
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
        # При GET запросе создаем пустую форму
        form = BookingForm()
    
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

def analytics(request):
    # 1. Общая выручка (сумма цен подтвержденных броней)
    # Примечание: для простоты считаем полную стоимость брони
    total_revenue = Booking.objects.filter(status='CONFIRMED').aggregate(
        total=Sum('room__price')
    )['total'] or 0

    # 2. Количество бронирований по месяцам (для графика)
    bookings_by_month = Booking.objects.filter(
        status__in=['NEW', 'CONFIRMED']
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Подготовка данных для графика
    labels = [item['month'].strftime('%B %Y') for item in bookings_by_month]
    data = [item['count'] for item in bookings_by_month]

    # 3. Последние брони для таблицы
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]

    context = {
        'total_revenue': total_revenue,
        'labels': labels,
        'data': data,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'core/analytics.html', context)

# ==========================================
# НОВЫЕ ФУНКЦИИ ДЛЯ АВТОРИЗАЦИИ
# ==========================================

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from django.contrib import messages

# Страница входа
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                
                # Если админ - redirect на dashboard, иначе - на профиль
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('profile')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

# Страница регистрации
def user_register(request):
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

# Личный кабинет пользователя
@login_required
def user_profile(request):
    # Получаем только брони текущего пользователя
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {'bookings': bookings})

# Выход из системы
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')

# ==========================================
# ФУНКЦИИ ДЛЯ АДМИН-ПАНЕЛИ (если ещё нет)
# ==========================================

from django.contrib.auth.decorators import user_passes_test

# Проверка: является ли пользователь админом
def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin, login_url='/admin/')
def admin_dashboard(request):
    # Получаем все брони, сортируем по новизне
    bookings = Booking.objects.all().select_related('room', 'user').order_by('-created_at')
    
    # Считаем статистику
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='CONFIRMED').count()
    pending_bookings = bookings.filter(status='NEW').count()
    
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
    }
    return render(request, 'core/admin_dashboard.html', context)

# Функция для изменения статуса брони (Подтвердить/Отменить)
@user_passes_test(is_admin, login_url='/admin/')
def change_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = status
    booking.save()
    return redirect('admin_dashboard')