from django.contrib import admin
from .models import Country, Category, Product, PickupPoint, Order, OrderItem, UserProfile, Review


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'flag_emoji']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'country', 'category', 'in_stock', 'is_active', 'created_at']
    list_filter = ['country', 'in_stock', 'is_active', 'category']
    list_editable = ['price', 'in_stock', 'is_active']
    search_fields = ['name', 'description']


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'is_active']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'phone', 'pickup_point', 'status', 'total', 'created_at']
    list_filter = ['status', 'pickup_point']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'total']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'bonus_points']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__username']
