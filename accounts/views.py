from django.shortcuts import render,redirect
from .models import CustomUser,EmailOTP
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import CustomUserRegisterForm, LoginForm
from django.template.loader import render_to_string # Add this import                                                                 │
from django.core.mail import send_mail, EmailMultiAlternatives 
# Create your views here.
'''login Function Based View
def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if CustomUser.objects.filter(email=email).exists():
            messages.success(request,'Email Already Exists')
            return redirect('signup')
        
        user = CustomUser.objects.create_user(email=email,password=password,first_name=first_name,last_name=last_name)
        user.is_active = False
        user.save()

        otp_code = EmailOTP.genrate_otp()
        EmailOTP.objects.create(user=user,otp=otp_code)

        send_mail(
            subject="Your OTP Verification Code",
            message=f"Your OTP code is {otp_code}",
            from_email="no-reply@example.com",
            recipient_list=[email],
        )

        request.session['pending_user_id'] = user.id
        messages.info(request, "OTP sent to your email. Verify to continue.")
        return redirect('verify_otp')
    return render(request, 'accounts/signup.html')
'''

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            user = CustomUser.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password      
            )
            user.is_active = False
            user.save()

            otp_code = EmailOTP.genrate_otp()
            EmailOTP.objects.create(user=user,otp=otp_code)
# Render the HTML email content                                                                                           

            plain_message = f"Your OTP code is {otp_code}"                                                                            
            html_message = render_to_string('accounts/email/otp_email.html', {'otp_code': otp_code})                                  
                                                                                                                                      
            # Send the email                                                                                                          
            msg = EmailMultiAlternatives(                                                                                             
                body=plain_message,                                                                                                   
                subject="Your OTP Verification Code",                                                                                 
                from_email="secondstrap@example.com", # Use your DEFAULT_FROM_EMAIL or a specific one                                 
                to=[email],                                                                                                           
            )                                                                                                                         
            msg.attach_alternative(html_message, "text/html")                                                                         
            msg.send()                                                                                                                
                                        

            request.session['pending_user_id'] = user.id
            messages.info(request, "OTP sent to your email. Verify to continue.")
            return redirect('verify_otp')
        else:
            return render(request,'accounts/signup.html',{'form': form})
    else:
        form = CustomUserRegisterForm()
    return render(request, 'accounts/signup.html',{'form': form})
       


def verify_otp_view(request):
    user_id = request.session.get('pending_user_id')

    if not user_id:
        messages.error(request,'No pending Verification Found')
        return redirect('signup')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request,"User Not Found")
        return redirect('signup')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp','').strip()

        otp_record = EmailOTP.objects.filter(user=user,otp=otp_input).last()

        if otp_record and otp_record.is_valid():
            user.is_active = True
            user.save()
            otp_record.delete()

            # Remove session key
            del request.session['pending_user_id']

            # Auto-login user
            login(request, user)
            messages.success(request, "Your email has been verified successfully!")
            return redirect('Home_page_user')
        else :
            messages.error(request,'Invalid or ')
    else:
        messages.error(request, "OTP expired. Please resend a new one.")
        return render(request, 'accounts/verify_otp.html', {'email': user.email})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                    return redirect('Home_page_user')
                else:
                    messages.error(request, "Please verify your email first.")
            else:
                messages.error(request, "Invalid credentials. Please check your email and password.")
        else:
            # If form is invalid, iterate through errors and add to messages for toast display
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"{error}")
                    else:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            # Re-render the login page with the form and its errors
            return render(request, 'accounts/login.html', {'form': form})
    else: # GET request
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('Home_page_user')