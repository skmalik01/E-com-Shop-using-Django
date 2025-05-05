from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Orders, Product, Contact, OrderUpdate
from django.contrib import messages
from django.db.models import Q
from math import ceil
import json
import razorpay

# Create your views here.
def index(request):
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nslides), nslides])
    params = {'allprods' : allprods}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = Contact(name=name, email=email, subject=subject, message=message)
        contact.save()
        send_mail(
            subject=f"New Contact Form Submission: {subject}",
            message=f"New message received!\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['malikshaikh0105@gmail.com'],
            fail_silently=False,
        )

        
        send_mail(
            subject="Thank you for contacting MyShop!",
            message=f"Hi {name},\n\nThank you for contacting us.\nWe have received your message and will respond within 24 hours.\n\n- Team MyShop",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, f"Thank you {name}, your message has been received!")

    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('OrderId')
        email = request.POST.get('email')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text' : item.update_desc, 'time' : item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request, 'shop/tracker.html')

def search(request):
    
    if request.method == "POST":
        query = request.POST.get('query', '').strip()
    else:
        query = request.GET.get('query', '').strip()
    if len(query) < 2:
        products = []
        message = "Please enter a more relevant search term."
    else:
        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(category__icontains=query) |
            Q(desc__icontains=query)
        )
        message = "" if products else "No products found."

    return render(request, 'shop/search.html', {
        'products': products,
        'query': query,
        'message': message
    })

def productView(request, myid):
    #fetch the product using id
    try:
        # Use get instead of filter
        product = Product.objects.get(id=myid)
    except Product.DoesNotExist:
        raise Http404("Product not found")
    return render(request, 'shop/prodView.html', {'product' : product})

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address1') + " " + request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        payment_id = request.POST.get('payment_id')  # Razorpay Payment ID from frontend
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Razorpay Signature Verification
        if payment_id:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            try:
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': razorpay_signature
                }

                client.utility.verify_payment_signature(params_dict)  # Will raise error if invalid
                payment_verified = True
            except:
                payment_verified = False
        else:
            payment_verified = False  # If no payment done (Cash on Delivery maybe)

        # Save Order
        order = Orders(
            items_json=items_json,
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            payment_id=payment_id if payment_verified else None  # Save payment_id only if verified
        )
        order.save()

        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
        update.save()
        
        # Items loop
        items = json.loads(items_json)
        item_details = ""
        total_price = 0

        for product_id, values in items.items():
            qty = values[0]
            price = values[2]
            total_price += qty * price

            try:
                pk = int(product_id[2:])  # Assuming product id like "pr5"
                product = Product.objects.get(id=pk)
                product_name = product.product_name
            except:
                product_name = f"Unknown Product ({product_id})"

            item_details += f"{product_name}  |  Qty: {qty}  |  ₹{price} each\n"

        # Payment success/fail message
        if payment_verified:
            payment_msg = f"Payment received successfully via Razorpay.\n🆔 Payment ID: {payment_id}\n"
        else:
            payment_msg = "⚠️ Payment pending or failed. Please contact support if amount was deducted.\n"

        # 📨 Send email to user
        message_body = f"""
Hi {name},

🧾 Your Order has been placed successfully!

🆔 Order ID: {order.order_id}

{payment_msg}

📦 Items Ordered:
{item_details}

💰 Total Price: ₹{total_price}

📍 Delivery Address:
{address}, {city}, {state}, {zip_code}
📞 Contact: {phone}

⏰ Your order will be delivered within 24 hours.

Thank you for shopping with us!
– Team MyShop
"""
        message_body += "\nFor any queries, contact us at support@myshop.com\n"


        send_mail(
            "Order Confirmation - MyShop",
            message_body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank' : thank, 'id' : id})
    return render(request, 'shop/checkout.html')
