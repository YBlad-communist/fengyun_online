from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, PickupPoint, City, UserProfile, Review


class OrderForm(forms.ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        label='Город',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city'})
    )
    pickup_point = forms.ModelChoiceField(
        queryset=PickupPoint.objects.filter(is_active=True),
        label='Точка выдачи',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pickup_point'})
    )

    class Meta:
        model = Order
        fields = ['name', 'phone', 'pickup_point', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (xxx) xxx-xx-xx'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий к заказу'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pickup_point'].queryset = PickupPoint.objects.none()
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['pickup_point'].queryset = PickupPoint.objects.filter(city_id=city_id, is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.pickup_point:
            self.fields['pickup_point'].queryset = PickupPoint.objects.filter(city=self.instance.pickup_point.city, is_active=True)
            self.fields['city'].initial = self.instance.pickup_point.city


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш отзыв'}),
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(5, '5 ★'), (4, '4 ★'), (3, '3 ★'), (2, '2 ★'), (1, '1 ★')]),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
