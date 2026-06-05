from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    # 🔐 AUTH (ONLY ONE PAGE)
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),

    # 📊 DASHBOARDS
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),

# Product List
path('products/', views.product_list, name='product_list'),

# Add Product
path('add_product/', views.add_product, name='add_product'),

path('edit_product/<int:id>/', views.edit_product, name='edit_product'),
path('delete_product/<int:id>/', views.delete_product, name='delete_product'),

path('billing/', views.create_sale, name='billing'),
path('invoice/<int:sale_id>/', views.invoice, name='invoice'),

path('sales_report/', views.sales_report, name='sales_report'),

path('register/', views.register, name='register'),

path('logout/', views.logout_page, name='logout'),

path('download_invoice/<int:sale_id>/', views.download_invoice, name='download_invoice'),

path('delete_sale/<int:sale_id>/', views.delete_sale, name='delete_sale'),

path('edit_sale/<int:id>/', views.edit_sale, name='edit_sale'),

path('low_stock/', views.low_stock_products, name='low_stock'),

path('suppliers/', views.supplier_list, name='supplier_list'),
path('add_supplier/', views.add_supplier, name='add_supplier'),

path('edit_supplier/<int:id>/', views.edit_supplier, name='edit_supplier'),
path('delete_supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),

path('invoice_pdf/<int:sale_id>/', views.invoice_pdf, name='invoice_pdf'),



path('staff_list/', views.staff_list, name='staff_list'),
path('staff/add', views.add_staff, name='add_staff'),
path('delete_staff/<int:id>/', views.delete_staff, name='delete_staff'),
path('edit_staff/<int:id>/', views.edit_staff, name='edit_staff'),

path('attendance/', views.attendance_dates, name='attendance'),
path('attendance/<str:date>/', views.attendance_by_date, name='attendance_by_date'),
path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
path('attendance-pdf/<str:date>/', views.attendance_pdf, name='attendance_pdf'),


path('contact/', views.contact, name='contact'),
path('helpdesk/', views.helpdesk, name='helpdesk'),

path('product/<int:id>/', views.product_details, name='product_details'),

    

path('invoices/', views.invoice_list, name='invoice_list'),

path('invoice/<int:id>/pdf/', views.invoice_pdf, name='invoice_pdf'),

path('sales/', views.sales_list, name='sales_list'),

path('purchase/', views.purchase_list, name='purchase_list'),
path('purchase/add/', views.add_purchase, name='add_purchase'),
path('purchase/edit/<int:id>/', views.edit_purchase, name='edit_purchase'),
path('purchase/delete/<int:id>/', views.delete_purchase, name='delete_purchase'),

path('set-captcha/', views.set_captcha, name='set_captcha'),
path('reports/', views.reports, name='reports'),

]