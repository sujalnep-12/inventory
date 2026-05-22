from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'service categories'

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'expense categories'

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    sku = models.CharField('SKU', max_length=60, unique=True, null=True, blank=True)
    name = models.CharField(max_length=180)
    brand = models.CharField(max_length=120, blank=True)
    model_number = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        if self.sku:
            return f'{self.name} ({self.sku})'
        return self.name

    @property
    def inventory_value(self):
        return self.cost_price * self.stock_quantity

    @property
    def expected_stock_revenue(self):
        return self.selling_price * self.stock_quantity

    @property
    def unit_margin(self):
        return self.selling_price - self.cost_price

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def get_absolute_url(self):
        return reverse('product_list')


class Service(TimeStampedModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
    )
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    standard_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    delivery_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Internal labor, material, or partner cost for this service.',
    )
    duration_minutes = models.PositiveIntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def service_margin(self):
        return self.standard_price - self.delivery_cost

    def get_absolute_url(self):
        return reverse('service_list')


class Expense(TimeStampedModel):
    expense_date = models.DateField(default=timezone.localdate)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
    )
    title = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f'{self.title} - {self.amount}'


class Sale(TimeStampedModel):
    PAYMENT_CASH = 'cash'
    PAYMENT_QR = 'qr'
    PAYMENT_CARD = 'card'
    PAYMENT_BANK = 'bank'
    PAYMENT_CREDIT = 'credit'
    PAYMENT_OTHER = 'other'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_QR, 'QR code'),
        (PAYMENT_CARD, 'Card'),
        (PAYMENT_BANK, 'Bank transfer'),
        (PAYMENT_CREDIT, 'Credit'),
        (PAYMENT_OTHER, 'Other'),
    ]

    STATUS_PAID = 'paid'
    STATUS_PARTIAL = 'partial'
    STATUS_CREDIT = 'credit'
    STATUS_CHOICES = [
        (STATUS_PAID, 'Paid'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_CREDIT, 'Credit'),
    ]

    invoice_number = models.CharField(max_length=40, unique=True, blank=True)
    sale_date = models.DateField(default=timezone.localdate)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_phone = models.CharField(max_length=60, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PAID)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return self.invoice_number or f'Sale #{self.pk}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            prefix = timezone.localdate().strftime('FYN-%Y%m%d')
            existing = Sale.objects.filter(invoice_number__startswith=prefix).count() + 1
            self.invoice_number = f'{prefix}-{existing:04d}'
        self._sync_status()
        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        balance = self.total_amount - self.amount_paid
        return balance if balance > Decimal('0.00') else Decimal('0.00')

    def _sync_status(self):
        if self.amount_paid <= Decimal('0.00'):
            self.status = self.STATUS_CREDIT
        elif self.amount_paid < self.total_amount:
            self.status = self.STATUS_PARTIAL
        else:
            self.status = self.STATUS_PAID

    def recalculate_totals(self, save=True):
        subtotal = Decimal('0.00')
        total_cost = Decimal('0.00')

        for item in self.items.all():
            subtotal += item.line_total
            total_cost += item.line_cost

        total = subtotal - self.discount_amount
        if total < Decimal('0.00'):
            total = Decimal('0.00')

        self.subtotal = subtotal
        self.total_amount = total
        self.total_cost = total_cost
        self.gross_profit = total - total_cost
        self._sync_status()

        if save:
            self.save(update_fields=[
                'subtotal',
                'discount_amount',
                'total_amount',
                'total_cost',
                'gross_profit',
                'amount_paid',
                'status',
                'updated_at',
            ])


class SaleItem(models.Model):
    ITEM_PRODUCT = 'product'
    ITEM_SERVICE = 'service'
    ITEM_CHOICES = [
        (ITEM_PRODUCT, 'Product'),
        (ITEM_SERVICE, 'Service'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=240)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.description

    def clean(self):
        if self.item_type == self.ITEM_PRODUCT and not self.product:
            raise ValidationError('Product line items must include a product.')
        if self.item_type == self.ITEM_SERVICE and not self.service:
            raise ValidationError('Service line items must include a service.')

    def save(self, *args, **kwargs):
        if self.item_type == self.ITEM_PRODUCT and self.product:
            if not self.description:
                self.description = self.product.name
            if self.unit_price is None:
                self.unit_price = self.product.selling_price
            self.unit_cost = self.product.cost_price
        elif self.item_type == self.ITEM_SERVICE and self.service:
            if not self.description:
                self.description = self.service.name
            if self.unit_price is None:
                self.unit_price = self.service.standard_price
            self.unit_cost = self.service.delivery_cost

        self.line_total = self.unit_price * self.quantity
        self.line_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class StockAdjustment(TimeStampedModel):
    TYPE_RESTOCK = 'restock'
    TYPE_REMOVE = 'remove'
    TYPE_SET = 'set'
    TYPE_SALE = 'sale'
    TYPE_CHOICES = [
        (TYPE_RESTOCK, 'Restock'),
        (TYPE_REMOVE, 'Remove stock'),
        (TYPE_SET, 'Set stock level'),
        (TYPE_SALE, 'Sale'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity_change = models.IntegerField()
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product} {self.quantity_change:+d}'
