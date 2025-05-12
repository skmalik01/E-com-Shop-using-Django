from django.contrib import admin
from .models import OrderUpdate, Orders, Product, Contact
from import_export.admin import ImportExportModelAdmin

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('product_name', 'category', 'subcategory', 'price', 'pub_date')

@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    list_display = ('name', 'email', 'subject')

@admin.register(Orders)
class OrdersAdmin(ImportExportModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'state', 'zip_code')

@admin.register(OrderUpdate)
class OrderUpdateAdmin(ImportExportModelAdmin):
    list_display = ('order_id', 'update_desc', 'timestamp')
