from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    CATEGORY_CHOICES = [
        ('STD', 'Стандарт'),
        ('LUX', 'Люкс'),
        ('FAM', 'Семейный'),
    ]

    title = models.CharField('Название номера', max_length=100)
    category = models.CharField('Категория', max_length=3, choices=CATEGORY_CHOICES, default='STD')
    price = models.IntegerField('Цена за сутки')
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Фото номера', upload_to='rooms/')
    is_available = models.BooleanField('Доступен', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

class Booking(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новая заявка'),
        ('CONFIRMED', 'Подтверждено'),
        ('CANCELLED', 'Отменено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Клиент')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Номер')
    check_in = models.DateField('Дата заезда')
    check_out = models.DateField('Дата выезда')
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"Бронь {self.room.title} от {self.user.username}"

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'