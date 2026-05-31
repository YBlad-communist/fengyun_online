from django.core.management.base import BaseCommand
from shop.models import City, PickupPoint, Category, Product, Country, Review, Order, OrderItem, CartItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds or flushes demo data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete all data')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Deleting all data...')
            Review.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            CartItem.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            PickupPoint.objects.all().delete()
            City.objects.all().delete()
            Country.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All data deleted'))
            return

        # Countries
        cn, _ = Country.objects.get_or_create(name='Китай', defaults={'code': 'CN', 'flag_emoji': '🇨🇳'})
        jp, _ = Country.objects.get_or_create(name='Япония', defaults={'code': 'JP', 'flag_emoji': '🇯🇵'})
        kr, _ = Country.objects.get_or_create(name='Корея', defaults={'code': 'KR', 'flag_emoji': '🇰🇷'})
        th, _ = Country.objects.get_or_create(name='Таиланд', defaults={'code': 'TH', 'flag_emoji': '🇹🇭'})
        self.stdout.write('Countries created')

        # Cities
        nakhodka, _ = City.objects.get_or_create(name='Находка')
        fokino, _ = City.objects.get_or_create(name='Фокино')
        khabarovsk, _ = City.objects.get_or_create(name='Хабаровск')
        self.stdout.write('Cities created')

        # Pickup points
        PickupPoint.objects.get_or_create(
            name='ТЦ «Мега»', city=nakhodka,
            defaults={'address': 'Находка, ул. Пограничная, 80, ТЦ «Мега», 1 этаж'}
        )
        PickupPoint.objects.get_or_create(
            name='ТЦ «Клён»', city=nakhodka,
            defaults={'address': 'Находка, Находкинский пр-т, 54, ТЦ «Клён», цокольный этаж'}
        )
        PickupPoint.objects.get_or_create(
            name='ТЦ «Южный»', city=fokino,
            defaults={'address': 'Фокино, ул. Центральная, 15, ТЦ «Южный», 2 этаж'}
        )
        PickupPoint.objects.get_or_create(
            name='ТЦ «Большая Медведица»', city=khabarovsk,
            defaults={'address': 'Хабаровск, ул. Муравьёва-Амурского, 44, ТЦ «БМ», -1 этаж'}
        )
        self.stdout.write('Pickup points created')

        # Categories
        snacks, _ = Category.objects.get_or_create(name='Снеки', defaults={'slug': 'sneki'})
        drinks, _ = Category.objects.get_or_create(name='Напитки', defaults={'slug': 'napitki'})
        chips, _ = Category.objects.get_or_create(name='Чипсы', defaults={'slug': 'chipsy'})
        nuts, _ = Category.objects.get_or_create(name='Орешки', defaults={'slug': 'oreshki'})
        noodles, _ = Category.objects.get_or_create(name='Лапша', defaults={'slug': 'lapsha'})
        sweets, _ = Category.objects.get_or_create(name='Сладости', defaults={'slug': 'sladosti'})
        self.stdout.write('Categories created')

        # Products
        products_data = [
            ('Лапша Nongshim Shin Ramyun', noodles, kr, 129),
            ('Лапша Samyang Carbo Fire', noodles, kr, 149),
            ('Лапша Doenjang Jjigae Ramen', noodles, kr, 139),
            ('Чипсы Lay\'s Original', chips, cn, 99),
            ('Чипсы Pringles Sour Cream', chips, cn, 159),
            ('Чипсы Doritos Nacho Cheese', chips, cn, 139),
            ('Арахис жареный солёный', nuts, cn, 69),
            ('Фисташки с солью', nuts, cn, 199),
            ('Кешью жареный', nuts, cn, 249),
            ('Миндаль в шоколаде', nuts, cn, 179),
            ('Coca-Cola 0.5л', drinks, cn, 59),
            ('Sprite 0.5л', drinks, cn, 59),
            ('Fanta Апельсин 0.5л', drinks, cn, 59),
            ('Зелёный чай Ito-en', drinks, jp, 89),
            ('Сок Mitsui Apple', drinks, jp, 119),
            ('Карамельkin', sweets, cn, 79),
            ('Жевательный мармелад', sweets, cn, 89),
            ('Печенье с начинкой', sweets, jp, 119),
            ('Моти со вкусом манго', sweets, th, 139),
            ('Китайские леденцы на палочке', sweets, cn, 49),
            ('Снеки с креветками', snacks, cn, 69),
            ('Рисовые шарики васаби', snacks, jp, 89),
            ('Водоросли нори жареные', snacks, kr, 79),
            ('Сушёный кальмар', snacks, kr, 149),
            ('Кимчи чипсы', snacks, kr, 99),
            ('Кукурузные палочки', snacks, cn, 59),
            ('Чай матча порошок', drinks, jp, 299),
            ('Соус соевый Kikkoman', drinks, jp, 159),
        ]

        for name, cat, country, price in products_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'country': country,
                    'price': Decimal(str(price)),
                    'description': f'{name} — качественный продукт из {country.name}. Отличный вкус, свежий продукт.',
                    'in_stock': True,
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'{len(products_data)} products created'))
