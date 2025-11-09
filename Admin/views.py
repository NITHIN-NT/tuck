from .decorators import superuser_required
from django.template.loader import render_to_string 
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import CustomUser,EmailOTP
from django.db import transaction
from django.core.mail import EmailMultiAlternatives 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView
from django.views import View
from django.db.models import Count,Sum
from .forms import (AdminLoginForm,AdminForgotPasswordEmailForm,
                    AdminSetNewPassword,AdminVerifyOTPForm,
                    AdminProductAddForm,VariantFormSet,ImageFormSet)
from products.models import Product,Category,ProductVariant
from django.urls import reverse_lazy

# Create your views here.
@never_cache
def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email,password=password)
            if user is not None and user.is_superuser :
                login(request, user)
                return redirect('admin_home')
            else:
                messages.error(request, "Invalid email or password, or you don't have admin access.")
                return redirect('admin_login')
    else:
        form = AdminLoginForm()
    return render(request,'adminAuth/login.html',{'form' : form})

def admin_forgot (request):
    form = AdminForgotPasswordEmailForm()
    if request.method == 'POST':
        form = AdminForgotPasswordEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                messages.error(request,'No User Found With this email')
                return redirect('admin_login')

            if not user.is_superuser:
                messages.error(request, 'Access denied. Only admins can reset password here.')
                return redirect('admin_login')


            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(user=user,otp=otp_code)

            subject = 'Admin Reset Password One-Time-Password '
            plain_message = f"Your OTP code for password Rest is :{otp_code}"
            html_message = render_to_string('email/admin_otp_email.html', {'otp_code': otp_code}) 

            try:
                msg = EmailMultiAlternatives(
                    body=plain_message,
                    subject=subject,
                    from_email ='TuckInda@gmail.com',
                    to=[email],
                )
                msg.attach_alternative(html_message,"text/html")
                msg.send()
                request.session['reset_admin_email'] = user.email
                messages.success(request,f'An OTP has been Sent to {email}')
                return redirect('admin_otp_verification')
            
            except Exception as e :
                print("Email sending failed:", e)
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return redirect('admin_forgot_password')
    return render(request,'adminAuth/forgot-password.html',{'form':form})

def admin_otp_verification (request):
    if not request.session.get('reset_admin_email'):
        messages.error(request,'You are Not autherized to access this page.')
        return redirect('admin_login')
    email = request.session.get('reset_admin_email')
    if not email :
        messages.error(request,'Your Session has expired. Please Start Over')
        return redirect('admin_forgot_password')
    if request.method =='POST':
        form = AdminVerifyOTPForm(request.POST)
        if form.is_valid():
            otp_from_form = form.cleaned_data['otp']
            user = get_object_or_404(CustomUser,email=email)

            try:
                email_otp = EmailOTP.objects.filter(user=user).latest('created_at')
            except EmailOTP.DoesNotExist:
                messages.error(request,'No OTP found,Please request New One')
                return redirect('admin_forgot_password')

            if email_otp.otp == otp_from_form and email_otp.is_valid():
                email_otp.delete()

                request.session['admin_reset_password_allowed'] = True

                messages.success(request,'OTP verified successfully. Please set your new password')
                return redirect('admin_reset')
            elif not email_otp.is_valid():
                messages.error(request,'Your OTP has expired. Please request a new one.')
            else:
                messages.error(request,'Invalid or expired OTP. Please try again.')
    else:
        form = AdminVerifyOTPForm()
    return render(request,'adminAuth/otp-verification.html',{'form':form})

