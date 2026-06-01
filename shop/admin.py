from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Category, Country, City, PickupPoint, Order, OrderItem, Review, News


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_link', 'quantity', 'price', 'get_total')
    fields = ('product_link', 'quantity', 'price', 'get_total')

    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product_id])
        return format_html('<a href="{}">{} (#{})</a>', url, obj.product.name, obj.product_id)
    product_link.short_description = 'Товар'

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Сумма'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'phone', 'pickup_point', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'pk')
    readonly_fields = ('pk', 'name', 'phone', 'pickup_point', 'status', 'comment', 'total', 'created_at', 'user')
    inlines = [OrderItemInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'price', 'in_stock', 'is_active')
    list_filter = ('category', 'country', 'in_stock', 'is_active')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Country)
admin.site.register(City)
admin.site.register(PickupPoint)
admin.site.register(Review)
admin.site.register(News)
