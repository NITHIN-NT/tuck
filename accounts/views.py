from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.template.loader import render_to_string # Add this import                                                                 │
from django.core.mail import EmailMultiAlternatives 
from django.views import View
from .models import CustomUser,EmailOTP
from .forms import CustomUserRegisterForm, LoginForm,VerifyOTPForm,SetNewPassword,ForgotPasswordEmailForm


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

            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(user=user,otp=otp_code)
# Render the HTML email content                                                                                           

            plain_message = f"Your OTP code is {otp_code}"                                                                            
            html_message = render_to_string('accounts/email/otp_email.html', {'otp_code': otp_code})                                  
                                                                                                                                      
            # Send the email                                                                                                          
            try:
                msg = EmailMultiAlternatives(                                                                                             
                    body=plain_message,                                                                                                   
                    subject='Your OTP Verification Code',                                                                               
                    from_email="TuckInda@gmail.com", # Use your DEFAULT_FROM_EMAIL or a specific one                                 
                    to=[email],                                                                                                           
                )                                                                                                                         
                msg.attach_alternative(html_message, "text/html")                                                                         
                msg.send()         
            except Exception as e :
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return redirect('signup')                                                                                                 
                                        

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
            messages.error(request,'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/verify_otp.html', {'email': user.email})                   
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

class SendOTPView(View):

    def get(self,request):
        form = ForgotPasswordEmailForm()
        return render(request,'accounts/forgot-password.html',{'form':form})
    
    def post(self,request):
        form = ForgotPasswordEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                messages.error(request,'No user found with this email')
                return render(request,'accounts/signup.html')
            
            otp = EmailOTP.generate_otp()
            EmailOTP.objects.create(user=user,otp=otp)

            plain_message = f'Your OTP code for password reset is: {otp}'
            html_message = render_to_string('accounts/email/otp_email_reset.html', {'otp_code': otp}) 

            try:
                msg = EmailMultiAlternatives(
                    body=plain_message,
                    subject='Your OTP Verification Code',
                    from_email ='TuckInda@gmail.com',
                    to=[email],
                )
                msg.attach_alternative(html_message,"text/html")
                msg.send()
            except Exception as e :
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return redirect('signup')

            request.session['reset_user_email'] = user.email

            messages.success(request,f'An otp has been sent to {email}.')
            return redirect('forgot-verify-otp')
        else:
            return render(request,'accounts/forgot-password.html',{'form': form})


class VerifyOTPView(View):
    def get(self,request):
        if 'reset_user_email' not in request.session:
            messages.error(request,'Please Request an OTP First.')
            return redirect('forgot-password')
        
        form = VerifyOTPForm()
        return render(request,'accounts/verify-otp-password_reset.html',{'form':form})
    
    def post(self,request):
        email = request.session.get('reset_user_email')
        if not email:
            messages.error(request,'Your Session has expired.Please start over')
            return redirect('forgot-password')
        
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_from_form = form.cleaned_data['otp']
            user = get_object_or_404(CustomUser,email=email)

            try:
                email_otp = EmailOTP.objects.filter(user=user).latest('created_at')
            except EmailOTP.DoesNotExist:
                messages.error(request,"No OTP found,Please request New One")
                return render(request,'accounts/verify-otp-password_reset.html',{'form':form})
            

            if email_otp.otp == otp_from_form and email_otp.is_valid():
                email_otp.delete()
                request.session['reset_password_allowed'] = True
                messages.success(request,'OTP verified successfully. Please set your new password')
                return redirect('set-new-password')
            elif not email_otp.is_valid():
                messages.error(request,'Your OTP has expired. Please request a new one.')
            else:
                messages.error(request,'Invalid or expired OTP. Please try again.')

        return render(request,'accounts/verify-otp-password_reset.html',{'form':form})

class NewPasswordView(View):
    def get(self,request):
        if not request.session.get('reset_user_email') or not request.session.get('reset_password_allowed'):
            messages.error(request, 'You are not authorized to access this page. Please verify your OTP first.')
            return redirect('forgot-password')
        
        form = SetNewPassword()
        return render(request,'accounts/new-password.html',{'form':form})
    
    def post(self,request):
        email = request.session.get('reset_user_email')

        if not email or not request.session.get('reset_password_allowed'):
            messages.error(request,'Your session has expired. Please start over.')
            return redirect('forgot-password')
        
        form = SetNewPassword(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user = get_object_or_404(CustomUser,email=email)

            user.set_password(new_password)
            user.save()
            request.session.flush()
            messages.success(request,'Your password has been reset successfully. Please log in.')
            try:
                del request.session['reset_user_email']
                del request.session['reset_password_allowed']
            except KeyError:
                pass
            return redirect('login')
        
        return render(request,'accounts/new-password.html',{'form':form})
                

