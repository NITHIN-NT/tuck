from django.shortcuts import render,redirect
from .models import CustomUser,EmailOTP
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
# Create your views here.
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
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('Home_page_user')
            else:
                messages.error(request, "Please verify your email first.")
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('Home_page_user')