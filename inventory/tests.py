from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Expense, Product, Sale, Service, StockAdjustment


class InventoryWorkflowTests(TestCase):
    def test_sale_create_reduces_stock_and_calculates_profit(self):
        product = Product.objects.create(
            name='USB Keyboard',
            sku='KB-001',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            stock_quantity=3,
        )
        service = Service.objects.create(
            name='Windows Setup',
            standard_price=Decimal('50.00'),
            delivery_cost=Decimal('20.00'),
        )

        response = self.client.post(reverse('sale_create'), {
            'sale_date': timezone.localdate().isoformat(),
            'customer_name': 'Walk-in',
            'customer_phone': '',
            'payment_method': Sale.PAYMENT_CASH,
            'discount_amount': '10.00',
            'amount_paid': '',
            'notes': '',
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-item_type': 'product',
            'form-0-product': str(product.pk),
            'form-0-service': '',
            'form-0-description': '',
            'form-0-quantity': '2',
            'form-0-unit_price': '',
            'form-1-item_type': 'service',
            'form-1-product': '',
            'form-1-service': str(service.pk),
            'form-1-description': '',
            'form-1-quantity': '1',
            'form-1-unit_price': '',
        })

        self.assertEqual(response.status_code, 302)
        sale = Sale.objects.get()
        product.refresh_from_db()

        self.assertEqual(product.stock_quantity, 1)
        self.assertEqual(sale.subtotal, Decimal('350.00'))
        self.assertEqual(sale.total_amount, Decimal('340.00'))
        self.assertEqual(sale.total_cost, Decimal('220.00'))
        self.assertEqual(sale.gross_profit, Decimal('120.00'))
        self.assertEqual(sale.amount_paid, Decimal('340.00'))
        self.assertEqual(StockAdjustment.objects.filter(adjustment_type=StockAdjustment.TYPE_SALE).count(), 1)

    def test_report_export_returns_xlsx_file(self):
        Expense.objects.create(
            expense_date=timezone.localdate(),
            title='Internet',
            amount=Decimal('1200.00'),
            payment_method='Cash',
        )

        response = self.client.get(reverse('export_xlsx'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            response['Content-Type'],
        )
        self.assertIn('fynnet-inventory', response['Content-Disposition'])

# Create your tests here.
