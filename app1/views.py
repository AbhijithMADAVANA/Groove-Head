
from django.shortcuts import render
from django.utils import timezone
from typing import OrderedDict
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, OrderBy, OrderWrt
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import HttpResponse, redirect, render

from django.urls import reverse
from app1.models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from admin_panel.forms import CreateProductForm, OrderForm
from django.contrib import auth
from app1.admin import CouponAdmin, OrderAdmin, OrderProductAdmin, PaymentAdmin, RedeemedCouponAdmin, WalletAdmin
from userauths.models import *
from datetime import datetime
from .models import Product, Category, ProductOffer, CategoryOffer
from admin_panel.models import Banner
#for profile validation

def is_valid_phone(phone):
    # Phone number should be exactly 10 digits
    phone_pattern = "^\d{10}$"
    return re.match(phone_pattern, str(phone)) is not None

def is_valid_postal_code(postal_code):
    # Postal code should be a valid format based on your requirement
    postal_code_pattern = "^[0-9]{6}$"
    return re.match(postal_code_pattern, postal_code) is not None

def is_not_empty_or_whitespace(value):
    # Check if the value is not empty or contains only whitespace
    return bool(value.strip())






from django.shortcuts import render
from django.utils.timezone import now
from .models import Product, Category, ProductOffer, CategoryOffer

def index(request):
    products = Product.objects.filter(featured=True, status=True)
    product1 = Product.objects.filter(status=True).order_by("-id")[:6]
    categories = Category.objects.all()
    banners =Banner.objects.filter(is_active=True)
    try:
        discount_offer = ProductOffer.objects.get(active=True)
    except ProductOffer.DoesNotExist:
        discount_offer = None
    if discount_offer:
        current_date = now()
        if current_date > discount_offer.end_date or current_date < discount_offer.start_date:
            discount_offer.active = False
            discount_offer.save()
    
    try:
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except CategoryOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            products_with_discount = Product.objects.filter(category=dis.category, status=True)
            current_date = now()
            if current_date > dis.end_date or current_date < dis.start_date:
                dis.active = False
                dis.save()

    context = {
        "products": products,
        "product1": product1,
        "categories": categories,
        "discount_offer": discount_offer,
        "discounted_offer": discounted_offer,
        'banners':banners,
    }
    return render(request, 'app1/index.html', context)






    


def product_list(request):
    products = Product.objects.filter(status=True)
    categories = Category.objects.all()

    
    per_page = 10  
    paginator = Paginator(products, per_page)

    page = request.GET.get('page')
    productss = paginator.get_page(page)

    try:
        discount_offer = ProductOffer.objects.get(active=True)
    except ProductOffer.DoesNotExist:
        discount_offer = None
        
    try:
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except CategoryOffer.DoesNotExist:
        discounted_offer = None

    context = {
        "products": products,
        "categories": categories,
        "productss": productss,
        "discount_offer": discount_offer,
        "discounted_offer": discounted_offer
    }
    
    return render(request, 'app1/product_list.html', context)



def category_list_view(request):

    categories = Category.objects.all()

    context = {
        "categories":categories
    }
   
    return render (request,'app1/category_list.html',context)

def category_product_list(request, cid):
    category = Category.objects.get(cid=cid)
    product = Product.objects.filter(category=category,status =True)
    
    try:
        
        discount_offer = ProductOffer.objects.get(active=True)
    except ProductOffer.DoesNotExist:
        discount_offer = None
    
    
                        
    try:
        
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except ProductOffer.DoesNotExist:
        discounted_offer = None
    if discounted_offer:
        for dis in discounted_offer:
            products_with_discount = Product.objects.filter(category=dis.category, status=True)
            current_date = timezone.now()
            if current_date > dis.end_date:
                dis.active = False
                dis.save()
    
    
    
    context ={
        "category":category,
        "product":product,
        "discount_offer":discount_offer,
        "discounted_offer":discounted_offer
    }
    
    return render(request,'app1/category_product_list.html', context)





    
                        

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now  # Update the import statement

# ... other import statements ...

