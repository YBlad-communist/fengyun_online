import random
import re
import threading
from datetime import datetime, timedelta
from collections import Counter

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count

from .models import Product, Country, PickupPoint, City, Order, OrderItem, UserProfile, Review, News, Category
from .forms import OrderForm, RegisterForm, ProfileForm, ReviewForm


# ─── Cart helpers ────────────────────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def cart_total(cart):
    return sum(item['price'] * item['qty'] for item in cart.values())


# ─── Catalog ─────────────────────────────────────────────────────────────────

def index(request):
    products = list(Product.objects.filter(is_active=True, in_stock=True).select_related('country'))
    new_products = sorted(products, key=lambda p: p.created_at or datetime.min, reverse=True)[:8]
    popular_products = random.sample(products, min(4, len(products)))
    min_price = min((p.price for p in products), default=0)
    total_count = len(products)
    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)
    countries = Country.objects.filter(product__in=Product.objects.filter(is_active=True)).distinct()
    pickup_count = PickupPoint.objects.filter(is_active=True).count()
    return render(request, 'shop/index.html', {
        'new_products': new_products,
        'popular_products': popular_products,
        'min_price': min_price,
        'total_count': total_count,
        'categories': categories,
        'countries_count': countries.count(),
        'pickup_count': pickup_count,
    })


def catalog(request):
    products = Product.objects.filter(is_active=True, in_stock=True).select_related('country')
    countries = Country.objects.all()
    country_filter = request.GET.get('country')
    search_query = request.GET.get('q', '')
    if country_filter:
        products = products.filter(country__code=country_filter)
    if search_query:
        products = products.filter(name__icontains=search_query)
    products_count = products.count()
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'shop/catalog.html', {
        'page_obj': page_obj,
        'countries': countries,
        'selected_country': country_filter,
        'search_query': search_query,
        'products_count': products_count,
    })


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен!')
    return redirect('product_detail', pk=pk)


STOP_WORDS = {'это', 'в', 'на', 'из', 'по', 'и', 'не', 'от', 'для', 'с', 'у', 'за', 'со', 'ещё', 'так', 'что', 'как', 'но', 'или', 'же', 'то', 'до', 'об', 'под', 'над', 'о', 'к', 'а', 'все', 'при'}

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.select_related('user').all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    else:
        avg_rating = 0

    # Similar products: by description keyword overlap
    similar = []
    if product.description:
        keywords = set(re.findall(r'[а-яёa-z]{3,}', product.description.lower()))
        keywords -= STOP_WORDS
        if keywords:
            word_q = Q()
            for word in keywords:
                word_q |= Q(description__icontains=word)
            candidates = Product.objects.filter(word_q, is_active=True).exclude(pk=product.pk).select_related('country')[:20]
            scored = Counter()
            for c in candidates:
                if c.description:
                    c_words = set(re.findall(r'[а-яёa-z]{3,}', c.description.lower()))
                    scored[c.pk] = len(keywords & c_words)
            similar_pks = [pk for pk, _ in scored.most_common(6)]
            similar = [c for c in candidates if c.pk in similar_pks]

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'similar_products': similar,
    })


# ─── Cart ────────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = get_cart(request)
    pids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = {p.pk: p for p in Product.objects.filter(pk__in=pids).select_related('country')}
    items = []
    for pid in pids:
        p = products.get(pid)
        if p and str(pid) in cart:
            item = cart[str(pid)]
            items.append({'product': p, 'qty': item['qty'], 'subtotal': item['price'] * item['qty']})
    return render(request, 'shop/cart.html', {'items': items, 'total': cart_total(cart)})


@require_POST
def cart_add(request, pk):
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'login'}, status=403)
        messages.info(request, 'Войдите или зарегистрируйтесь, чтобы добавить товар в корзину')
        return redirect(f'{settings.LOGIN_URL}?next={request.POST.get("next", "/")}')
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = get_cart(request)
    pid = str(pk)
    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {'qty': 1, 'price': float(product.price), 'name': product.name}
    save_cart(request, cart)
    total_count = sum(item['qty'] for item in cart.values())
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'count': total_count})
    messages.success(request, f'«{product.name}» добавлен в корзину')
    return redirect(request.POST.get('next', '/'))


@require_POST
def cart_remove(request, pk):
    cart = get_cart(request)
    cart.pop(str(pk), None)
    save_cart(request, cart)
    return redirect('cart')


@require_POST
def cart_update(request, pk):
    cart = get_cart(request)
    pid = str(pk)
    try:
        qty = int(request.POST.get('qty', 1))
    except ValueError:
        qty = 1
    if pid in cart:
        if qty < 1:
            cart.pop(pid)
        else:
            cart[pid]['qty'] = qty
    save_cart(request, cart)
    return redirect('cart')


