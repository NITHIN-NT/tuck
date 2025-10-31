from django.shortcuts import render
from django.views.generic import TemplateView,DetailView,ListView
from userFolder.products.models import Product,Category
from accounts.models import CustomUser
# Create your views here.

def admin_login(request):
    return render(request,'adminAuth/login.html')
def admin_forgot (request):
    return render(request,'adminAuth/forgot-password.html')
def admin_otp_verification (request):
    return render(request,'adminAuth/otp-verification.html')
def admin_reset(request):
    return render(request,'adminAuth/reset-password.html')
class AdminHome(TemplateView):
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

# def admin_home(request):
#     return render(request,'dashboard/dashboard.html')

'''User View Start Here Add Edit View '''
class AdminUserView(ListView):
    model = CustomUser
    template_name = 'users/home_user.html'
    context_object_name = 'Users'
    ordering =['-date_joined']

    # def get_queryset(self):
    #     queryset =  super().get_queryset()


# def admin_user_view(request):
#     return render(request,'users/home_user.html')

def admin_user_edit(request):
    return render(request,'users/edit_user.html')

def admin_user_add(request):
    return render(request,'users/add_user.html')

'''User View End Here'''

'''Product View Start Here Add Edit View'''
class AdminProductsView(ListView):
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
    
'''Product View End Here'''
class AdminCategoryView(ListView):
    model = Category
    template_name = 'categorys/category.html'
    context_object_name = 'categorys'

# def admin_user_edit(request):
#     return render(request,'users/edit_user.html')

# def admin_user_add(request):
#     return render(request,'users/add_user.html')