def product_detail(request, pid):
    try:
        product = Product.objects.get(pid=pid)
        p_images = product.p_images.all()
        variants = ProductVariant.objects.filter(product=product)
        distinct_colors = variants.values_list('color__name', flat=True).distinct()

        selected_color = request.GET.get('selected_color')
        selected_variants = None
        selected_variant_images = None

        
        try:
            discount_offer = ProductOffer.objects.get(active=True)
        except ProductOffer.DoesNotExist:
            discount_offer = None

        try:
            discounted_offer = CategoryOffer.objects.filter(active=True)
        except ProductOffer.DoesNotExist:
            discounted_offer = None

        if discounted_offer:
            for dis in discounted_offer:
                products_with_discount = Product.objects.filter(category=dis.category, status=True)
                current_date = now()  # Fix the import here
                if current_date > dis.end_date:
                    dis.active = False
                    dis.save()

        if not selected_color:
            default_variant = variants.first()
            if default_variant:
                selected_color = default_variant.color.name
                selected_variants = variants.filter(color__name=selected_color)
                selected_variant_images = default_variant.v_images.all()
        else:
            sel_color = Color.objects.get(name=selected_color)
            selected_variants = variants.filter(color=sel_color)

            if selected_variants.exists():
                selected_variant = selected_variants.first()
                selected_variant_images = selected_variant.v_images.all()

    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

    context = {
        "product": product,
        "p_images": p_images,
        "distinct_colors": distinct_colors,
        "variants": variants, 
        "selected_color": selected_color,
        "selected_variants": selected_variants,
        "selected_variant_images": selected_variant_images,
        "discount_offer": discount_offer,
        "discounted_offer": discounted_offer
    }
    return render(request, 'app1/product-detail.html', context)

####################################################################################################

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
     cart = request.session.create()
    return cart

@login_required(login_url='userauths:sign-in')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'app1/cart.html', context)

@login_required(login_url='userauths:sign-in')
def add_cart(request, pid):
   
   
   color = request.GET.get('color')
   if color is None or color.lower() == 'none':
       messages.error(request, 'Please choose a color', extra_tags='danger')
   
       return HttpResponseRedirect(reverse('app1:product-detail', args=(pid,)))
   
   else:
    
    sel=Color.objects.get(name=color)
    print(sel)
    print(color)
    
    product = Product.objects.get(pid=pid)

    try:
        variant = ProductVariant.objects.get(product=product, color=sel.id)
    except ProductVariant.DoesNotExist:
        messages.warning(request, 'Variation not available, please select another variation')
        return HttpResponseRedirectBase(reverse('app1:product_detail', args=(pid)))

    if variant.stock_count >= 1:
        if request.user.is_authenticated:
            try:
                is_cart_item_exists = CartItem.objects.filter(
                    user=request.user, product=product, variations=variant).exists()
            except CartItem.DoesNotExist:
                is_cart_item_exists = False

            if is_cart_item_exists:
                to_cart = CartItem.objects.get(user=request.user, product=product, variations=variant)
                variation = to_cart.variations
                if to_cart.quantity < variation.stock_count:
                    to_cart.quantity += 1
                    to_cart.save()
                else:
                    messages.success(request, "Product out of stock")
            else:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                except Cart.MultipleObjectsReturned:
                    # If multiple records exist, choose the first one
                    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(cart_id=_cart_id(request))
                to_cart = CartItem.objects.create(
                    user=request.user,
                    product=product,
                    variations=variant,
                    quantity=1,
                    is_active=True,
                    cart=cart  # Associate the CartItem with the Cart
                )
            return redirect('app1:shopping_cart')
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.MultipleObjectsReturned:
               
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
            is_cart_item_exists = CartItem.objects.filter(cart=cart, product=product, variations=variant).exists()
            if is_cart_item_exists:
                to_cart = CartItem.objects.get(cart=cart, product=product, variations=variant)
                to_cart.quantity += 1
            else:
                to_cart = CartItem(cart=cart, product=product, variations=variant, quantity=1)
            to_cart.save()
            return redirect('cart:shopping_cart')
    else:
        messages.warning(request, 'This item is out of stock.')
        return redirect('app1:product-detail', pid)

    messages.warning(request, 'Variant not found.') 
    return redirect('app1:product-detail', pid)




