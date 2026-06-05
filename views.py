from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash  # ADD THIS AT TOP
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Attendance
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Product
from django.db.models import Q
from django.utils.timezone import now
from .models import Sale, Product
from django.shortcuts import get_object_or_404
from datetime import date as today_date
from django.db.models import Count
from django.db.models import Sum

from .models import Sale
from .models import Product, Customer, Sale
from decimal import Decimal
import json
from .models import Product, Supplier, Purchase, Staff, Attendance, Sale, Profile
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.core.mail import send_mail
import random
from django.contrib.auth import authenticate, login
import smtplib
import ssl
from .models import Product, Supplier, Purchase
import re

# ================== HOME ==================
def home(request):
    return render(request, 'home.html')


# ================== AUTH ==================

def login_page(request):

    if request.method == "POST":

        print("POST DATA:", request.POST)

        action = request.POST.get("action")
        print("ACTION:", action)

        # ================= LOGIN =================
        if action == "login":

            request.session['step'] = ""

            username_input = request.POST.get("username")
            password = request.POST.get("password")

            # 🔥 CAPTCHA CHECK
            user_captcha = request.POST.get("captcha_input")
            real_captcha = request.session.get("captcha")

            if not user_captcha or user_captcha != real_captcha:
                messages.error(request, "Invalid captcha")
                request.session['step'] = ""
                return redirect('login')

            # 🔥 EMAIL OR USERNAME LOGIN
            try:
                user_obj = User.objects.get(email=username_input)
                username = user_obj.username

            except User.DoesNotExist:
                username = username_input

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                # ✅ CLEAR SESSION FLOW
                request.session['step'] = ""

                if user.is_superuser:
                    return redirect('admin_dashboard')

                else:
                    return redirect('staff_dashboard')

            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')

        # ================= REGISTER =================
        elif action == "register":

            request.session['step'] = "register"

            full_name = request.POST.get("full_name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            role = request.POST.get("role")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            # 🔴 PHONE VALIDATION
            phone = request.POST.get("phone", "").strip()

            if not phone:
                request.session['step'] = "register"
                messages.error(request, "Phone number is required")
                return redirect('login')

            if not phone.isdigit() or len(phone) != 10:
                request.session['step'] = "register"
                messages.error(request, "Enter valid 10-digit phone number")
                return redirect('login')

            # 🔴 PASSWORD MATCH
            if password != confirm_password:
                request.session['step'] = "register"
                messages.error(request, "Passwords do not match")
                return redirect('login')

            # 🔴 STRONG PASSWORD VALIDATION
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[A-Z]", password):
                messages.error(request, "Password must include uppercase letter")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[a-z]", password):
                messages.error(request, "Password must include lowercase letter")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[0-9]", password):
                messages.error(request, "Password must include a number")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[!@#$%^&*]", password):
                messages.error(request, "Password must include special character")
                request.session['step'] = "register"
                return redirect('login')

            # 🔴 EMAIL CHECK
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
                request.session['step'] = "register"
                return redirect('login')

            # 🔴 USERNAME AUTO FROM EMAIL
            username = email.split("@")[0]

            # 🔴 HANDLE DUPLICATE USERNAME
            if User.objects.filter(username=username).exists():
                username = username + str(User.objects.count())

            # ✅ CREATE USER
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # ✅ ROLE
            if role == "admin":
                user.is_superuser = True
                user.is_staff = True

            else:
                user.is_staff = True

            user.save()

            messages.success(request, "Account created successfully")
            request.session['step'] = ""

            return redirect('login')

        # ================= FORGOT PASSWORD =================
        elif action == "forgot":

            email = request.POST.get("email")

            # CHECK EMAIL EXISTS
            if User.objects.filter(email=email).exists():

                # GENERATE OTP
                otp = str(random.randint(100000, 999999))

                # SAVE SESSION
                request.session['otp'] = otp
                request.session['temp_email'] = email
                request.session['step'] = "otp"

                # SEND EMAIL
                send_mail(
                    "Your OTP - Sangeetha Mobiles",
                    f"Your OTP is: {otp}",
                    "br6242442@gmail.com",
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "OTP sent successfully")
                return redirect('login')

            else:

                messages.error(request, "Email not registered")
                request.session['step'] = "forgot"

                return redirect('login')

        # ================= VERIFY OTP =================
        elif action == "verify_otp":

            entered_otp = request.POST.get("otp")
            real_otp = request.session.get("otp")

            if entered_otp == real_otp:

                messages.success(request, "OTP verified successfully")
                request.session['step'] = "reset"

                return redirect('login')

            else:

                messages.error(request, "Invalid OTP")
                request.session['step'] = "otp"

                return redirect('login')

        # ================= RESET PASSWORD =================
        elif action == "reset_password":

            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password != confirm_password:

                messages.error(request, "Passwords do not match")
                request.session['step'] = "reset"

                return redirect('login')

            email = request.session.get("temp_email")

            try:

                user = User.objects.get(email=email)

                user.set_password(new_password)
                user.save()

                messages.success(request, "Password updated successfully")

                request.session['step'] = "login"

                return redirect('login')

            except:

                messages.error(request, "User not found")
                request.session['step'] = "forgot"

                return redirect('login')

# ================== DASHBOARD ==================
def admin_dashboard(request):
    return render(request, 'dashboard.html',{ 'title': 'Admin Dashboard'})


def staff_dashboard(request):
    return render(request, 'dashboard.html',{ 'title': 'Staff Dashboard'})


# ================== PRODUCT ==================
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def add_product(request):

    if not request.user.is_superuser:
        return redirect('staff_dashboard')
    
    if request.method == "POST":
        mobile_name = request.POST.get('mobile_name')
        brand_model = request.POST.get('brand_model')
        imei = request.POST.get('imei')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')

        # 🔥 VALIDATE STOCK ONLY
        if not stock:
            return render(request, 'add_product.html', {'error': 'Stock is required'})

        stock = int(stock)

        # 🔥 CHECK PRODUCT BY NAME
        product = Product.objects.filter(mobile_name=mobile_name).first()

        if product:
            # ✅ UPDATE ONLY STOCK
            product.stock_quantity += stock
            product.save()
        else:
            # 🔥 PRICE REQUIRED ONLY FOR NEW PRODUCT
            if not price:
                return render(request, 'add_product.html', {'error': 'Price required for new product'})

            price = Decimal(price)

            Product.objects.create(
                mobile_name=mobile_name,
                brand_model_name=brand_model,
                imei_number=imei,
                price=price,
                stock_quantity=stock,
                product_description=description
            )

        
        messages.success(request,"Product added successfully!", extra_tags="added")
        return redirect('product_list')

    return render(request, 'add_product.html')


def edit_product(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    product = get_object_or_404(Product, product_id=id)

    if request.method == "POST":
        product.mobile_name = request.POST.get('mobile_name')
        product.brand_model_name = request.POST.get('brand_model')
        product.imei_number = request.POST.get('imei')
        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock')
        product.product_description = request.POST.get('description')

        product.save()

        messages.success(request,"Product updated successsfully!", extra_tags="updated")
        return redirect('product_list')

    return render(request, 'edit_product.html', {'product': product})


def delete_product(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    product = get_object_or_404(Product, product_id=id)
    product.delete()
    return redirect('product_list')


def product_details(request, product_id):
    product = Product.objects.get(product_id=product_id)
    return render(request, 'product_details.html', {'product': product})


# ================== SUPPLIER ==================
def add_supplier(request):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        # 🔴 VALIDATION (THIS IS THE PLACE)
        if not name or not phone or not email or not address:
            return render(request, 'add_supplier.html', {
                'error': 'All fields are required!'
            })

        # ✅ SAVE DATA
        Supplier.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address
        )
        
        messages.success(request,"Product deleted successfully!",extra_tags="deleted")
        return redirect('supplier_list')

    return render(request, 'add_supplier.html')


def supplier_list(request):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


def edit_supplier(request, id):
    
    if not request.user.is_superuser:
     return redirect('staff_dashboard')
    supplier = Supplier.objects.get(supplier_id=id)   

    if request.method == "POST":
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('mobile')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        
        return redirect('supplier_list')

    # 🔥 SPA RENDER
    return render(request, 'edit_supplier.html',{'supplier': supplier})


def delete_supplier(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    supplier = Supplier.objects.get(supplier_id=id)
    supplier.delete()
    return redirect('supplier_list')


# ================== PURCHASE ==================
def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-date')

    for p in purchases:
        if p.purchase_price:
            p.total = p.quantity * p.purchase_price
        else:
            p.total = 0

    return render(request, 'purchase_list.html', {
        'purchases': purchases
    })

def add_purchase(request):

    products = Product.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":

        product_id = request.POST.get("product")
        supplier_id = request.POST.get("supplier")
        quantity = request.POST.get("quantity")
        purchase_price = request.POST.get("purchase_price")

        product = Product.objects.get(product_id=product_id)
        supplier = Supplier.objects.get(supplier_id=supplier_id)

        quantity = int(quantity)

        # Update Stock
        product.stock_quantity += quantity
        product.save()

        # Create Purchase
        Purchase.objects.create(
            product=product,
            supplier=supplier,
            quantity=quantity,
            purchase_price=purchase_price
        )

        messages.success(request, "Purchase added successfully!")

        return redirect('purchase_list')

    return render(request, 'add_purchase.html', {
        'products': products,
        'suppliers': suppliers
    })

def delete_purchase(request, id):
    purchase = Purchase.objects.get(id=id)
    purchase.delete()
    return redirect('purchase_list')


# ================== STAFF ==================
@login_required
def staff_list(request):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff_list = Staff.objects.all()
    return render(request, 'staff_list.html', {'staff_list': staff_list})

@login_required
def add_staff(request):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')

        Staff.objects.create(
            name=name,
            email=email,
            phone=phone,
            role=role
        )

        messages.success(request, "Staff added successfully")
        return redirect('staff_list')

    return render(request, 'add_staff.html')

@login_required
def edit_staff(request, id):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff = Staff.objects.get(id=id)

    if request.method == "POST":
        staff.name = request.POST.get('name')
        staff.email = request.POST.get('email')
        staff.phone = request.POST.get('phone')
        staff.role = request.POST.get('role')
        staff.save()

        messages.success(request, "Staff updated successfully")
        return redirect('staff_list')

    return render(request, 'edit_staff.html', {'staff': staff})

@login_required
def delete_staff(request, id):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff = Staff.objects.get(id=id)

    if request.method == "POST":   # 👈 IMPORTANT SECURITY
        staff.delete()
        messages.success(request, "Staff deleted successfully")
        return redirect('staff_list')

    return redirect('staff_list')


# ================== ATTENDANCE ==================
def attendance(request):
    attendance = Attendance.objects.all()
    return render(request, 'attendance.html', {'attendance': attendance})


from django.db.models import Q

def mark_attendance(request):
    staff_list = Staff.objects.all()

    selected_date = request.GET.get('date')  # 👈 GET date

    attendance_dict = {}

    if selected_date:
        records = Attendance.objects.filter(date=selected_date)
        for r in records:
            attendance_dict[r.staff.id] = r.status

    if request.method == "POST":
        date = request.POST.get('date')

        for staff in staff_list:
            status = request.POST.get(f"status_{staff.id}")

            obj = Attendance.objects.filter(staff=staff, date=date).first()

            if obj:
                obj.status = status
                obj.save()
            else:
                Attendance.objects.create(
                    staff=staff,
                    date=date,
                    status=status
                )

        messages.success(request, "Attendance saved successfully")
        return redirect(f'/mark-attendance/?date={date}')  # 👈 reload same date

    return render(request, 'mark_attendance.html', {
        'staff_list': staff_list,
        'attendance_dict': attendance_dict,
        'selected_date': selected_date
    })


def mark_attendance(request):
    staff_list = Staff.objects.all()
    attendance_dict = {}

    date = request.GET.get("date") or request.POST.get("date")

    if request.method == "POST":

        if request.method == "POST":
         print("FORM SUBMITTED ✅")   # 👈 ADD THIS

        for staff in staff_list:
            status = request.POST.get(f"status_{staff.id}")

            obj, created = Attendance.objects.get_or_create(
                staff=staff,
                date=date
            )

            obj.status = status
            obj.save()

            messages.success(request,"Attendance Saved Successfully ✅")

        return redirect(f'/mark-attendance/?date={date}')

    if date:
        records = Attendance.objects.filter(date=date)
        for r in records:
            attendance_dict[r.staff.id] = r.status

    return render(request, 'mark_attendance.html', {
        'staffs': staff_list,
        'attendance_dict': attendance_dict,
        'selected_date': date
    })





# ================== SALES ==================
from django.db.models import Sum

def invoice_list(request):

    sales = Sale.objects.all().order_by('-date')

    grand_total = Sale.objects.aggregate(
        total=Sum('total_price')
    )['total']

    if grand_total is None:
        grand_total = 0

    if request.user.is_staff:
        role = 'staff'
    else:
        role = 'admin'

    return render(request, 'invoice_list.html', {
        'sales': sales,
        'grand_total': grand_total,
        'role': role
    })


def create_sale(request):

    products = Product.objects.all()

    if request.method == "POST":

        customer_name = request.POST.get('customer')
        phone = request.POST.get('phone')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        product = Product.objects.get(product_id=product_id)


        quantity = int(quantity)
    
       # ✅ STOCK VALIDATION
        if quantity > product.stock_quantity:
            messages.error(request, f"Only {product.stock_quantity} items available in stock")
            return redirect('billing')

        customer, created = Customer.objects.get_or_create(name=customer_name)

        customer.phone = phone
        customer.save()

        product.stock_quantity = max(0, product.stock_quantity - quantity)

        product.save()

        total_price = product.price * quantity

        sale = Sale.objects.create(
            customer=customer,
            phone=phone,
            mobile=product,
            quantity=quantity,
            total_price=total_price
            )

        return redirect('invoice', sale_id=sale.id)

    return render(request, 'billing.html', {
        'products': products
    })

def sales_report(request):
    sales = Sale.objects.all()

    total_sales = sum(s.total_price for s in sales)

    # ✅ ADD THIS LINE (VERY IMPORTANT)
    from_page = request.GET.get('from')

    return render(request, 'sales_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'from_page': from_page,
    })

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'register.html')


def download_invoice(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    template = get_template('invoice_pdf.html')
    html = template.render({
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


def delete_sale(request, sale_id):
    if request.method == "POST":
        sale = Sale.objects.get(id=sale_id)

        # restore stock
        product = sale.mobile
        product.stock_quantity += sale.quantity
        product.save()

        sale.delete()

        messages.success(request, "Sale deleted successfully")

    return redirect('sales_report')   # or 'sales_report'



def edit_sale(request, id):
    sale = get_object_or_404(Sale, id=id)

    if sale.date.date() != date.today():
        messages.error(request, "❌ Sorry, you cannot edit old sales")
        return redirect('sales_report')

    # continue normal edit logic below
    
    products = Product.objects.all()
    from_page = request.GET.get('from')

    if request.method == "POST":
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')

        # ✅ EMPTY CHECK
        if not product_id or not quantity:
            messages.error(request, "All fields are required!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ INTEGER CHECK
        try:
            quantity = int(quantity)
        except:
            messages.error(request, "Enter valid quantity!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ ZERO CHECK
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than 0!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        product = get_object_or_404(Product, product_id=product_id)

        # ✅ STOCK CHECK
        if quantity > product.stock_quantity:
            messages.error(request, f"Only {product.stock_quantity} items available!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ FINAL SAVE (ONLY IF ALL VALID)
        sale.mobile = product
        sale.quantity = quantity
        sale.total_price = quantity * product.price
        sale.save()

        messages.success(request, "Sale updated successfully!")

        # ✅ REDIRECT BASED ON PAGE
        if from_page == "staff":
            return redirect('/sales_report/?from=staff')
        else:
            return redirect('/sales_report/?from=admin')

    return render(request, 'edit_sale.html', {
        'sale': sale,
        'products': products,
        'from_page': from_page
    })


def invoice_pdf(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    template = get_template('invoice_pdf.html')
    html = template.render({
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


def edit_purchase(request, id):
    purchase = Purchase.objects.get(id=id)

    if request.method == "POST":
        qty = int(request.POST.get("quantity"))

        purchase.quantity = qty
        purchase.save()

        messages.success(request,"Purchase updated successfully!")
        return redirect("purchase_list")

    return render(request, "edit_purchase.html", {
        "purchase": purchase
    })

def contact(request):
    return render(request, 'helpdesk.html')

def helpdesk(request):
    return render(request, 'helpdesk.html')



def attendance_pdf(request, date):
    attendance = Attendance.objects.filter(date=date).select_related('staff')

    template = get_template("attendance_pdf.html")
    html = template.render({"attendance": attendance, "date": date})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{date}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response

def sales_list(request):
    return render(request, 'sales_report.html')


def low_stock_products(request):
    products = Product.objects.filter(stock_quantity__lt=10)

    if request.user.is_staff:
        role = 'staff'
    else:
        role = 'admin'


    return render(request, 'low_stock.html', {
        'products': products
    })


def edit_purchase(request, id):
    purchase = Purchase.objects.get(id=id)
    product = purchase.product

    if request.method == "POST":
        qty = request.POST.get("quantity")

        # 🔒 VALIDATION 1 — EMPTY CHECK
        if not qty:
            messages.error(request, "Quantity is required")
            return redirect("edit_purchase", id=id)

        qty = int(qty)

        # 🔒 VALIDATION 2 — NEGATIVE CHECK
        if qty <= 0:
            messages.error(request, "Quantity must be greater than 0")
            return redirect("edit_purchase", id=id)

        old_qty = purchase.quantity
        difference = qty - old_qty

        # 🔒 VALIDATION 3 — STOCK SHOULD NOT GO NEGATIVE
        if product.stock_quantity + difference < 0:
            messages.error(request, "Not enough stock")
            return redirect("edit_purchase", id=id)

        # ✅ UPDATE
        product.stock_quantity += difference
        product.save()

        purchase.quantity = qty
        purchase.save()

        messages.success(request, "Purchase updated successfully")

        return redirect("purchase_list")

    return render(request, "edit_purchase.html", {
        "purchase": purchase
    })


def attendance_dates(request):
    today = today_date.today()

    dates = Attendance.objects.filter(date__lte=today) \
        .values('date') \
        .annotate(total=Count('id')) \
        .order_by('-date')

    return render(request, 'attendance_dates.html', {
        'dates': dates,
        'today': today
    })

def attendance_by_date(request, date):
    search = request.GET.get('search', '')

    attendance = Attendance.objects.filter(date=date).select_related('staff')

    if search:
        attendance = attendance.filter(staff__name__icontains=search)

    return render(request, 'attendance_day.html', {
        'attendance': attendance,
        'selected_date': date,
        'search': search
    })

def invoice(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    return render(request, 'invoice.html', {
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

def logout_page(request):
    logout(request)
    return redirect('login')


def set_captcha(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session['captcha'] = data.get('captcha')
        return JsonResponse({"status": "ok"})
    
def login_page(request):
     
    if request.method == "POST":

        print("POST DATA:",request.POST)

        action = request.POST.get("action")
        print("ACTION:", action)

        # ================= LOGIN =================
        if action == "login":

            request.session['step'] = ""

            username_input = request.POST.get("username")
            password = request.POST.get("password")

            # 🔥 CAPTCHA CHECK
            user_captcha = request.POST.get("captcha_input")
            real_captcha = request.session.get("captcha")

            if not user_captcha or user_captcha != real_captcha:
                messages.error(request, "Invalid captcha")
                request.session['step'] = ""
                return redirect('login')
            

            # 🔥 EMAIL OR USERNAME LOGIN
            try:
                user_obj = User.objects.get(email=username_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_input

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # ✅ CLEAR SESSION FLOW
                request.session['step'] = ""

                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('staff_dashboard')

            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')

        # ================= REGISTER =================
        elif action == "register":

            request.session['step'] = "register"

            full_name = request.POST.get("full_name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            role = request.POST.get("role")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            # 🔴 PHONE VALIDATION
            phone = request.POST.get("phone", "").strip()

            if not phone:
                request.session['step'] = "register"
                messages.error(request, "Phone number is required")
                return redirect('login')

            if not phone.isdigit() or len(phone) != 10:
                request.session['step'] = "register"
                messages.error(request, "Enter valid 10-digit phone number")
                return redirect('login')

            # 🔴 PASSWORD MATCH
            if password != confirm_password:
                request.session['step'] = "register"
                messages.error(request, "Passwords do not match")
                return redirect('login')

            # 🔴 STRONG PASSWORD VALIDATION
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[A-Z]", password):
                messages.error(request, "Password must include uppercase letter")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[a-z]", password):
                messages.error(request, "Password must include lowercase letter")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[0-9]", password):
                messages.error(request, "Password must include a number")
                request.session['step'] = "register"
                return redirect('login')

            if not re.search(r"[!@#$%^&*]", password):
                messages.error(request, "Password must include special character")
                request.session['step'] = "register"
                return redirect('login')

            # 🔴 EMAIL CHECK
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
                request.session['step'] = "register"
                return redirect('login')

            # 🔴 USERNAME AUTO FROM EMAIL
            username = email.split("@")[0]

            # 🔴 HANDLE DUPLICATE USERNAME
            if User.objects.filter(username=username).exists():
                username = username + str(User.objects.count())

            # ✅ CREATE USER
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # ✅ ROLE
            if role == "admin":
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_staff = True

            user.save()

            messages.success(request, "Account created successfully")
            request.session['step'] = ""
            return redirect('login')

        # ================= FORGOT PASSWORD =================
        elif action == "forgot":

            email = request.POST.get("email")

            if User.objects.filter(email=email).exists():

                # 🔥 GENERATE OTP
                otp = str(random.randint(100000, 999999))
                print("OTP DEBUG:", otp)   # ✅ ADD THIS LINE

                request.session['otp'] = otp
                request.session['temp_email'] = email
                request.session['step'] = "otp"



                server = smtplib.SMTP_SSL(
                "smtp.gmail.com",
                465,
                )

                server.login(
                "br6242442@gmail.com",
                "pobt yqlg dppy obmh"
                )

                server.sendmail(
                "br6242442@gmail.com",
                email,
                f"Subject: Your OTP - Sangeetha Mobiles\n\nYour OTP is: {otp}"
                )

                server.quit()

                messages.success(request, "OTP sent to your email")
                return render (request,'login.html',{
                    'show_otp':True
                })

            else:
                messages.error(request, "Email not registered")
                request.session['step'] = "login"
                return redirect('login')

        # ================= VERIFY OTP =================
        elif action == "verify_otp":

            entered_otp = request.POST.get("otp")

            if entered_otp == request.session.get('otp'):

                # ✅ VERY IMPORTANT
                request.session['step'] = 'reset'

                messages.success(request, "OTP Verified successfully")

                redirect('login')

            else:
                messages.error(request, "Invalid OTP")
                request.session['step'] = 'otp'
                return redirect('login')

        # ================= RESET PASSWORD =================
        elif action == "reset_password":

            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            email = request.session.get("temp_email")

            if not new_password or not confirm_password:
                messages.error(request, "All fields are required")
                request.session['step'] = "reset"
                return redirect('login')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                request.session['step'] = "reset"
                return redirect('login')

            if len(new_password) < 6:
                messages.error(request, "Password must be at least 6 characters")
                request.session['step'] = "reset"
                return redirect('login')

            email = request.session.get('temp_email')

            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()

                messages.success(request, "Password updated successfully")

                # 🔥 SECURITY CLEAN
                request.session.flush()

                return redirect('login')

            except:
                messages.error(request, "Something went wrong")
                return redirect('login')
            
    if request.method == "GET":
        request.session['step'] = ""

    return render(request, "login.html")

def add_product(request):

    if not request.user.is_superuser:
        return redirect('staff_dashboard')
    
    if request.method == "POST":
        mobile_name = request.POST.get('mobile_name')
        brand_model = request.POST.get('brand_model')
        imei = request.POST.get('imei')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')

        # 🔥 VALIDATE STOCK ONLY
        if not stock:
            return render(request, 'add_product.html', {'error': 'Stock is required'})

        stock = int(stock)

        # 🔥 CHECK PRODUCT BY NAME
        product = Product.objects.filter(mobile_name=mobile_name).first()

        if product:
            # ✅ UPDATE ONLY STOCK
            product.stock_quantity += stock
            product.save()
        else:
            # 🔥 PRICE REQUIRED ONLY FOR NEW PRODUCT
            if not price:
                return render(request, 'add_product.html', {'error': 'Price required for new product'})

            price = Decimal(price)

            Product.objects.create(
                mobile_name=mobile_name,
                brand_model_name=brand_model,
                imei_number=imei,
                price=price,
                stock_quantity=stock,
                product_description=description
            )

        
        messages.success(request,"Product added successfully!", extra_tags="added")
        return redirect('product_list')

    return render(request, 'add_product.html')


def edit_product(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    product = get_object_or_404(Product, product_id=id)

    if request.method == "POST":
        product.mobile_name = request.POST.get('mobile_name')
        product.brand_model_name = request.POST.get('brand_model')
        product.imei_number = request.POST.get('imei')
        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock')
        product.product_description = request.POST.get('description')

        product.save()

        messages.success(request,"Product updated successsfully!", extra_tags="updated")
        return redirect('product_list')

    return render(request, 'edit_product.html', {'product': product})


def delete_product(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    product = get_object_or_404(Product, product_id=id)
    product.delete()
    return redirect('product_list')


def product_details(request, product_id):
    product = Product.objects.get(product_id=product_id)
    return render(request, 'product_details.html', {'product': product})


# ================== SUPPLIER ==================
def add_supplier(request):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        # 🔴 VALIDATION (THIS IS THE PLACE)
        if not name or not phone or not email or not address:
            return render(request, 'add_supplier.html', {
                'error': 'All fields are required!'
            })

        # ✅ SAVE DATA
        Supplier.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address
        )
        
        messages.success(request,"Product deleted successfully!",extra_tags="deleted")
        return redirect('supplier_list')

    return render(request, 'add_supplier.html')


def supplier_list(request):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


def edit_supplier(request, id):
    
    if not request.user.is_superuser:
     return redirect('staff_dashboard')
    supplier = Supplier.objects.get(supplier_id=id)   

    if request.method == "POST":
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('mobile')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        
        return redirect('supplier_list')

    # 🔥 SPA RENDER
    return render(request, 'edit_supplier.html',{'supplier': supplier})


def delete_supplier(request, id):

    if not request.user.is_superuser:
     return redirect('staff_dashboard')

    supplier = Supplier.objects.get(supplier_id=id)
    supplier.delete()
    return redirect('supplier_list')


# ================== PURCHASE ==================
def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-date')

    for p in purchases:
        if p.purchase_price:
            p.total = p.quantity * p.purchase_price
        else:
            p.total = 0

    return render(request, 'purchase_list.html', {
        'purchases': purchases
    })


def add_purchase(request):

    products = Product.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":

        product_id = request.POST.get("product")
        supplier_id = request.POST.get("supplier")
        quantity = request.POST.get("quantity")
        purchase_price = request.POST.get("purchase_price")

        product = Product.objects.get(product_id=product_id)
        supplier = Supplier.objects.get(supplier_id=supplier_id)

        quantity = int(quantity)

        # Update Stock
        product.stock_quantity += quantity
        product.save()

        # Create Purchase
        Purchase.objects.create(
            product=product,
            supplier=supplier,
            quantity=quantity,
            purchase_price=purchase_price
        )

        messages.success(request, "Purchase added successfully!")

        return redirect('purchase_list')

    return render(request, 'add_purchase.html', {
        'products': products,
        'suppliers': suppliers
    })

def delete_purchase(request, id):
    purchase = Purchase.objects.get(id=id)
    purchase.delete()
    return redirect('purchase_list')


# ================== STAFF ==================
@login_required
def staff_list(request):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff_list = Staff.objects.all()
    return render(request, 'staff_list.html', {'staff_list': staff_list})

@login_required
def add_staff(request):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')

        Staff.objects.create(
            name=name,
            email=email,
            phone=phone,
            role=role
        )

        messages.success(request, "Staff added successfully")
        return redirect('staff_list')

    return render(request, 'add_staff.html')

@login_required
def edit_staff(request, id):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff = Staff.objects.get(id=id)

    if request.method == "POST":
        staff.name = request.POST.get('name')
        staff.email = request.POST.get('email')
        staff.phone = request.POST.get('phone')
        staff.role = request.POST.get('role')
        staff.save()

        messages.success(request, "Staff updated successfully")
        return redirect('staff_list')

    return render(request, 'edit_staff.html', {'staff': staff})

@login_required
def delete_staff(request, id):
    if not request.user.is_superuser:
        return redirect('login')   # 👈 ADD HERE

    staff = Staff.objects.get(id=id)

    if request.method == "POST":   # 👈 IMPORTANT SECURITY
        staff.delete()
        messages.success(request, "Staff deleted successfully")
        return redirect('staff_list')

    return redirect('staff_list')


# ================== ATTENDANCE ==================
def attendance(request):
    attendance = Attendance.objects.all()
    return render(request, 'attendance.html', {'attendance': attendance})

def mark_attendance(request):
    staff_list = Staff.objects.all()

    selected_date = request.GET.get('date')  # 👈 GET date

    attendance_dict = {}

    if selected_date:
        records = Attendance.objects.filter(date=selected_date)
        for r in records:
            attendance_dict[r.staff.id] = r.status

    if request.method == "POST":
        date = request.POST.get('date')

        for staff in staff_list:
            status = request.POST.get(f"status_{staff.id}")

            obj = Attendance.objects.filter(staff=staff, date=date).first()

            if obj:
                obj.status = status
                obj.save()
            else:
                Attendance.objects.create(
                    staff=staff,
                    date=date,
                    status=status
                )

        messages.success(request, "Attendance saved successfully")
        return redirect(f'/mark-attendance/?date={date}')  # 👈 reload same date

    return render(request, 'mark_attendance.html', {
        'staff_list': staff_list,
        'attendance_dict': attendance_dict,
        'selected_date': selected_date
    })


def mark_attendance(request):
    staff_list = Staff.objects.all()
    attendance_dict = {}

    date = request.GET.get("date") or request.POST.get("date")

    if request.method == "POST":

        if request.method == "POST":
         print("FORM SUBMITTED ✅")   # 👈 ADD THIS

        for staff in staff_list:
            status = request.POST.get(f"status_{staff.id}")

            obj, created = Attendance.objects.get_or_create(
                staff=staff,
                date=date
            )

            obj.status = status
            obj.save()

            messages.success(request,"Attendance Saved Successfully ✅")

        return redirect(f'/mark-attendance/?date={date}')

    if date:
        records = Attendance.objects.filter(date=date)
        for r in records:
            attendance_dict[r.staff.id] = r.status

    return render(request, 'mark_attendance.html', {
        'staffs': staff_list,
        'attendance_dict': attendance_dict,
        'selected_date': date
    })





# ================== SALES ==================
from django.db.models import Sum

def invoice_list(request):

    sales = Sale.objects.all().order_by('-date')

    grand_total = Sale.objects.aggregate(
        total=Sum('total_price')
    )['total']

    if grand_total is None:
        grand_total = 0

    if request.user.is_staff:
        role = 'staff'
    else:
        role = 'admin'

    return render(request, 'invoice_list.html', {
        'sales': sales,
        'grand_total': grand_total,
        'role': role
    })

def create_sale(request):

    products = Product.objects.all()

    if request.method == "POST":

        customer_name = request.POST.get('customer')
        phone = request.POST.get('phone')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        product = Product.objects.get(product_id=product_id)


        quantity = int(quantity)
    
       # ✅ STOCK VALIDATION
        if quantity > product.stock_quantity:
            messages.error(request, f"Only {product.stock_quantity} items available in stock")
            return redirect('billing')

        customer, created = Customer.objects.get_or_create(name=customer_name)

        customer.phone = phone
        customer.save()

        product.stock_quantity = max(0, product.stock_quantity - quantity)

        product.save()

        total_price = product.price * quantity

        sale = Sale.objects.create(
            customer=customer,
            phone=phone,
            mobile=product,
            quantity=quantity,
            total_price=total_price
            )

        return redirect('invoice', sale_id=sale.id)

    return render(request, 'billing.html', {
        'products': products
    })

def sales_report(request):
    sales = Sale.objects.all()

    total_sales = sum(s.total_price for s in sales)

    # ✅ ADD THIS LINE (VERY IMPORTANT)
    from_page = request.GET.get('from')

    return render(request, 'sales_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'from_page': from_page,
    })

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'register.html')

def download_invoice(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    template = get_template('invoice_pdf.html')
    html = template.render({
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


def delete_sale(request, sale_id):
    if request.method == "POST":
        sale = Sale.objects.get(id=sale_id)

        # restore stock
        product = sale.mobile
        product.stock_quantity += sale.quantity
        product.save()

        sale.delete()

        messages.success(request, "Sale deleted successfully")

    return redirect('sales_report')   # or 'sales_report'


def edit_sale(request, id):
    sale = get_object_or_404(Sale, id=id)

    if sale.date.date() != date.today():
        messages.error(request, "❌ Sorry, you cannot edit old sales")
        return redirect('sales_report')

    # continue normal edit logic below
    
    products = Product.objects.all()
    from_page = request.GET.get('from')

    if request.method == "POST":
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')

        # ✅ EMPTY CHECK
        if not product_id or not quantity:
            messages.error(request, "All fields are required!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ INTEGER CHECK
        try:
            quantity = int(quantity)
        except:
            messages.error(request, "Enter valid quantity!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ ZERO CHECK
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than 0!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        product = get_object_or_404(Product, product_id=product_id)

        # ✅ STOCK CHECK
        if quantity > product.stock_quantity:
            messages.error(request, f"Only {product.stock_quantity} items available!")
            return render(request, 'edit_sale.html', {
                'sale': sale,
                'products': products,
                'from_page': from_page
            })

        # ✅ FINAL SAVE (ONLY IF ALL VALID)
        sale.mobile = product
        sale.quantity = quantity
        sale.total_price = quantity * product.price
        sale.save()

        messages.success(request, "Sale updated successfully!")

        # ✅ REDIRECT BASED ON PAGE
        if from_page == "staff":
            return redirect('/sales_report/?from=staff')
        else:
            return redirect('/sales_report/?from=admin')

    return render(request, 'edit_sale.html', {
        'sale': sale,
        'products': products,
        'from_page': from_page
    })


def invoice_pdf(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    template = get_template('invoice_pdf.html')
    html = template.render({
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response

def edit_purchase(request, id):
    purchase = Purchase.objects.get(id=id)

    if request.method == "POST":
        qty = int(request.POST.get("quantity"))

        purchase.quantity = qty
        purchase.save()

        messages.success(request,"Purchase updated successfully!")
        return redirect("purchase_list")

    return render(request, "edit_purchase.html", {
        "purchase": purchase
    })

def contact(request):
    return render(request, 'helpdesk.html')

def helpdesk(request):
    return render(request, 'helpdesk.html')

def attendance_pdf(request, date):
    attendance = Attendance.objects.filter(date=date).select_related('staff')

    template = get_template("attendance_pdf.html")
    html = template.render({"attendance": attendance, "date": date})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{date}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response

def sales_list(request):
    return render(request, 'sales_report.html')


def low_stock_products(request):
    products = Product.objects.filter(stock_quantity__lt=10)

    if request.user.is_staff:
        role = 'staff'
    else:
        role = 'admin'


    return render(request, 'low_stock.html', {
        'products': products
    })

def edit_purchase(request, id):
    purchase = Purchase.objects.get(id=id)
    product = purchase.product

    if request.method == "POST":
        qty = request.POST.get("quantity")

        # 🔒 VALIDATION 1 — EMPTY CHECK
        if not qty:
            messages.error(request, "Quantity is required")
            return redirect("edit_purchase", id=id)

        qty = int(qty)

        # 🔒 VALIDATION 2 — NEGATIVE CHECK
        if qty <= 0:
            messages.error(request, "Quantity must be greater than 0")
            return redirect("edit_purchase", id=id)

        old_qty = purchase.quantity
        difference = qty - old_qty

        # 🔒 VALIDATION 3 — STOCK SHOULD NOT GO NEGATIVE
        if product.stock_quantity + difference < 0:
            messages.error(request, "Not enough stock")
            return redirect("edit_purchase", id=id)

        # ✅ UPDATE
        product.stock_quantity += difference
        product.save()

        purchase.quantity = qty
        purchase.save()

        messages.success(request, "Purchase updated successfully")

        return redirect("purchase_list")

    return render(request, "edit_purchase.html", {
        "purchase": purchase
    })

def attendance_dates(request):
    today = today_date.today()

    dates = Attendance.objects.filter(date__lte=today) \
        .values('date') \
        .annotate(total=Count('id')) \
        .order_by('-date')

    return render(request, 'attendance_dates.html', {
        'dates': dates,
        'today': today
    })

def attendance_by_date(request, date):
    search = request.GET.get('search', '')

    attendance = Attendance.objects.filter(date=date).select_related('staff')

    if search:
        attendance = attendance.filter(staff__name__icontains=search)

    return render(request, 'attendance_day.html', {
        'attendance': attendance,
        'selected_date': date,
        'search': search
    })

def invoice(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    subtotal = sale.total_price
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    return render(request, 'invoice.html', {
        'sale': sale,
        'subtotal': subtotal,
        'gst': gst,
        'grand_total': grand_total
    })

def logout_page(request):
    logout(request)
    return redirect('login')

from django.http import JsonResponse
import json

def set_captcha(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session['captcha'] = data.get('captcha')
        return JsonResponse({"status": "ok"})
    
def reports(request):
    return render(request, 'reports.html')









    











    

