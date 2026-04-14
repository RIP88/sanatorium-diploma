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

# ==========================================
# НОВЫЕ ФОРМЫ ДЛЯ АВТОРИЗАЦИИ И РЕГИСТРАЦИИ
# ==========================================

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Пароль'
        })
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Подтверждение пароля'
        })