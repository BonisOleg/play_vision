from django import forms
from django.forms import inlineformset_factory
from .models import Event


class TicketTierForm(forms.Form):
    """Form for single ticket tier"""
    name = forms.CharField(
        max_length=50,
        label='Назва тарифу',
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Ціна (грн)',
        widget=forms.NumberInput(attrs={'class': 'vTextField'})
    )
    features = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField',
            'rows': 8,
            'placeholder': 'Одна пер година на рядок (1-8 пунктів)'
        }),
        label='Переваги тарифу',
        help_text='Кожен пункт з нового рядка (максимум 8)'
    )
    is_popular = forms.BooleanField(
        required=False,
        label='Найвигідніше',
        help_text='Позначка "Найвигідніше" на картці'
    )


class EventForm(forms.ModelForm):
    """Extended Event form with ticket tiers"""
    
    tier_1_name = forms.CharField(max_length=50, initial='Базовий', label='Тариф 1: Назва')
    tier_1_price = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label='Тариф 1: Ціна')
    tier_1_features = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
        label='Тариф 1: Переваги'
    )
    tier_1_popular = forms.BooleanField(required=False, label='Тариф 1: Найвигідніше')
    
    tier_2_name = forms.CharField(max_length=50, initial='ПРО', label='Тариф 2: Назва')
    tier_2_price = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label='Тариф 2: Ціна')
    tier_2_features = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
        label='Тариф 2: Переваги'
    )
    tier_2_popular = forms.BooleanField(required=False, label='Тариф 2: Найвигідніше')
    
    tier_3_name = forms.CharField(max_length=50, initial='Преміум', label='Тариф 3: Назва')
    tier_3_price = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label='Тариф 3: Ціна')
    tier_3_features = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
        label='Тариф 3: Переваги'
    )
    tier_3_popular = forms.BooleanField(required=False, label='Тариф 3: Найвигідніше')
    
    class Meta:
        model = Event
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk and self.instance.ticket_tiers:
            tiers = self.instance.ticket_tiers
            for i, tier in enumerate(tiers[:3], 1):
                self.fields[f'tier_{i}_name'].initial = tier.get('name', '')
                self.fields[f'tier_{i}_price'].initial = tier.get('price', 0)
                features_list = tier.get('features', [])
                self.fields[f'tier_{i}_features'].initial = '\n'.join(features_list)
                self.fields[f'tier_{i}_popular'].initial = tier.get('is_popular', False)
    
    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free', False)
        
        if not is_free:
            has_valid_tier = False
            for i in range(1, 4):
                name = cleaned_data.get(f'tier_{i}_name', '').strip()
                price = cleaned_data.get(f'tier_{i}_price')
                
                if name and price is not None and price > 0:
                    has_valid_tier = True
                    break
            
            if not has_valid_tier:
                self.add_error(
                    'tier_1_name',
                    'Для платних подій потрібно заповнити хоча б один тариф з ціною > 0'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Тільки якщо NOT is_free - створюємо тарифи
        if not instance.is_free:
            tiers = []
            for i in range(1, 4):
                name = self.cleaned_data.get(f'tier_{i}_name')
                price = self.cleaned_data.get(f'tier_{i}_price')
                features_text = self.cleaned_data.get(f'tier_{i}_features', '')
                is_popular = self.cleaned_data.get(f'tier_{i}_popular', False)
                
                if name and price is not None:
                    features = [f.strip() for f in features_text.split('\n') if f.strip()][:8]
                    tiers.append({
                        'name': name,
                        'price': float(price),
                        'features': features,
                        'is_popular': is_popular
                    })
            
            instance.ticket_tiers = tiers
        else:
            # Якщо безкоштовний - очищаємо тарифи
            instance.ticket_tiers = []
        
        if commit:
            instance.save()
        
        return instance


class FreeEventRegistrationForm(forms.Form):
    """Form for free event registration"""
    attendee_name = forms.CharField(
        max_length=200,
        label='Ім\'я',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваше ім\'я'
        })
    )
    attendee_email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@email.com'
        })
    )
    attendee_phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+380...'
        })
    )

