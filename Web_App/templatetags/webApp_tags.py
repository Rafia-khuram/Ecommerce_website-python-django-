from ..models import Image, Product, Care
from django import template

register = template.Library()

@register.simple_tag
def get_image(product):
    image = (product.image_set.all())[0]
    return str(image.image)

@register.simple_tag
def sub_categories(category):
    products = Product.objects.filter(category=category)
    categories = []
    for item in products:
        if item.sub_category not in categories:
            categories.append(item.sub_category)
    return categories

@register.simple_tag
def get_care(product):
    return product.care_set.all()
    

