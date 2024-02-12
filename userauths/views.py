from django.shortcuts import render,redirect
from userauths.forms import UserRegistrationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from .models import *
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import random
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from app1.models import *
User=settings.AUTH_USER_MODEL

app_name = "userauths"


def register_view(request):
    if request.method=="POST":
        form=UserRegistrationForm(request.POST or None)
        
        if form.is_valid():
            
            
            username = form.cleaned_data.get("username")
            
            email = form.cleaned_data.get("email")
            password=form.cleaned_data.get('password1')
            request.session["username"] = username
            request.session["password"]=password
            request.session["email"]=email
            messages.success(request,f"Hey{username},your account created sucessfully")
            # new_user=authenticate(username=form.cleaned_data['email'],
            #                       password=form.cleaned_data['password1']
                                  
            #                       )
            email=request.POST["email"]
            send_otp(request)
            
            return render(request,'userauths/otp.html',{"email":email})
            
                 
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'userauths/sign-up.html', context)


def send_otp(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'groovehead17@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,"userauths/otp.html")


def otp_verification(request):
    if request.method == 'POST':
        otp_ = request.POST.get("otp")

        if otp_ == request.session["otp"]:
            encrypted_password = make_password(request.session['password'])
            nameuser = Account(username=request.session['username'], email=request.session['email'], password=encrypted_password)
            nameuser.is_active = True
            nameuser.save()

            
            login(request, nameuser, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, 'Account activation successful. You are now logged in.')
            
            return redirect('app1:index')  
        else:
            messages.error(request, "OTP doesn't match.")

    return render(request, 'userauths/otp.html')   
    


def login_view(request):
  
    if request.user.is_authenticated:
      messages.warning(request,f"Hey You are already logged in")
      return redirect("app1:index")
    if request.method == 'POST':
        email = request.POST.get('email')
        
        password = request.POST.get('password')
        request.session["email"]=email
        print(email,password)
        if not Account.objects.filter(email=email).exists():
            messages.error(request, "Invalid Email Adress")
            return redirect('userauths:sign-in')
        
        if not Account.objects.filter(email=email,is_active=True).exists():
            messages.error(request, "Account blocked ! ! !")
            return redirect('userauths:sign-in') 
        try:
           
            user = Account.objects.get(email=email)
           

            user_authenticated = authenticate(email=email, password=password,)

            if user_authenticated is not None:
                login(request, user_authenticated)
                messages.success(request, 'Login successful.')
                return redirect("app1:index")  
            else:
                messages.warning(request, 'Username or password is incorrect.')

        except Account.DoesNotExist:
            messages.warning(request, f'User with email {email} does not exist.')

        except Exception as e:
            messages.warning(request, f'An error occurred: {e}')  
          
        
    context = {}
    return render(request, 'userauths/sign-in.html', context)




def logout_view(request):
    logout(request)
    messages.success(request,"You logged out.")
    return redirect("app1:index")
    
def login_otp(request):
    
    if request.user.is_authenticated:
      messages.warning(request,f"Hey You are already logged in")
      return redirect("app1:index")
    if request.method == 'POST':
        email = request.POST.get('email')
        
        request.session["email"]=email
        
        if not Account.objects.filter(email=email).exists():
            messages.error(request, "Invalid Email Adress")
            return redirect('userauths:login_otp')
        
        if not Account.objects.filter(email=email,is_active=True).exists():
            messages.error(request, "Account blocked ! ! !")
            return redirect('userauths:login_otp') 
        try:
          user = Account.objects.get(email=email)
          if user is not None:
            send_otp_login(request)
            
            return render(request,'userauths/otp_login.html',{"email":email})
        #   
        except:
          messages.warning(request, f'User with {email} doesnot exists')

    return render(request,'userauths/login_otp.html')

def send_otp_login(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'groovehead17@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,"userauths/otp_login.html")


    


def otp_verification_login(request):
    if request.method == 'POST':
        otp_ = request.POST.get("otp")
        try:
            if "otp" in request.session and otp_ == request.session["otp"]:
                email = request.session.get("email")
                user = Account.objects.get(email=email)

                
                request.session.pop('otp', None)

                user.is_active = True
                user.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Account activated successfully.')
                redirect_url = reverse('app1:index')
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, "OTP doesn't match or session expired.")

        except ObjectDoesNotExist:
            messages.warning(request, f'User with email {email} does not exist.')
        except KeyError:
            messages.error(request, 'Session error. Please try again.')

    return render(request, 'userauths/otp_login.html')


