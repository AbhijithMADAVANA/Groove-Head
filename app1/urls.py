from django.contrib import admin
from django.urls import path
from app1 import views
from app1.views import index,product_list,category_list_view,category_product_list,confirm_razorpay_payment

app_name="app1"
urlpatterns = [
    path('',views.index,name='index'),
    path("products/",product_list,name='product-list'),
    path("category/",category_list_view,name='category-list'),
    path('category/<cid>/', views.category_product_list, name = 'category-product-list'),
    path('product/<pid>/', views.product_detail, name = 'product-detail'),
    

    path('shoping_cart/', views.cart, name='shopping_cart'),
    path('add_cart/<pid>/', views.add_cart, name='add_cart'),
    path('remove_cart/<pid>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<pid>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('ajax/update/cart/', views.newcart_update, name='newcart_update'),
    path('ajax/remove/cart/', views.remove_cart_item_fully, name='remove_cart_item_fully'),

    path('checkout',views.checkout,name="checkout"),
    path('add_adresss/',views.add_addresss,name='add_addresss'),
    path('place_order',views.place_order,name="place_order"),
    path('payment',views.paytment,name="payment"),

    path('confirm_razorpay_payment/<int:order_number>/', views.confirm_razorpay_payment, name='confirm_razorpay_payment'),

    path('order_success/<int:id>/', views.order_success, name='order_sucess'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),

    path('cancel_order_product/<order_id>/',views.cancel_order_product,name='cancel_order_product'),
   

    path('user_dashboard/',views.user_orders, name='user_dashboard'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('profile/',views.profile,name='profile'),
    path('user_address/',views.user_addres,name='user_address'),
    path('add_address/',views.add_address,name='add_address'),
    path('add_adresss/',views.add_addresss,name='add_addresss'),
    path('edit_address/<int:id>/',views.edit_address,name='edit_address'),
    path('delete_address/<int:id>/',views.delete_address,name='delete_address'),
    path('cancel_order_product/<int:order_id>/',views.cancel_order_product,name='cancel_order_product'),
    path('change_password',views.change_password,name='change_password'),




    path('apply_coupon',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon/',views.remove_coupon, name='remove_coupon'),

     

    path('wallet',views.wallet_details,name="wallet"),
    path('pay_wallet_details/<str:order_number>/<str:order_total>/', views.pay_wallet_details, name="pay_wallet_details"),


    


    
]