def remove_cart(request, pid, cart_item_id):
    
    product = get_object_or_404(Product, pid=pid)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            variant = cart_item.variations
            variant.stock_count += 1
            cart_item.quantity -= 1

            variant.save()
            cart_item.save()    
        else:
            cart_item.delete()
    except:
        pass
    return redirect('app1:shopping_cart')



def remove_cart_item(request, pid, cart_item_id):
    product = get_object_or_404(Product, pid=pid)

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, remove the cart item associated with the user
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # If the user is not authenticated, remove the cart item associated with the session cart
            cart_item = CartItem.objects.get(product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
        
        # Delete the cart item
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass  
    return redirect('app1:shopping_cart')




def newcart_update(request):
    new_quantity = 0
    total = 0
    tax = 0
    grand_total = 0
    quantity=0
    counter=0
    
    if request.method == 'POST' and request.user.is_authenticated:
        prod_id = request.POST.get('product_id')
        
        cart_item_id = int(request.POST.get('cart_id'))
        qty=int(request.POST.get('qty'))
        counter=int(request.POST.get('counter'))
        
        product = get_object_or_404(Product, pid=prod_id)
        

        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart item not found'})
        
        if cart_item.variations:
            
            print(cart_item.variations)
            variation = cart_item.variations  
            if cart_item.quantity < variation.stock_count:
                cart_item.quantity += 1
                cart_item.save()
               
                sub_total=cart_item.quantity * variation.price
                new_quantity = cart_item.quantity
            else:
                message = "out of stock"
                return JsonResponse({'status': 'error', 'message': message})      
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        print(new_quantity,total,tax,grand_total,sub_total)       
        
        

    if new_quantity ==0:
        message = "out of stock"
        return JsonResponse({'status': 'error', 'message': message})
    else:
        return JsonResponse({
            'status': "success",
            'new_quantity': new_quantity,
            "total": total,
            "tax": tax,
            'counter':counter,
            "grand_total": grand_total,
            "sub_total":sub_total,
            
        })
    
def remove_cart_item_fully(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            counter = int(request.POST.get('counter'))
            product_id = request.POST.get('product_id')
            cart_item_id = int(request.POST.get('cart_id'))

            # Get the product and cart item
            product = get_object_or_404(Product, pid=product_id)
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)

            
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                sub_total = cart_item.quantity * cart_item.variations.price

                total = 0
                quantity = 0

                for cart_item in cart_items:
                    total += (cart_item.variations.price * cart_item.quantity)
                    quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + tax
                current_quantity = cart_item.quantity

                return JsonResponse({
                    'status': 'success',
                    'tax': tax,
                    'total': total,
                    'grand_total': grand_total,
                    'counter': counter,
                    'new_quantity': current_quantity,
                    'sub_total': sub_total,  # Updated quantity
                })
            else:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
                cart_item.delete()
                message = "the cart item has bee deleted"
                return JsonResponse({'status': 'error', 'message': message}) 

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return HttpResponseBadRequest('Invalid request')



@login_required(login_url='userauths:sign-in')
def checkout(request,total=0, quantity=0, cart_items=None):
        
    if not request.user.is_authenticated:
        return redirect('app1:index')
    if 'coupon_discount' in request.session:
                del request.session['coupon_discount']
    try:
        tax = 0
        grand_total = 0
        coupon_discount = 0

        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user, is_active=True)
           addresses = Address.objects.filter(user=request.user,is_active=True)
           coupons = Coupon.objects.filter(is_active=True)
           
           coupons = [coupon for coupon in coupons if coupon.validate_usage_count(request.user)]
           
          
        else:
            addresses = []

        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity

            try:
                variant = cart_item.variations
                if variant.stock_count <= 0:
                    print("Not enough stock!")
            except ObjectDoesNotExist:
                pass

        tax = (2 * total) / 100
        

        grand_total = round(total + tax)
  

       

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'addresses':addresses,
        'tax': tax,
        'grand_total': grand_total,
        'coupons'  : coupons,
    }

    return render(request,'app1/checkout.html',context)


