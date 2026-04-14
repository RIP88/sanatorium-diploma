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
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.user = request.user if request.user.is_authenticated else None
            booking.save()
            messages.success(request, f'Заявка на бронирование номера "{room.title}" успешно создана!')
            return redirect('index')
    else:
        form = BookingForm(room=room)
    
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime

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