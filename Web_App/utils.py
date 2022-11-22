from datetime import datetime
from .models import *
from json import loads


def get_sub_categories():
    products = Product.objects.all()
    sub_categories = []

    for item in products:
        if item.sub_category not in sub_categories: sub_categories.append(item.sub_category)

    return sub_categories

def get_order_items(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_items = order.orderitem_set.all()
    else:
        try: cart = loads(request.COOKIES['cart'])
        except: cart = {}
        order_items = []
        order_total = {'get_cart_total': 0, 'get_cart_items': 0}
        cart_items = order_total['get_cart_items']
        order = Order.objects.create(
            complete=False
        )
        for item in cart:
            cart_items += cart[item]['quantity']
            product = Product.objects.get(id=item)
            total = (product.price * cart[item]['quantity'])
            order_total['get_cart_total'] += total
            order_total['get_cart_items'] += cart[item]['quantity']
            item = { 'product': product, 'quantity': cart[item]['quantity'], 'get_total': total}
            order_items.append(item)

        for item in order_items:
                OrderItem.objects.create(
                product = item['product'],
                order = order,
                quantity = item['quantity']
            )

    return {'order_items': order_items, 'order': order}

def confirm_order(request, order_data, order):
    transaction_id = datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user.customer
        print(customer.name)
        order.customer = customer
    else:
        name = order_data['user_form']['name']
        email = order_data['user_form']['email']
        customer, created = Customer.objects.get_or_create(name=name, email=email)
        customer.save()
        order.customer = customer

    order.transaction_id = transaction_id
    order.complete = True
    order.save()

    ShippingAddress.objects.create(
        customer = customer,
        order = order,
        address = order_data['shipping_form']['address'],
        city = order_data['shipping_form']['city'],
        state = order_data['shipping_form']['state'],
        zipcode = order_data['shipping_form']['zipcode'],
        
        )
    
   