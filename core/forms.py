from django import forms
from .models import Booking, Room
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError("Дата выезда должна быть позже даты заезда.")
            
            # Проверка на пересечение с существующими бронями
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                status__in=['NEW', 'CONFIRMED'],  # Только активные брони
            ).filter(
                # Логика пересечения дат: 
                # (начало новой <= конец старой) И (конец новой >= начало старой)
                check_in__lte=check_out,
                check_out__gte=check_in,
            )

            if overlapping_bookings.exists():
                raise ValidationError("Этот номер уже забронирован на выбранные даты.")

        return cleaned_data