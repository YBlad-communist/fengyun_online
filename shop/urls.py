from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('preorder/', views.preorder, name='preorder'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/success/', views.order_success, name='order_success'),

    path('stores/', views.stores, name='stores'),

    path('account/', views.account_view, name='account'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/register/', views.register_view, name='register'),
]
