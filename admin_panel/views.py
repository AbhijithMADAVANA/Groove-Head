from collections import defaultdict
import datetime
from decimal import Decimal
from io import BytesIO
import os
from django.utils.timezone import make_aware
from typing import DefaultDict
from django.shortcuts import render,redirect,get_object_or_404
from app1.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from admin_panel.forms import ColorForm, CouponForm, CreateProductForm, ProductVariantForm
from django.http import HttpResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from admin_auth import views
from django.db.models import Count, Sum
from datetime import datetime, timezone
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from app1.forms import ProductOfferForm,CategoryOfferForm
from django.http import JsonResponse
from django.http import HttpResponse
from app1.models import *
# Create your views here.









from django.contrib.auth.decorators import login_required

@login_required(login_url='admin_auth:admin_login')
def dashboard(request):
    if not request.user.is_superadmin:
        return redirect("admin_auth:admin_login")

    total_users_count = int(Account.objects.count())
    product_count = Product.objects.count()
    orders = Order.objects.all()
    total_users_count = int(Account.objects.count())
    product_count = Product.objects.count()
    user_order = Order.objects.filter(is_ordered=True).count()
    # # for i in monthly_order_totals:
    completed_orders = Order.objects.filter(is_ordered=True)

    monthly_totals_dict = DefaultDict(float)
    total_revenue = 0
    for order in orders:
        if order.status == 'Completed':  
        
            order_total = order.order_total 
            total_revenue += order_total

    revenue = int(total_revenue)


    # Iterate over completed orders and calculate monthly totals
    for order in completed_orders:
        order_month = order.created_at.strftime('%m-%Y')
        monthly_totals_dict[order_month] += float(order.order_total)

    print(monthly_totals_dict)
    months = list(monthly_totals_dict.keys())
    totals = list(monthly_totals_dict.values())

    variants = ProductVariant.objects.all()
    last_orders = Order.objects.order_by('-id')[:5]
    
    context = {
        'total_users_count': total_users_count,
        'product_count': product_count,
        'order': user_order,
        'variants': variants,
        'months': months,
        'totals': totals,
        'last_orders':last_orders,
        'user_order':user_order,
        'revenue':revenue,


    }
    return render(request, 'admin_panel/dashboard.html', context)

def admin_products_list(request):
  if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
  products = Product.objects.all()
  p=Paginator(Product.objects.all(),10)
  page=request.GET.get('page')
  productss=p.get_page(page)
  
  context ={
    "products":products ,
    "productss":productss
  }
  return render(request, 'admin_panel/admin_products_list.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_products_details(request, pid):
    
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')

    try:
        product = Product.objects.get(pid=pid)
        product_images = ProductImages.objects.filter(product=product)
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Save the form including the image
            product = form.save(commit=False)
            product_image = form.cleaned_data['new_image']
            if product_image is not None:
                product.image = product_image
            product.save()

            # Update or create additional images
            for i in product_images:
                image_field_name = f'product_image{i.id}'
                image = request.FILES.get(image_field_name)

                if image:
                    i.Images = image
                    i.save()

            return redirect('admin_panel:admin_products_list')
        else:
            print(form.errors)
            context = {
                'form': form,
                'product': product,
                'product_images': product_images,
            }
            return render(request, 'admin_panel/admin_products_details.html', context)
    else:
        initial_data = {'new_image': product.image.url if product.image else ''}
        form = CreateProductForm(instance=product, initial=initial_data)

    context = {
        'form': form,
        'product': product,
        'product_images': product_images,
    }
    return render(request, 'admin_panel/admin_products_details.html', context)



def block_unblock_products(request, pid):
  if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
  product = get_object_or_404(Product, pid=pid)
  if product.status:
    product.status=False
  else:
      product.status=True
  product.save()
  return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    categories = Category.objects.all()

    if request.method == 'POST':
        product_name = request.POST.get('title')
        product_stock_count = request.POST.get('stock_count')
        description = request.POST.get('description')
        max_price = request.POST.get('old_price')
        sale_price = request.POST.get('price')
        category_name = request.POST.get('category')
        # validations
        validation_errors = []

        try:
            max_price = float(max_price)
            if max_price < 0:
                validation_errors.append("Max Price must be a non-negative number.")

            sale_price = float(sale_price)
            if sale_price < 0:
                validation_errors.append("Sale Price must be a non-negative number.")
        except ValueError as e:
            validation_errors.append(str(e))

        if validation_errors:
            form = CreateProductForm()
            content = {
                'categories': categories,
                'form': form,
                'additional_image_count': range(1, 4),
                'error_messages': validation_errors,
            }
            return render(request, 'admin_panel/admin_add_product.html', content)
        
        category = get_object_or_404(Category, title=category_name)

        product = Product(
            title=product_name,
            stock_count=product_stock_count,
            category=category,
            description=description,
            old_price=max_price,
            price=sale_price,
            image=request.FILES['image_feild']
        )
        product.save()

        # Handling additional images
        additional_image_count = 5  
        for i in range(1, additional_image_count + 1):
            image_field_name = f'product_image{i}'
            image = request.FILES.get(image_field_name)
            if image:
                ProductImages.objects.create(product=product, images=image)  

        return redirect('admin_panel:admin_products_list')
    else:
        form = CreateProductForm()

    content = {
        'categories': categories,
        'form': form,
        'additional_image_count': range(1, 4), 
    }
    return render(request, 'admin_panel/admin_add_product.html', content)



#ends here

def delete_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    try:
        product = Product.objects.get(pid=pid)
        product.delete()
        return redirect('admin_panel:admin_products_list')
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)
    
