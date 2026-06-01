from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Category, Country, City, PickupPoint, Order, OrderItem, Review, News


admin.site.site_header = 'Фэнъюнь — управление'
admin.site.site_title = 'Фэнъюнь'
admin.site.index_title = 'Панель управления магазином'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    classes = ('collapse',)
    fields = ('product_link', 'quantity', 'price', 'get_total')
    readonly_fields = fields

    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product_id])
        return format_html('<a href="{}">{} <span style="color:#888;">#{}</span></a>', url, obj.product.name, obj.product_id)
    product_link.short_description = 'Товар'

    def get_total(self, obj):
        return f'{obj.get_total():.0f} ₽'
    get_total.short_description = 'Сумма'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def colored_status(obj):
    colors = {
        'new': '#F9C900',
        'processing': '#ff9800',
        'ready': '#4caf50',
        'done': '#2196f3',
        'cancelled': '#999',
    }
    c = colors.get(obj.status, '#666')
    return format_html('<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-weight:700;font-size:0.75rem;background:{}22;color:{};border:1px solid {};">{}</span>', c, c, c, obj.get_status_display())
colored_status.short_description = 'Статус'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'phone_link', 'pickup_point', colored_status, 'total_display', 'created_at')
    list_display_links = ('pk', 'name')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'pk')
    date_hierarchy = 'created_at'
    readonly_fields = ('pk', 'name', 'phone', 'pickup_point', 'user', 'comment', 'total', 'created_at', 'status')
    inlines = [OrderItemInline]
    exclude = ('user',)

    def phone_link(self, obj):
        return format_html('<a href="tel:{}" style="text-decoration:none;">📞 {}</a>', obj.phone, obj.phone)
    phone_link.short_description = 'Телефон'

    def total_display(self, obj):
        return f'{obj.total:.0f} ₽'
    total_display.short_description = 'Сумма'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_flag', 'category', 'price_display', 'stock_badge', 'is_active', 'created_at')
    list_display_links = ('name',)
    list_filter = ('category', 'country', 'in_stock', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('name', 'description', 'price')}),
        ('Категория и страна', {'fields': ('category', 'country'), 'classes': ('wide',)}),
        ('Статус', {'fields': ('in_stock', 'is_active')}),
        ('Фото', {'fields': ('image',), 'classes': ('wide',)}),
    )

    def country_flag(self, obj):
        return obj.country.flag_emoji if obj.country else '🌏'
    country_flag.short_description = ''

    def price_display(self, obj):
        return f'{obj.price:.0f} ₽'
    price_display.short_description = 'Цена'

    def stock_badge(self, obj):
        if obj.in_stock:
            return format_html('<span style="color:#4caf50;font-weight:700;">✔ В наличии</span>')
        return format_html('<span style="color:#999;">✖ Под заказ</span>')
    stock_badge.short_description = 'Наличие'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    fields = ('title', 'content', 'image', 'is_published')


admin.site.register(Country)
admin.site.register(City)
admin.site.register(PickupPoint)
admin.site.register(Review)
