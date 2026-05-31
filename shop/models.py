from django.db import models
from django.contrib.auth.models import User


class Country(models.Model):
    name = models.CharField('Страна', max_length=100)
    code = models.CharField('Код', max_length=10, unique=True)
    flag_emoji = models.CharField('Флаг', max_length=10, default='🌏')

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name='Страна')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    in_stock = models.BooleanField('В наличии', default=True, db_index=True)
    is_active = models.BooleanField('Активен', default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField('Город', max_length=100)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    name = models.CharField('Название', max_length=100)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name='Город', related_name='pickup_points', null=True)
    address = models.CharField('Адрес', max_length=255)
    is_active = models.BooleanField('Активна', default=True, db_index=True)

    class Meta:
        verbose_name = 'Точка выдачи'
        verbose_name_plural = 'Точки выдачи'

    def __str__(self):
        return f'{self.name} ({self.city.name})'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов к выдаче'),
        ('done', 'Выдан'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL, null=True, verbose_name='Точка выдачи')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    comment = models.TextField('Комментарий', blank=True)
    total = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def get_total(self):
        return self.price * self.quantity


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField('Отзыв')
    rating = models.PositiveSmallIntegerField('Оценка', default=5, choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.product.name}'


class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    image = models.ImageField('Фото', upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField('Опубликована', default=True, db_index=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    bonus_points = models.IntegerField('Бонусные баллы', default=0)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'
