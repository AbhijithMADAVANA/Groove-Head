from django import forms
from app1.models import *
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import Banner

class CreateProductForm(forms.ModelForm):
    new_image = forms.ImageField(required=False) 
    
    class Meta:
        model = Product
        fields = ['title', 'category', 'description','price','old_price', 'new_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price
    
class ProductVariantForm(forms.ModelForm):
      # Add this line for the new image field
    class Meta:
        model = ProductVariant
        fields = ['product', 'color' ,'price','old_price', 'stock_count','image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price

class PriceFilterForm(forms.Form):
    min_price = forms.DecimalField(decimal_places=2)
    max_price = forms.DecimalField(decimal_places=2)

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []

from django import forms
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount', 'expiration_date', 'is_active','minimum_purchase_value','maximum_purchase_value','Usage_count']


        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }






class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'description1', 'description2', 'description3', 'start_date', 'end_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description1': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description2': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description3': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control'}),
        }
