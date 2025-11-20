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
    
    # Віртуальне поле для вибору формату події
    event_format = forms.ChoiceField(
        label='Формат події',
        choices=[
            ('online', '🌐 Онлайн подія'),
            ('offline', '📍 Офлайн подія'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'event-format-toggle'}),
        required=True,
        help_text='Оберіть формат проведення події'
    )
    
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
        help_texts = {
            'location': 'Фізична адреса проведення події (для офлайн подій)',
            'online_link': 'Посилання на Zoom, Google Meet, тощо (для онлайн подій)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Визначити початкове значення event_format на основі існуючих даних
        if self.instance and self.instance.pk:
            if self.instance.is_online:
                self.fields['event_format'].initial = 'online'
            else:
                self.fields['event_format'].initial = 'offline'
        else:
            # За замовчуванням для нових подій
            self.fields['event_format'].initial = 'offline'
        
        # Зробити location та online_link необов'язковими (валідація в clean)
        self.fields['location'].required = False
        self.fields['online_link'].required = False
        
        # Завантажити дані тарифів
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
        event_format = cleaned_data.get('event_format')
        location = cleaned_data.get('location')
        online_link = cleaned_data.get('online_link')
        
        if event_format == 'online':
            # Онлайн подія - потрібен online_link
            if not online_link:
                self.add_error('online_link', 'Для онлайн події обов\'язкове посилання на трансляцію')
            # Встановити location = "Онлайн"
            cleaned_data['location'] = 'Онлайн'
        
        elif event_format == 'offline':
            # Офлайн подія - потрібен location
            if not location:
                self.add_error('location', 'Для офлайн події обов\'язкова фізична адреса')
            # Очистити online_link
            cleaned_data['online_link'] = ''
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
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
        
        if commit:
            instance.save()
        
        return instance

