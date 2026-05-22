from django.urls import path

from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('services/', views.service_list, name='service_list'),
    path('services/new/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/new/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('stock-adjustments/', views.stock_adjustment_create, name='stock_adjustment_create'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_xlsx, name='export_xlsx'),
    path('categories/', views.category_manager, name='category_manager'),
    path('categories/product/<int:pk>/delete/', views.product_category_delete, name='product_category_delete'),
    path('categories/service/<int:pk>/delete/', views.service_category_delete, name='service_category_delete'),
    path('categories/expense/<int:pk>/delete/', views.expense_category_delete, name='expense_category_delete'),
]
