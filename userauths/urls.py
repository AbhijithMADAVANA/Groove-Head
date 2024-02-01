from django.urls import path
from . import views

app_name = "userauths"

urlpatterns = [
    path("sign-up/",views.register_view, name="sign-up"),
    path("sign-in/",views.login_view, name="sign-in"),
    path("sign-out/",views.logout_view, name="sign-out"),
    path('sign-up/otp_verification',views.otp_verification,name="otp_verification"),
    path('login_otp/',views.login_otp,name ='login_otp'),
    path('login/otp_verification_login',views.otp_verification_login,name="otp_verification_login"),

    

]