from .utils import get_sub_categories, get_order_items, confirm_order
from .models import *
from json import load, loads
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .forms import CreateUserForm

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def register(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account created for ' + user)
				return redirect('login_user')
		
		context = {'form':form}

		return render(request, 'register.html', context)

def login_user(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('index')
			else:
				messages.info(request, 'Username or password is incorrect')
            
		return render(request, 'login_user.html')

def logout_user(request):
	logout(request)
	return redirect('login_user')

def index(request):
    images = Image.objects.all()
    context = {'images': images }
    if request.user.is_authenticated:
        customer, created  = Customer.objects.get_or_create(user=request.user, name= request.user.username)
        context.update({'customer': customer})
        
    return render(request, 'index.html', context)

def products(request, category):
    images = Image.objects.all()

    if  category == 'Men' or category == 'Women':
        products = Product.objects.filter(category=category)
        return render(request, 'products.html', {'products': products, 'images': images, 'category': category})
    
    sub_categories = get_sub_categories()

    if category in sub_categories:
        products = Product.objects.filter(sub_category=category)
        
        return render(request, 'products.html', {'products': products, 'images': images, 'category': category})
  
def product_detail(request, pk):
    product = Product.objects.get(id=int(pk))
    images = product.image_set.all()
    care = product.care_set.all()
    skus = product.sku_set.all()
    context = {'product': product, 'images': images, 'care': care, 'skus': skus}
    
    return render(request, 'product_detail.html', context)
    
def view_transactions(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    customer_orders = customer.order_set.all()

    return render(request, 'view_transactions.html', {'customer_orders': customer_orders})

def cart(request):
    context = get_order_items(request)    
    return render(request, 'cart.html' , context)

def checkout(request):
    context = get_order_items(request)   
    context.update({
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    })

    return render(request, 'checkout.html' , context)

def process_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order_data = loads(request.body)
    confirm_order(request, order_data, order)

    return JsonResponse('Payment Complete', safe=False)

def update_item(request):
   
    cart_data = loads(request.body)
    product_id = cart_data['product_id']
    action = cart_data['action']
    
    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product = product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse("Item was added", safe=False)

def payment(request, order_id):
    order = Order.objects.get(pk=order_id)
    form_data = loads(request.body)
    checkout_session = stripe.checkout.Session.create(
        payment_method_types = ['card'],
        line_items=[{
            'price_data':{
            'currency':'usd',
            'product_data':{
            'name':order.id,
            },
            'unit_amount':order.get_cart_total*100,
        },
        'quantity': 1,
        }],
    metadata = {"order_id": order_id},
    mode='payment',
    success_url= f'http://127.0.0.1:8000/payment_success?form_data={form_data}&order_id={order_id}',
    cancel_url= 'http://127.0.0.1:8000/cancel',
        )
    return JsonResponse({
        'id': checkout_session.id
    })
    
def payment_success(request):
    form = request.GET
    form_data = (form['form_data']).replace("\'", "\"")
    order_id = form['order_id']
    order = Order.objects.get(pk=int(order_id))
    form_data = loads(form_data)
    confirm_order(request, form_data, order)

    return redirect('index')
    

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.WEBHOOK_SECRET
    )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        global session
        session = event['data']['object']

    customer_email = session['customer_details']['email']
    send_mail(
        subject = "Order Details",
        message = "Thankyou for shopping, Your Order has been confirmed",
        recipient_list=[customer_email],
        from_email="abc@example.com"
    )
    return HttpResponse(status=200)


def payment_cancel(request):
   return HttpResponse("Payment Cancelled")


def load_data(request):
    with open('garments.json', 'r') as data:
        parsed_json = load(data)

    for garment in parsed_json:
        product_obj = Product(
           name = garment['name'],
           category = garment['category'][0],
           price = garment['price'],
           color = list(garment['image_urls'].keys())[0],
           sub_category = garment['category'][1],
           description = garment['description'][0],
           gender = garment['gender'],
        ) 
        product_obj.save()

        for item in garment['care']:
            care = Care(product = product_obj, care = item)
            care.save()

        for item in list(garment['image_urls'].values())[0]:
            image = Image(product = product_obj, image = item)
            image.save()

        skus = list(garment['skus'].values())

        for item in skus:
            sku = Sku(
                product = product_obj,
                color = item['color'],
                size = item['size'],
                out_of_stock = item['out_of_stock'],
                price = item['price']   
            )
            sku.save()

    return HttpResponse("success")

