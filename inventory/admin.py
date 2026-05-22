from django.contrib import admin

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


@admin.register(ProductCategory, ServiceCategory, ExpenseCategory)
class NamedCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'stock_quantity', 'low_stock_threshold', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'sku', 'brand', 'model_number']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'standard_price', 'delivery_cost', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_date', 'title', 'category', 'amount', 'payment_method']
    list_filter = ['expense_date', 'category']
    search_fields = ['title', 'notes']


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['line_total', 'line_cost']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'sale_date', 'customer_name', 'payment_method', 'total_amount', 'gross_profit', 'amount_paid', 'status']
    list_filter = ['sale_date', 'payment_method', 'status']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone']
    inlines = [SaleItemInline]


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'product', 'adjustment_type', 'quantity_change', 'previous_quantity', 'new_quantity']
    list_filter = ['adjustment_type', 'created_at']
    search_fields = ['product__name', 'note']
