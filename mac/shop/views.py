from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Contact
from django.contrib import messages
from math import ceil

# Create your views here.
def index(request):
    # products = Product.objects.all()
    # n = len(products)
    # nslides = n // 4 + ceil((n / 4) - (n // 4))
    # params = {'no_of_slides' : nslides, 'range' : range(1, nslides), 'product' : products}
    # allprods = [[products, range(1, nslides), nslides], [products, range(1, nslides), nslides]]
    # params = {'allprods' : allprods}
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
    return render(request, 'shop/checkout.html')