# ─── Checkout ────────────────────────────────────────────────────────────────

def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = cart_total(cart)
            order.save()

            pids = [int(pid) for pid in cart.keys() if pid.isdigit()]
            products = {p.pk: p for p in Product.objects.filter(pk__in=pids)}
            for pid in pids:
                p = products.get(pid)
                if p and str(pid) in cart:
                    item = cart[str(pid)]
                    OrderItem.objects.create(order=order, product=p, quantity=item['qty'], price=item['price'])

            # Bonus points: 1 point per 100 rubles
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    profile.bonus_points += int(order.total // 100)
                    profile.save()
                except UserProfile.DoesNotExist:
                    pass

            save_cart(request, {})
            request.session['last_order_pk'] = order.pk
            threading.Thread(target=send_telegram_notification, args=(order,)).start()
            messages.success(request, f'Заказ №{order.pk} успешно оформлен!')
            return redirect('order_success', pk=order.pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['name'] = request.user.get_full_name() or request.user.username
            try:
                initial['phone'] = request.user.profile.phone
            except UserProfile.DoesNotExist:
                pass
        form = OrderForm(initial=initial)

    items = []
    pids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = {p.pk: p for p in Product.objects.filter(pk__in=pids).select_related('country')}
    for pid in pids:
        p = products.get(pid)
        if p and str(pid) in cart:
            item = cart[str(pid)]
            items.append({'product': p, 'qty': item['qty'], 'subtotal': item['price'] * item['qty']})

    return render(request, 'shop/checkout.html', {
        'form': form,
        'items': items,
        'total': cart_total(cart),
    })


def order_success(request, pk):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, pk=pk, user=request.user)
    else:
        last_pk = request.session.get('last_order_pk')
        if last_pk != pk:
            raise Http404
        order = get_object_or_404(Order, pk=pk)
    return render(request, 'shop/order_success.html', {'order': order})


# ─── Telegram ────────────────────────────────────────────────────────────────

def send_telegram_notification(order):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
    if not token or not chat_id:
        return
    items_text = '\n'.join([f'  • {i.product.name} × {i.quantity} = {i.price * i.quantity} ₽' for i in order.items.all()])
    text = (
        f'🛒 *Новый заказ №{order.pk}*\n'
        f'👤 {order.name}\n'
        f'📞 {order.phone}\n'
        f'📍 {order.pickup_point}\n'
        f'💰 Итого: {order.total} ₽\n\n'
        f'Товары:\n{items_text}'
    )
    try:
        req_lib.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'},
            timeout=5
        )
    except Exception:
        pass


# ─── News ────────────────────────────────────────────────────────────────────

def news_list(request):
    news = News.objects.filter(is_published=True)
    return render(request, 'shop/news.html', {'news': news})


def news_detail(request, pk):
    article = get_object_or_404(News, pk=pk, is_published=True)
    return render(request, 'shop/news_detail.html', {'article': article})


# ─── Stores map ──────────────────────────────────────────────────────────────

def stores(request):
    cities = City.objects.all()
    return render(request, 'shop/stores.html', {'cities': cities})


def api_pickup_points(request):
    city_id = request.GET.get('city')
    points = PickupPoint.objects.filter(is_active=True)
    if city_id:
        points = points.filter(city_id=city_id)
    data = [{'id': p.pk, 'name': p.name, 'address': p.address, 'city': p.city.name} for p in points]
    return JsonResponse(data, safe=False)


# ─── Account ─────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('account')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect('account')
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('account')

    attempts = request.session.get('login_attempts', 0)
    lockout_until = request.session.get('login_lockout_until')

    if lockout_until and datetime.now() < datetime.fromisoformat(lockout_until):
        remaining = int((datetime.fromisoformat(lockout_until) - datetime.now()).total_seconds() // 60) + 1
        messages.error(request, f'Слишком много попыток. Попробуйте через {remaining} мин.')
        return render(request, 'shop/login.html', {'form': AuthenticationForm()})

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            request.session['login_attempts'] = 0
            request.session.pop('login_lockout_until', None)
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or 'account'
            return redirect(next_url)
        else:
            request.session['login_attempts'] = attempts + 1
            if request.session['login_attempts'] >= LOGIN_MAX_ATTEMPTS:
                request.session['login_lockout_until'] = (datetime.now() + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)).isoformat()
                messages.error(request, f'Слишком много попыток. Подождите {LOGIN_LOCKOUT_MINUTES} мин.')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def account_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('account')
    else:
        form = ProfileForm(instance=profile)

    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'shop/account.html', {
        'profile': profile,
        'form': form,
        'orders': orders,
    })