def admin_reset(request):
    if not request.session.get('admin_reset_password_allowed') or not request.session.get('reset_admin_email'):
        messages.error(request,'You are not authorized to access this page. Please verify your OTP first.')
        return redirect('admin_forgot_password')
    
    email = request.session.get('reset_admin_email')

    if not email or not request.session.get('admin_reset_password_allowed'):
        messages.error(request,'Your session has expired. Please start over.')
        return redirect('admin_forgot_password')
    
    if request.method == 'POST':
        form = AdminSetNewPassword(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user = get_object_or_404(CustomUser,email=email)

            user.set_password(new_password)
            user.save()
            messages.success(request,'Your password has been reset successfully. Please log in.')
            try:
                del request.session['reset_admin_email']
                del request.session['admin_reset_password_allowed']
            except KeyError:
                pass
            return redirect('admin_login')
    else:
        form = AdminSetNewPassword()
    return render(request,'adminAuth/reset-password.html',{'form':form})

def admin_logout(request):
    logout(request)
    return redirect('admin_login')
@method_decorator([never_cache,superuser_required],name='dispatch')
class AdminHome(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = CustomUser.objects.all().count()
        context["total_products"] = Product.objects.all().count()
        '''
            Total orders is fake you need to add when you create the orders
        '''
        context['total_orders'] = '02'
        context['total_revenue'] = '02'
        return context

'''User View Start Here Add Edit View '''
@method_decorator([never_cache,superuser_required],name='dispatch')
class AdminUserView(LoginRequiredMixin,ListView):
    model = CustomUser
    template_name = 'users/home_user.html'
    context_object_name = 'Users'
    ordering =['date_joined']


def toggle_user_block(request,id):
    user = get_object_or_404(CustomUser,id=id)
    user.is_active = not user.is_active

    user.save()

    status =  "Unblocked" if user.is_active  else "Blocked"
    messages.warning(request,f"{{user.email}} is {status} Successfuly")

    return redirect('admin_user')

'''User View End Here'''

'''Product View Start Here Add Edit View'''
@method_decorator([never_cache,superuser_required],name='dispatch')
class AdminProductsView(LoginRequiredMixin,ListView):
    model = Product
    template_name = 'products/products_admin.html'
    context_object_name = 'products'
    ordering = ['-created_at']
    paginate_by = 10 


    def get_queryset(self):
        queryset =  super().get_queryset()

        search_query = self.request.GET.get('search','')
        category_query = self.request.GET.get('category','')
        status_query = self.request.GET.get('status','')

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if category_query:
            queryset = queryset.filter(category__name__icontains=category_query)

        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorys"] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        return context
    
@login_required
@user_passes_test(lambda user: user.is_superuser,login_url='admin_login')
@transaction.atomic
def manage_product(request,id=None):
    product = None
    if id:
        product = get_object_or_404(Product,id=id)

    if request.method == "POST":
        product_form = AdminProductAddForm(request.POST,request.FILES,instance=product)
        formset = VariantFormSet(request.POST,instance=product,prefix = 'variants')
        formset_images = ImageFormSet(request.POST,request.FILES,instance=product,prefix='images')

        if product_form.is_valid() and formset.is_valid() and formset_images.is_valid():

            product = product_form.save()

            formset.instance = product
            formset_images.instance = product

            formset.save()
            formset_images.save()
            
            messages.success(request,"Product saved successfully.")
            return redirect('admin_products')
        else:
            print("Product Form Errors:", product_form.errors)
            print("Variant Formset Errors:", formset.errors)
            print("Image Formset Errors:", formset_images.errors)
            messages.error(request, "Please fix the errors below.")
    else:
        product_form = AdminProductAddForm(instance=product)
        formset = VariantFormSet(instance=product, prefix='variants')
        formset_images = ImageFormSet(instance=product, prefix='images')


    context = {
        'product_form' : product_form,
        'formset' : formset,
        'formset_images' : formset_images,
        'product':product
    }
    return render(request,'products/product_add_edit.html',context)

@login_required
@user_passes_test(lambda user: user.is_superuser,login_url='admin_login')
@transaction.atomic
def delete_product(request,id=None):
    product = get_object_or_404(Product,id=id)
    product.delete()
    messages.success(request,'Product Deleted Successfully')
    return redirect('admin_products')
'''Product View End Here'''
@method_decorator([never_cache,superuser_required],name='dispatch')
class AdminCategoryView(ListView):
    model = Category
    template_name = 'categorys/category.html'
    context_object_name = 'categorys'

@method_decorator([never_cache,superuser_required],name='dispatch')
class StockManagementView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'stock/stock_management.html'

    def get_queryset(self):
        return Product.objects.annotate(
            total_stock=Sum('variants__stock'), 
            variant_count=Count('variants')
        ).prefetch_related(
            'variants',         
            'variants__size'    
        )
    


    
    