from django.http import JsonResponse
@login_required(login_url='userauths:sign-in')
def add_address(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        print(first_name, postal_code)

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            messages.success(request, 'Address added successfully.')
            
            return redirect('app1:user_address')

   
    return render(request, 'app1/add_address.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('app1:index')
    
    final_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.variations.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100

    
    coupon_discount = round(request.session.get('coupon_discount', 0))


    
    import math

    final_total = math.floor((total + tax) - coupon_discount)

    

    


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = current_user
            data.discount=coupon_discount
            data.order_total = final_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
            selected_address_id = request.session.get('selected_address_id')
            
            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                data.selected_address = selected_address
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                if selected_address_id is None:
                    messages.error(request,'choose an address or add address')  
                    return redirect('app1:checkout')
                else:
                    selected_address = Address.objects.get(pk=selected_address_id)
                    data.selected_address = selected_address

            data.save()
            
            from datetime import datetime
            yr = datetime.now().year
            dt = datetime.now().day
            mt = datetime.now().month
            d = datetime(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Remove the coupon_discount from the session
            if 'coupon_discount' in request.session:
                cp = request.session.get('coupon_code')
                ns = Coupon.objects.get(code=cp)

                reddemcoupon = RedeemedCoupon(
                    coupon=ns,
                    user=request.user,
                    redeemed_date=current_date,
                    is_redeemed=False,
                )  
                reddemcoupon.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            selected_address = order.selected_address
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'final_total' : final_total,
                'selected_address': selected_address,
                'coupon_discount':coupon_discount,
            }
            return render(request, 'app1/payment.html', context)
        else:
            return redirect('app1:checkout')
    else:
        
        return redirect('app1:index')

        
     

from datetime import date, timezone

def apply_coupon(request):
   
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        grand_total_str = request.POST.get('grand_total', '0')  
        grand_total = float(grand_total_str)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
            min=coupon.minimum_purchase_value
            max=coupon.maximum_purchase_value
            minimum=float(min)
            maximum=float(max)
           
             
           
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Coupon not found'})

        if not coupon.is_active:
            return JsonResponse({'status': 'error', 'message': 'Coupon is not active'})
        if grand_total < minimum or grand_total > maximum:
                print(f'grand_total: {grand_total}, minimum: {minimum}, maximum: {maximum}')  # Print values for debugging
                return JsonResponse({'status': 'error', 'message': 'Not in between price range'})
 

        if coupon.expiration_date < date.today():
            return JsonResponse({'status': 'error', 'message': 'Coupon has expired'})
        

       
        coupon_discount = (coupon.discount / 100) * grand_total
        final_total = grand_total - int(coupon_discount)

        # Store the coupon_discount in the session
        request.session['coupon_discount'] = int(coupon_discount)
        request.session['coupon_code'] = coupon_code

        response_data = {
            'status': 'success',
            'coupon_discount': coupon_discount,
            'final_total': final_total,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt
def remove_coupon(request):
    if 'coupon_discount' in request.session:
        # Remove coupon data from the session
        del request.session['coupon_discount']
        del request.session['coupon_code']
        grand_total = float(request.POST.get('grand_total', '0'))
        response_data = {
            'status': 'success',
            'coupon_discount': 0,
            'final_total':  grand_total, 
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'No coupon applied'})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderProduct, Payment, orderAddress
from django.http import HttpResponse

# ...

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderProduct, Payment, orderAddress, Coupon, RedeemedCoupon, CartItem

def paytment(request):
   if request.method == 'POST':
        print(request.POST)
        action = request.POST.get('action')
        selected_address_id = request.POST.get('selected_address')
        grand_total = request.POST.get('grand_total')
        
        order_number = request.POST.get('order_number')
          
        
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)
        except Order.DoesNotExist:
            
            return HttpResponse("Order not found")

        if action == "Cash on Delivery":
            print('action is done')
            payment = Payment.objects.create(
                user=request.user,
                payment_method="Cash on Delivery",  
                amount_paid=grand_total,  
                status="Pending",  
            )

            
            order.payment = payment
            order.save()
            




            new_address = orderAddress(
                user=request.user,  # Replace 'username' with the field you use to identify users
                address_type=order.selected_address.address_type, 
                first_name=order.selected_address.first_name,
                last_name=order.selected_address.last_name,
                email=order.selected_address.email,
                phone=order.selected_address.phone,
                address_line_1=order.selected_address.address_line_1,
                address_line_2=order.selected_address.address_line_2,
                city=order.selected_address.city,
                state=order.selected_address.state,
                postal_code=order.selected_address.postal_code,
                country=order.selected_address.country,
                is_active=True
            )

            # Save the new address to the database
            new_address.save()
      
            order.address = new_address
            order.save()
           


            
            

            cp=request.session.get('coupon_code')
            if cp is not None:
             ns=Coupon.objects.get(code=cp)
             reddemcoupon= RedeemedCoupon.objects.filter(user=request.user,coupon=ns,is_redeemed=False)
             reddemcoupon.is_redeemed=True
             reddemcoupon.update(is_redeemed=True)
             del request.session['coupon_code']
            
             
             

            
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
      
        
            for item in cart_items:
                orderproduct = OrderProduct()
                item.variations.stock_count-=item.quantity
                item.variations.save()
                orderproduct.order = order
                orderproduct.payment = payment
                orderproduct.user = request.user
                orderproduct.product = item.product
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.variations.price
                orderproduct.ordered = True
                orderproduct.color = item.variations.color
                orderproduct.save()


                    
            cart_items.delete()
            
            
            return redirect("app1:order_sucess", id=order.id) 
        else:
            return render(request, 'app1/payment.html')



        




##################################################################################################
@login_required(login_url='userauths:sign-in')
def profile(request):
    user = request.user
    
    wallet_amt = wallet.objects.filter(user=request.user)
    user_profile=Account.objects.get(email=request.user)
    if not wallet_amt.exists():
        
        new_wallet = wallet.objects.create(user=request.user)  
        print("Wallet created for user:", request.user)
    else:
       
        print("Wallet already exists for user:", request.user)
    context = {
        'user': user,
        'user_profile':user_profile,
        'wallet_amt':wallet_amt,
    }
    return render(request, 'app1/profile.html', context)


@login_required(login_url='userauths:sign-in')
def user_orders(request,):
    orders = Order.objects.filter(is_ordered=True, user=request.user).order_by('-created_at')
   
   
    context = {
        'orders': orders,
       

    }
    return render(request, 'app1/my_orders.html', context)







@login_required(login_url='userauths:sign-in')
def order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id,user=request.user)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request,'app1/order_detail.html',context)
     
     
import re
@login_required(login_url='userauths:sign-in')
def edit_profile(request):
    #user = request.user  # Get the currently logged-in user
    user = Account.objects.get(pk=request.user.pk)
    print("User ID:", user.id)
   
    context={
            'user':user
        }

        
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('user_name')


        username_pattern = "^[a-zA-Z0-9_]+$"
        name_pattern = "^[a-zA-Z]+$"

        if not username or not re.match(username_pattern, username):
            messages.error(request, 'Invalid or empty username. Use only letters, numbers, and underscores.')
        elif not first_name or not re.match(name_pattern, first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not last_name or not re.match(name_pattern, last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        else:
         user.first_name=first_name
         user.last_name=last_name
         user.username=username
         user.save()
         return redirect('app1:profile')
        
    return render(request, 'app1/edit_profile.html',context)
@login_required(login_url='userauths:sign-in')
def user_addres(request):
    addresses = Address.objects.filter(user=request.user,is_active=True)
    context = {
        'addresses': addresses
    }
    return render(request, 'app1/user_address.html', context)


from django.http import JsonResponse
def add_addresss(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            return JsonResponse({'error': 'Invalid or empty first name. Use only letters.'})
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            return JsonResponse({'error': 'Invalid or empty last name. Use only letters.'})
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return JsonResponse({'error': 'Invalid or empty email address.'})
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            return JsonResponse({'error': 'Invalid or empty phone number. It should be exactly 10 digits.'})
        elif not is_not_empty_or_whitespace(address_line_1):
            return JsonResponse({'error': 'Address line 1 cannot be empty.'})
        elif not is_not_empty_or_whitespace(city):
            return JsonResponse({'error': 'City cannot be empty.'})
        elif not is_not_empty_or_whitespace(state):
            return JsonResponse({'error': 'State cannot be empty.'})
        elif not is_valid_postal_code(postal_code):
            return JsonResponse({'error': 'Invalid postal code.'})
        elif not is_not_empty_or_whitespace(country):
            return JsonResponse({'error': 'Country cannot be empty.'})
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            return JsonResponse({'success': 'Address added successfully.','redirect_url': reverse('app1:checkout')}) 
            

    return JsonResponse({'error': 'Invalid request method.'})




@login_required(login_url='userauths:sign-in')
def edit_address(request,id):
    try:
        address = Address.objects.get(pk=id)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('user:user_address')

    if request.method == 'POST':
        # Handle the form submission to edit the address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Perform validation on the fields
        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            # All fields are valid, update the address
            address.first_name = first_name
            address.last_name = last_name
            address.email = email
            address.phone = phone
            address.address_line_1 = address_line_1
            address.address_line_2 = address_line_2
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country

            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('app1:user_address')

    context = {'address': address}
    return render(request, 'app1/edit_address.html', context)

@login_required(login_url='userauths:sign-in')
def delete_address(request, id):
    try:
        address = Address.objects.get(id=id)
        address.is_active = False  # Corrected field name
        address.save()
    except Address.DoesNotExist:
        pass
    return redirect('app1:user_address')


@login_required(login_url='userauths:sign-in')
def change_password(request):
    if request.method=='POST':
        old_password=request.POST.get('old_password')
        new_password1=request.POST.get('new_password1')
        new_password2=request.POST.get('new_password2')
        user=request.user
        password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not user.check_password(old_password):
            messages.error(request,'Old password is incorect')


            
        elif new_password1!=new_password2 :
           messages.error(request,'newpassword desnot match ')
        elif not new_password1 or not re.match(password_pattern,new_password1):
             messages.error(request, 'Invalid or weak password. It should have at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character.')
        else:
            user.set_password(new_password1)
            user.save()
            auth.update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('app1:profile')  
    return render(request,'app1/change_password.html')  
#####################################################

@login_required(login_url='userauths:sign-in')
def cancel_order_product(request, order_id):
    print(order_id)
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()


        user_profile = request.user
        wallets,create = wallet.objects.get_or_create(user=user_profile)
        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()
        transaction = WalletTransaction.objects.create(
                        user=request.user,
                        Wallet=wallets,
                        status="Credited",
                        amount=order.order_total,
                        created_at=datetime.now()  
                    )

                    # Save the transaction to the database
        transaction.save()


        
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            products = order_product.product.pid
            product=Product.objects.get(pid=products)
            

            
            product_variants = ProductVariant.objects.filter(product=product)
                        
            for variant in product_variants:
             variant.stock_count += order_product.quantity
             variant.save()
            
    return redirect('app1:user_dashboard') 

from django.http import Http404

def return_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    if order.payment and order.payment.payment_method == 'Cash on Delivery' and order.status == 'Completed':
        # Handle Cash on Delivery return
        order.status = 'Rejected'
        order.save()
        messages.warning(request, 'Return request has been sent.')

    elif order.payment and order.payment.payment_method != 'Cash on Delivery' and order.status == 'Completed':
        # Handle other payment methods return
        user_profile = request.user
        wallets, created = wallet.objects.get_or_create(user=user_profile)

        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()

        transaction = WalletTransaction.objects.create(
            user=request.user,
            Wallet=wallets,
            status="Credited",
            amount=order.order_total,
            created_at=datetime.now()
        )

        transaction.save()

        order.status = 'Rejected'
        order.save()

        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            products = order_product.product.pid
            product = Product.objects.get(pid=products)

            product_variants = ProductVariant.objects.filter(product=product)

            for variant in product_variants:
                variant.stock_count += order_product.quantity
                variant.save()

        messages.warning(request, 'Return request has been sent. Amount successfully returned to your wallet.')

    elif order.payment and order.payment.payment_method == 'Cash on Delivery' and order.status != 'Completed':
        # Handle Cash on Delivery return with incomplete order
        order.status = 'Cancelled'
        order.save()
        messages.warning(request, 'Return request has been sent.')

    else:
        
        raise Http404("Invalid order")

    return redirect('app1:user_dashboard')

            

#######################################################################################################################

from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Order, CartItem, OrderProduct, orderAddress, Payment, wallet, WalletTransaction, Coupon, RedeemedCoupon



def calculate_final_total(cart_items, grand_total):
    # Calculate total, tax, and final total
    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    coupon_discount = sum(item.variations.price * item.quantity for item in cart_items)
    final_total = (total + tax) - coupon_discount

    return total, tax, final_total




@login_required(login_url='userauths:sign-in')
def wallet_details(request):
    # if not request.user 
    try:
        wallet_instance = wallet.objects.get(user=request.user)
    except wallet.DoesNotExist:
        wallet_instance = wallet.objects.create(user=request.user, wallet_amount=0)

    wallet_amount = round(wallet_instance.wallet_amount, 2)
    user = request.user

    # Fetch transactions related to the wallet
    wallet_transactions = WalletTransaction.objects.filter(Wallet=wallet_instance)

    context = {
        'wallet_amount': wallet_amount,
        'user': user,
        'wallet_transactions': wallet_transactions,
    }

    return render(request, 'app1/wallet.html', context)












from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Order, CartItem, Address, wallet

def pay_wallet_details(request, order_number, order_total):
    order = Order.objects.filter(order_number=order_number, is_ordered=False).first()
    if not order:
        return HttpResponse("Order not found or already processed")

    grand_total = float(order_total)
    action = request.POST.get('action')

    if request.method == 'POST':
        # Handle wallet payment logic
        try:
            wallets = wallet.objects.get(user=request.user)
        except wallet.DoesNotExist:
            wallets = wallet.objects.create(user=request.user, wallet_amount=0)
            wallets.save()

        if wallets.wallet_amount <= grand_total:
            messages.error(request, 'Wallet balance is less than the total amount')
            return redirect('app1:checkout')

        cart_items = CartItem.objects.filter(user=request.user)
        selected_address_id = request.session.get('selected_address_id')

        if selected_address_id is not None:
            selected_address = Address.objects.get(pk=selected_address_id)
            del request.session['selected_address_id']
        else:
            selected_address_id = request.POST.get('selected_address')
            if selected_address_id is None:
                messages.error(request, 'Choose an address or add address')
                return redirect('app1:checkout')
            else:
                selected_address = Address.objects.get(pk=selected_address_id)
                coupon_discount = request.session.get('coupon_discount', 0)
                final_total = 0
                quantity = 0
                total = 0
                tax = 0
                for cart_item in cart_items:
                    total += (cart_item.product.price * cart_item.quantity)
                    quantity += cart_item.quantity
                tax = (2 * total) / 100

                
                order.is_ordered = True
                order.save()
                
                
                return redirect("app1:order_sucess", id=order.id)
                
    else:
        
        return HttpResponse("Invalid request method")
    
def abc():
   pass 
def dfs():
    pass   




def confirm_razorpay_payment(request, order_number):
    
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return HttpResponse("Order not found")
        
    
    total_amount = order.order_total 


    payment = Payment.objects.create(
        user=current_user,
        payment_method="Razorpay",
        status="Paid",
        amount_paid=total_amount,
    )
    print("razorpay")

    order.payment = payment
    order.save()
    new_address = orderAddress(
                user=request.user,  # Replace 'username' with the field you use to identify users
                address_type=order.selected_address.address_type, 
                first_name=order.selected_address.first_name,
                last_name=order.selected_address.last_name,
                email=order.selected_address.email,
                phone=order.selected_address.phone,
                address_line_1=order.selected_address.address_line_1,
                address_line_2=order.selected_address.address_line_2,
                city=order.selected_address.city,
                state=order.selected_address.state,
                postal_code=order.selected_address.postal_code,
                country=order.selected_address.country,
                is_active=True
            )

            
    new_address.save()
      
    order.address = new_address
    order.save()



    cp=request.session.get('coupon_code')
    if cp is not None:
     ns=Coupon.objects.get(code=cp)
     reddemcoupon= RedeemedCoupon.objects.filter(user=request.user,coupon=ns,is_redeemed=False)
     reddemcoupon.is_redeemed=True
     reddemcoupon.update(is_redeemed=True)
     del request.session['coupon_code']
             
             

            
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
      
    for item in cart_items:
                orderproduct = OrderProduct()
                item.variations.stock_count-=item.quantity
                item.variations.save()
                orderproduct.order = order
                orderproduct.payment = payment
                orderproduct.user = request.user
                orderproduct.product = item.product
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.variations.price
                orderproduct.ordered = True
                orderproduct.color = item.variations.color
                orderproduct.save()


                
    cart_items.delete()
           
    return redirect("app1:order_sucess", id=order.id)




def order_success(request, id):
    order = get_object_or_404(Order, id=id)
    order_products = OrderProduct.objects.filter(order=order)

    order.status = 'New'
    order.is_ordered = True
    order.save()

    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'app1/order_sucess.html', context)

@login_required(login_url='userauths:sign-in')
def add_wishList(request,pid):
    product = get_object_or_404(Product, pid=pid)
    

    try:
        vs = WishList.objects.get(user=request.user, product=product)
    except WishList.DoesNotExist:
        vs = None

    if vs is not None:
        messages.error(request, 'Product Already in wishlist')
    else:
        wishlist = WishList.objects.create(user=request.user, product=product)
        messages.success(request, 'Added Product to wishlist')
        
    return redirect('app1:index')

@login_required(login_url='userauths:sign-in')
def wishlist(request):
    wishlist=WishList.objects.filter(user=request.user)
    
    context={
        'wishlist':wishlist
    }
    return render(request,'app1/wishlist.html',context)


@login_required(login_url='userauths:sign-in')
def remove_from_wishlist(request, pid):
    print(pid)
    if request.method == 'POST' or request.method == 'DELETE':
        product = get_object_or_404(Product, pid=pid)
        wishlist_item = get_object_or_404(WishList, user=request.user, product=product)

       
        wishlist_item.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.utils import timezone


def search(request):
    q = request.GET.get('q', '')  

    try:
        discount_offer = ProductOffer.objects.get(active=True)
    except ProductOffer.DoesNotExist:
        discount_offer = None

    if discount_offer:
        current_date = timezone.now()
        if current_date > discount_offer.end_date or current_date < discount_offer.start_date:
            discount_offer.active = False
            discount_offer.save()

    try:
        discounted_offer = CategoryOffer.objects.filter(active=True)
    except CategoryOffer.DoesNotExist:
        discounted_offer = None

    if discounted_offer:
        for dis in discounted_offer:
            products_with_discount = Product.objects.filter(category=dis.category, in_stock=True)
            current_date = timezone.now()
            if current_date > dis.end_date or current_date < dis.start_date:
                dis.active = False
                dis.save()

    data = Product.objects.filter(title__icontains=q).order_by('-id')

    return render(request, 'app1/search.html', {'data': data, "discount_offer": discount_offer, "discounted_offer": discounted_offer})




         


def referral_coupon(request):
    
    if request.method == 'POST':
        
        code= request.POST.get("referral_code")
       
        try:
            
            ref_user_details = get_object_or_404(Account, code=code)
            
            print(f'ghjhgjhg{ref_user_details.email}')
            
                
           
        except Account.DoesNotExist:
            messages.warning(request, 'Invalid Referral code')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            
        except Exception as e:
            
           messages.warning(request, "Invalid Referral code")
           return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
           
        
        if ref_user_details.email ==request.user:
                messages.warning(request, 'Coupon cannot be used for same user')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
                
        
        if ref_user_details:
            wallet_instance, created = wallet.objects.get_or_create(user=request.user)
            
            wallet_instance.wallet_amount += 500
            wallet_instance.referral=True
            wallet_instance.save()
           
            messages.success(request,'$500 has been credited to your account')
            referral_user=wallet.objects.get(user=ref_user_details.id)
    
    
            referral_user.wallet_amount += 200
            referral_user.save()
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        


 
from django.shortcuts import get_object_or_404, render
from .models import Order, OrderProduct

def invoice(request, order_id):
    
    order = get_object_or_404(Order, id=order_id)
    
    
    order_products = OrderProduct.objects.filter(order=order)
    
    
    total_price = sum(item.quantity * item.product_price for item in order_products)
    
    context = {
        'order': order,
        'order_products': order_products,
        'total_price': total_price,
    }

    return render(request, 'app1/invoice.html', context)
