from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Product, Order, OrderItem, Bill
from .forms import RegisterForm, ProductForm
import io

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome {user.username}, your account has been created successfully! 🎉")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login(request):
    return render(request, 'core/login.html')

from django.contrib.auth import authenticate, login as auth_login

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not password:
            messages.error(request, "Both username and password are required.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}! 🎉 login successfully!!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    return render(request, 'core/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully. 👋")
    return redirect("home")

def home(request):
    products = Product.objects.all()
    return render(request, 'core/home.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    # store quantity
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True  # important: mark session as changed
    messages.success(request, f"{product.name} has been added to your cart! 🛒")
    return redirect('cart')

@login_required
def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        action = request.POST.get("action")
        if action == "increase":
            cart[product_id] += 1
        elif action == "decrease":
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]
        request.session["cart"] = cart
    return redirect("cart")

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = product.price * qty
        total += subtotal
        items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })
    return render(request, 'core/cart.html', {
        'items': items,
        'total': total,
        'cart_empty': len(items) == 0
    })
    
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session["cart"] = cart
    return redirect("cart")
    
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')
    
    order = Order.objects.created(user=request.user)
    subtotal = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        price  = product.price
        OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
        subtotal += price * qty
        product.stock -= qty
        product.save()
        
    tax = subtotal * 0.10
    total = subtotal + tax
    order.total = total
    order.save()
    
    bill = Bill.objects.create(order=order, subtotal=subtotal, tax=tax, total=total)
    bill.pdf = generate_pdf_bill(bill)
    bill.save()
    
    del request.session['cart']
    return redirect('invoice', bill_id=bill.id)

def generate_pdf_bill(bill):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"Invoice for Order {bill.order.id}")
    p.drawString(100, 730, f"User: {bill.order.user.username}")
    p.drawString(100, 710, f"Subtotal: ${bill.subtotal}")
    p.drawString(100, 690, f"Tax: ${bill.tax}")
    p.drawString(100, 670, f"Total: ${bill.total}")
    
    p.save()
    buffer.seek(0)
    return buffer

@login_required
def invoice(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, order__user=request.user)
    response = HttpResponse(bill.pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{bill_id}.pdf"'
    return response


# Product Crud
def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # include request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully! ✅")
            return redirect('product-list')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully! ✏️")
            return redirect('product-list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully! 🗑️")
        return redirect('product-list')
    return render(request, 'core/product_confirm_delete.html', {'product': product})

# user side
@login_required
def view_product(request):
    products = Product.objects.all()
    return render(request, "core/products/view_product.html", {"products": products})

@login_required
def place_order(request):
    if request.method == "POST":
        order = Order.objects.create(user=request.user, status="Pending", total=0)
        total = 0
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                product_id = key.split("_")[1]
                quantity = int(value)
                if quantity > 0:
                    product = get_object_or_404(Product, id=product_id)
                    item_price = product.price * quantity
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=item_price
                    )
                    total += item_price
        order.total = total
        order.save()
        return redirect("view_order", order_id=order.id)
    return redirect("view_product")

@login_required
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "core/view_order.html", {"order": order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "core/order_history.html", {"orders": orders})




