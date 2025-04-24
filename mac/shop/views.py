from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Orders, Product, Contact, OrderUpdate
from django.contrib import messages
from math import ceil
import json

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
        # Send the email
        send_mail(
            subject,
            f"Message from {name} ({email}):\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            ['support@myshop.com'],
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
    return render(request, 'shop/search.html')

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

        order = Orders(items_json=items_json, name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank' : thank, 'id' : id})
    return render(request, 'shop/checkout.html')