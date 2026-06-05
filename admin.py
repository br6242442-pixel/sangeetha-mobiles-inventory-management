from django.contrib import admin
from .models import Product, Supplier, Customer, Sale
from .models import Purchase, Staff, Attendance

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(Purchase)
admin.site.register(Staff)
admin.site.register(Attendance)