#########################################################################
    
def admin_category_list(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    categories = Category.objects.all()
    
    context = {
        'categories':categories
    }
    
    return render(request,'admin_panel/admin_category_list.html',context)


def admin_add_category(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    if request.method == 'POST':
        cat_title = request.POST.get('category_name')
        if Category.objects.filter(title=cat_title).exists():
            messages.error(request, 'Category with this title already exists.')
        else:
            cat_data = Category(title=cat_title, image=request.FILES.get('category_image'))
            cat_data.save()
            messages.success(request, 'Category added successfully.')
            return redirect('admin_panel:admin_add_category')  
        
    return render(request, 'admin_panel/admin_add_category.html')

def admin_category_edit(request, cid):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

   
    categories = get_object_or_404(Category, cid=cid)

    if request.method == 'POST':
        # Update the fields of the existing category object
        cat_title = request.POST.get("category_name")
        cat_image = request.FILES.get('category_image')

        # Update the category object with the new title and image
        categories.title = cat_title
        if cat_image is not None:
            categories.image = cat_image

        
        # Save the changes to the database
        categories.save()

        
        return redirect('admin_panel:admin_category_list')

    
    context = {
        "categories_title": categories.title,
        "categories_image": categories.image,
    }

    return render(request, 'admin_panel/admin_category_edit.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_category(request,cid):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    try:
        category=Category.objects.get(cid=cid)
    except ValueError:
        return redirect('admin_panel:admin_category_list')
    category.delete()

    return redirect('admin_panel:admin_category_list')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def available_category(request,cid):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    category = get_object_or_404(Category, cid=cid)
    
    if category.is_blocked:
        category.is_blocked=False
       
    else:
        category.is_blocked=True
    category.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def color(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    prod = Color.objects.all()
    context = {
      'prod': prod
    }
    return render(request,"admin_panel/color-info.html",context)

def del_color(request,id):
    if request.method == "POST":
        prod = Color.objects.get(pk=id)
        prod.delete()
        return redirect('admin_panel:color')
    
def edit_color(request,id):
    product = get_object_or_404(Color,pk=id)
    if request.method == "POST":
        color_form = ColorForm(request.POST,request.FILES,instance=product)
        if color_form.is_valid():
            color_form.save()
            return redirect('admin_panel:color')
    else:
        color_form = ColorForm(instance=product)
    context = {
        'color_form':color_form
    }
    return render(request,"admin_panel/edit-color.html",context)
    
def add_color(request):
    if request.method == "POST":
        color_form = ColorForm(request.POST,request.FILES)
        if color_form.is_valid():
            color_form.save()
            return redirect("admin_panel:color")
    else:
        color_form = ColorForm()
    context = {'color_form': color_form}
    return render(request, 'admin_panel/add-color.html', context)


#################################################################

def variant_list(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    product_variations = ProductVariant.objects.all()
    form = ProductVariantForm()
    context = {
        'product_variant': product_variations,
        'form':form
        }
    return render(request, 'admin_panel/listvariants.html', context)


def add_variant(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    additional_image_count = 3  

    if request.method == 'POST':
        variant_form = ProductVariantForm(request.POST, request.FILES)
        if variant_form.is_valid():
            variant_instance = variant_form.save(commit=False)
            variant_instance.save()

            # Handling additional images
            for i in range(1, additional_image_count + 1):
                image_field_name = f'additional_image_{i}'
                image = request.FILES.get(image_field_name)
                if image:
                    VariantImages.objects.create(productvariant=variant_instance, images=image)

            return redirect('admin_panel:variant-list') 
    else:
        variant_form = ProductVariantForm()

    context = {
        'variant_form': variant_form,
        'additional_image_count': range(1, additional_image_count + 1),
    }

    return render(request, 'admin_panel/addvariants.html', context)





def edit_variant(request, id):
    product = get_object_or_404(ProductVariant, pk=id)
    if request.method == "POST":
        variant_form = ProductVariantForm(request.POST, request.FILES, instance=product)
        if variant_form.is_valid():
            variant_form.save()
            return redirect('admin_panel:variant-list')
    else:
        variant_form = ProductVariantForm(instance=product)

    context = {
        "variant_form": variant_form
    }
    return render(request, 'admin_panel/edit_variants.html', context)

def delete_variant(request, id):
    if request.method == "POST":
        prod = ProductVariant.objects.get(id=id)
        prod.delete()
        return redirect('admin_panel:variant-list')
    
##############################################################
    
@login_required(login_url='admin_auth:admin_login')
def order_list(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')  
    context = {'orders': orders}
    return render(request, 'admin_panel/orderlist.html', context)

@login_required(login_url='admin_auth:admin_login')
def ordered_product_details(request, order_id):
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    orders = Order.objects.get(id=order_id)
    
    order_instance = Order.objects.get(id=order_id)

# Retrieving related OrderProduct instances using the default reverse relation
    ordered_products = order_instance.orderproduct_set.all()


    print(ordered_products)
    for i in ordered_products:
        total=+(i.product_price*i.quantity)
    payments = Payment.objects.filter(order__id=order_id,user=orders.user)    

    context = {
        'total':total,
        'order': orders,
        'ordered_products': ordered_products,
        'payments':payments
    }
    return render(request, 'admin_panel/ordered_product_details.html', context)

from django.http import HttpResponseNotFound

@login_required(login_url='admin_auth:admin_login')
def update_order_status(request, order_id):
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=int(order_id))
        status = request.POST.get('status', 'New')
        order.status = status
        order.save()

        if status == 'Completed':
            try:
                payment = Payment.objects.get(order__id=order_id, user=order.user)
                if payment.payment_method == 'Cash on Delivery':
                    payment.status = 'Paid'
                    payment.save()
            except Payment.DoesNotExist:
                return HttpResponseNotFound("Payment does not exist for this order.")

        return redirect('admin_panel:order_list')
    else:
        return HttpResponseBadRequest("Bad request.")




def add_coupon(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:list_coupons') 
    form = CouponForm()
    
    return render(request, 'admin_panel/add coupons.html', {'form': form})


# from cart.models import *
def list_coupons(request):
    coupons=Coupon.objects.filter(is_active=True)
    return render(request,'admin_panel/list_coupon.html',{"coupons":coupons})

@login_required(login_url='admin_auth:admin_login')
def delete_coupon(request, id):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    try:
        coupon = Coupon.objects.get(id=id)
        coupon.is_active=False
        coupon.save()
    except Coupon.DoesNotExist:
        
        pass

    return redirect('admin_panel:list_coupons')


@login_required(login_url='admin_auth:admin_login')
def edit_coupon(request, id):
    coupon = get_object_or_404(Coupon, pk=id)
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    if request.method == 'POST':
        form = CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:list_coupons')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin_panel/edit_coupon.html', {'form': form})

##################################################################################

def product_offers(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    offers=ProductOffer.objects.all()
    try:
        product_offer = ProductOffer.objects.get(active=True)
        
    except ProductOffer.DoesNotExist:
       
        product_offer = None
    
    products = Product.objects.all()

    for p in products:
       
        if product_offer:
           
            discounted_price = p.old_price - (p.old_price * product_offer.discount_percentage / 100)
            p.price = max(discounted_price, Decimal('0.00'))  
        else:
            
            p.price = p.old_price

        p.save()

        # productoffer for product detail page
    vr1=   ProductVariant.objects.all()
    for v1 in vr1:
        if product_offer:
            discounted_price = v1.old_price - (v1.old_price * product_offer.discount_percentage / 100)
            v1.price = max(discounted_price, Decimal('0.00')) 
        else:
            
            v1.price = v1.old_price    

        v1.save()
        # till here
    context={
        'offers':offers
    }
    return render(request, 'admin_panel/product_offers.html',context)


def edit_product_offers(request, id):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    offer_discount = get_object_or_404(ProductOffer, id=id)
    print(f'Active Date: {offer_discount.start_date}')

    if request.method == 'POST':
        discount = request.POST['discount']
        active = request.POST.get('active') == 'on'
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        
        if end_date and start_date and end_date < start_date:
            messages.error(request, 'Expiry date must not be less than the start date.')
        else:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            current_date = timezone.now()
            if start_date and end_date and (current_date < start_date or current_date > end_date):
                active = False
                messages.error(request, 'Offer cannot be activated now. Check the start date.')
           
            active_category_offer = CategoryOffer.objects.filter(active=True).first()

            if active_category_offer:
               
                messages.error(request, 'Cannot create/update product offer when a category offer is active.')
                return redirect('admin_panel:product-offers')

           
            if active:
                ProductOffer.objects.exclude(id=offer_discount.id).update(active=False)

            offer_discount.discount_percentage = discount or None
            offer_discount.start_date = start_date or None
            offer_discount.end_date = end_date or None
            offer_discount.active = active
            offer_discount.save()

            messages.success(request, 'Offer Updated successfully')
            return redirect('admin_panel:product-offers')
    
    return render(request, 'admin_panel/edit_product_offers.html', {'offer_discount': offer_discount})

from datetime import datetime
from django.utils import timezone

def create_product_offer(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            discount_percentage = form.cleaned_data['discount_percentage']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            active = form.cleaned_data['active']
            
            if end_date and start_date and end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
            else:
                current_date = timezone.localtime(timezone.now())
                if start_date and end_date and (current_date < start_date or current_date > end_date):
                    active = False
                    messages.error(request, 'Offer cannot be activated now. Check the start date.')

                if active:
                    ProductOffer.objects.update(active=False)

                if discount_percentage or start_date or end_date or active:
                    form.save()
            
            return redirect('admin_panel:product-offers')  
    else:
        form = ProductOfferForm()

    return render(request, 'admin_panel/create-product-offers.html', {'form': form})


@login_required(login_url='admin_auth:admin_login')        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_product_offer(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    try:
        offer= get_object_or_404(ProductOffer, id=id)
    except ValueError:
        return redirect('admin_panel:product-offers')
    offer.delete()
    messages.warning(request,"Offer has been deleted successfully")

    return redirect('admin_panel:product-offers')


def category_offers(request):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    offers = CategoryOffer.objects.all()
    categories = Category.objects.all()

    for category in categories:
        try:
            category_offers = CategoryOffer.objects.filter(category=category, active=True)
            
        except CategoryOffer.DoesNotExist:
            category_offers = None

        products = Product.objects.filter(category=category, status=True)
        vr1 = ProductVariant.objects.filter(product__category=category)

        

        for product in products:
            for category_offer in category_offers:
                discounted_price = product.old_price - (product.old_price * category_offer.discount_percentage / 100)
                product.price = max(discounted_price, Decimal('0.00'))
                product.save()

        for v1 in vr1:
            for category_offer in category_offers:
                discounted_price = v1.old_price - (v1.old_price * category_offer.discount_percentage / 100)
                v1.price = max(discounted_price, Decimal('0.00'))
                v1.save()

    context = {
        'offers': offers
    }
    return render(request, 'admin_panel/category_offers.html', context)




def edit_category_offers(request, id):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')

    offer_discount = get_object_or_404(CategoryOffer, id=id)
    print(f'Active Date: {offer_discount.start_date}')

    if request.method == 'POST':
        discount = request.POST.get('discount')
        active = request.POST.get('active') == 'on'
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if end_date and start_date:
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))

            if end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
                return redirect('admin_panel:edit-category-offers', id=id)

            
            current_date = timezone.now()
            if start_date and end_date and (current_date < start_date or current_date > end_date):
                active = False
                messages.error(request, 'Offer cannot be activated now. Check the start date.')
            
       

        
        active_product_offer = ProductOffer.objects.filter(active=True).first()

        if active_product_offer:
            
            messages.error(request, 'Cannot activate category offer when a product offer is active.')
            return redirect('admin_panel:category-offers')
        
        if active:
            CategoryOffer.objects.exclude(id=offer_discount.id).update(active=False)

        
        offer_discount.discount_percentage = discount or None
        offer_discount.start_date = start_date or None
        offer_discount.end_date = end_date or None
        offer_discount.active = active
        offer_discount.save()

        messages.success(request, 'Offer updated successfully')
        return redirect('admin_panel:category-offers')

    return render(request, 'admin_panel/edit_category_offers.html', {'offer_discount': offer_discount})


def create_category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            discount_percentage = form.cleaned_data['discount_percentage']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            active = form.cleaned_data['active']

            if end_date and start_date and end_date < start_date:
                messages.error(request, 'Expiry date must not be less than the start date.')
            else:
               
                if active and CategoryOffer.objects.filter(category=category, active=True).exists():
                    messages.error(request, 'An active offer already exists for this category.')
                   
                else:
                    current_date = timezone.now()
                    if start_date and end_date and (current_date < start_date or current_date > end_date):
                        active = False
                        messages.error(request, 'Offer cannot be activated now. Check on start date')
                    
                    if active:
                        CategoryOffer.objects.update(active=False)
                    if discount_percentage or start_date or end_date or active:
                        form.save()

                    return redirect('admin_panel:category-offers')  
    else:
        form = CategoryOfferForm()

    return render(request, 'admin_panel/create_category_offer.html', {'form': form})



@login_required(login_url='admin_auth:admin_login')        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_category_offer(request,id):
    if not request.user.is_superadmin:
        return redirect('admin_auth:admin_login')
    
    try:
        offer= get_object_or_404(CategoryOffer, id=id)
    except ValueError:
        return redirect('admin_panel:category-offers')
    offer.delete()
    messages.warning(request,"Offer has been deleted successfully")

    return redirect('admin_panel:category-offers')


from django.urls import path, reverse_lazy
from django.views.generic import View
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Banner
from .forms import BannerForm
from django.urls import reverse  


class AdminBannerView(View):
    template_name = 'admin_panel/admin_banner.html'

    def get(self, request):
        banners = Banner.objects.all()
        for banner in banners:
            banner.is_active = banner.update_status()
            banner.save()
        return render(request, self.template_name, {'banners': banners})

@method_decorator(login_required(login_url='admin_login'), name='dispatch')
class CreateBannerView(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'admin_panel/banner_create.html'
    success_url = reverse_lazy('admin_panel:admin_banner')

@method_decorator(login_required(login_url='admin_login'), name='dispatch')
class UpdateBannerView(UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'admin_panel/banner_update.html'
    success_url = reverse_lazy('admin_panel:admin_banner')


@method_decorator(login_required(login_url='admin_login'), name='dispatch')
class DeleteBannerView(View):
    def get(self, request, banner_id):
        try:
            banner = Banner.objects.get(id=banner_id)
            banner.delete()
            # Redirect back to some URL after successful deletion
            return HttpResponseRedirect(reverse('admin_panel:admin_banner'))  # Redirect to admin_banner page
        except Banner.DoesNotExist:
            # Handle case where banner with given ID does not exist
            return HttpResponseRedirect(reverse('admin_panel:admin_banner'))  # Redirect to admin_banner page


   
   

