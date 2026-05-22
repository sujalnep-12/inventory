from decimal import Decimal

from django import forms
from django.forms import formset_factory

from .models import (
    Expense,
    ExpenseCategory,
    Product,
    ProductCategory,
    Sale,
    SaleItem,
    Service,
    ServiceCategory,
    StockAdjustment,
)


BASE_INPUT = (
    'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 '
    'shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200'
)
CHECK_INPUT = 'h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500'


class TailwindFormMixin:
    def _apply_tailwind(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', CHECK_INPUT)
            else:
                widget.attrs.setdefault('class', BASE_INPUT)
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)
            if isinstance(widget, forms.NumberInput):
                widget.attrs.setdefault('step', '0.01')


class ProductCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()


class ServiceCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()


class ExpenseCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()


class ProductForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'sku',
            'name',
            'brand',
            'model_number',
            'description',
            'cost_price',
            'selling_price',
            'stock_quantity',
            'low_stock_threshold',
            'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
        self.fields['category'].queryset = ProductCategory.objects.order_by('name')
        self.fields['sku'].required = False
        self.fields['description'].widget.attrs['rows'] = 4

    def clean_sku(self):
        return self.cleaned_data.get('sku') or None


class ServiceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'category',
            'name',
            'description',
            'standard_price',
            'delivery_cost',
            'duration_minutes',
            'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
        self.fields['category'].queryset = ServiceCategory.objects.order_by('name')
        self.fields['duration_minutes'].widget.attrs['step'] = '1'
        self.fields['description'].widget.attrs['rows'] = 4

    def clean_duration_minutes(self):
        return self.cleaned_data.get('duration_minutes') or 0


class ExpenseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_date', 'category', 'title', 'amount', 'payment_method', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
        self.fields['category'].queryset = ExpenseCategory.objects.order_by('name')


class SaleForm(TailwindFormMixin, forms.ModelForm):
    amount_paid = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.00'),
        help_text='Leave blank to mark the sale as fully paid.',
    )

    class Meta:
        model = Sale
        fields = [
            'sale_date',
            'customer_name',
            'customer_phone',
            'payment_method',
            'discount_amount',
            'amount_paid',
            'notes',
        ]
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
        self.fields['payment_method'].label = 'Payment'
        self.fields['discount_amount'].label = 'Discount'
        self.fields['amount_paid'].label = 'Paid now'


class SaleItemForm(TailwindFormMixin, forms.Form):
    item_type = forms.ChoiceField(choices=[('', 'Select type')] + SaleItem.ITEM_CHOICES, required=False)
    product = forms.ModelChoiceField(queryset=Product.objects.none(), required=False)
    service = forms.ModelChoiceField(queryset=Service.objects.none(), required=False)
    description = forms.CharField(max_length=240, required=False)
    quantity = forms.IntegerField(min_value=1, required=False)
    unit_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=Decimal('0.00'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')
        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('name')
        self._apply_tailwind()
        self.fields['item_type'].label = 'Type'
        self.fields['quantity'].label = 'Qty'
        self.fields['unit_price'].label = 'Sale price'
        self.fields['description'].label = 'Note'
        self.fields['quantity'].widget.attrs['step'] = '1'

    @property
    def has_line_data(self):
        if not self.is_bound or not hasattr(self, 'cleaned_data'):
            return False
        return any([
            self.cleaned_data.get('item_type'),
            self.cleaned_data.get('product'),
            self.cleaned_data.get('service'),
            self.cleaned_data.get('description'),
            self.cleaned_data.get('quantity'),
            self.cleaned_data.get('unit_price'),
        ])

    def clean(self):
        cleaned = super().clean()
        if not any(cleaned.get(name) for name in ['item_type', 'product', 'service', 'description', 'quantity', 'unit_price']):
            return cleaned

        item_type = cleaned.get('item_type')
        product = cleaned.get('product')
        service = cleaned.get('service')
        quantity = cleaned.get('quantity')

        if not item_type:
            raise forms.ValidationError('Choose product or service for this line.')
        if item_type == SaleItem.ITEM_PRODUCT and not product:
            raise forms.ValidationError('Choose a product for this line.')
        if item_type == SaleItem.ITEM_SERVICE and not service:
            raise forms.ValidationError('Choose a service for this line.')
        if not quantity:
            raise forms.ValidationError('Enter a quantity for this line.')

        return cleaned


SaleItemFormSet = formset_factory(SaleItemForm, extra=6)


class StockAdjustmentForm(TailwindFormMixin, forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True).order_by('name'))
    adjustment_type = forms.ChoiceField(
        choices=[
            (StockAdjustment.TYPE_RESTOCK, 'Restock'),
            (StockAdjustment.TYPE_REMOVE, 'Remove stock'),
            (StockAdjustment.TYPE_SET, 'Set stock level'),
        ]
    )
    quantity = forms.IntegerField(min_value=0)
    note = forms.CharField(max_length=240, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
        self.fields['quantity'].widget.attrs['step'] = '1'


class DateRangeForm(TailwindFormMixin, forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind()
