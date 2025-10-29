from django.shortcuts import render
from .models import Product,ProductImage,Category
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Max,Min
from django.views.generic import TemplateView,DetailView

# Create your views here.
'''
def home_page_view(request):
    products = Product.objects.select_related('category').order_by('?')[:4]
    featured_products = Product.objects.filter(is_featured=True).order_by('?')[:4]
    most_demanded = Product.objects.filter(is_most_demanded=True).order_by('?')[:4]
    today = timezone.now().date()
    new_arrivals = Product.objects.filter(created_at__date=today).order_by('?')[:4]
    context = {
        'products' : products,
        'featured_products' : featured_products,
        'most_demanded' : most_demanded,
        'new_arrivals' : new_arrivals
    }
    return render(request,'products/home.html',context)
'''

class HomePageView(TemplateView):
    template_name = 'products/home.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.select_related('category').order_by('?')[:4]
        featured_products = Product.objects.filter(is_featured=True).order_by('?')[:4]
        most_demanded = Product.objects.filter(is_most_demanded=True).order_by('?')[:4]
        today = timezone.now().date()
        new_arrivals = Product.objects.filter(created_at__date=today).order_by('?')[:4]


        context["products"] = products
        context["featured_products"] = featured_products
        context["most_demanded"] = most_demanded
        context["new_arrivals"] = new_arrivals
        return context
    

def product_list_view(request):
    categorys = Category.objects.all().order_by('name')
    
    selected_category_id = request.GET.get('category')

    products = Product.objects.filter(stock__gte = 1)
        
    if selected_category_id and selected_category_id != 'all':
        products = Product.objects.filter(category = selected_category_id,stock__gte = 1)

    price_range = Product.objects.aggregate(
        min_amount=Min('price'),
        max_amount=Max('price')
    )
    """
        Paginaton Logic Start here 
    """
    paginator = Paginator(products, 9) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 
    """
        If page_number is invalid (e.g., "abc" or 999 when you only have 20 pages), 
        it returns the last page instead of crashing
    """
    current_page = page_obj.number
    total_pages = paginator.num_pages
    window = 5 
    half_window = (window - 1) // 2

    start_page = max(1, current_page - half_window)
    end_page = min(total_pages, current_page + half_window)

    if current_page <= half_window:
        start_page = 1
        end_page = min(window, total_pages)
    
    elif current_page >= total_pages - half_window:
        end_page = total_pages
        start_page = max(1, total_pages - window + 1)

    custom_page_range = range(start_page, end_page + 1)
    """
        Paginaton Logic End here 
    """

    context = {
        'products': products,
        'categorys': categorys,
        'page_obj': page_obj,
        'custom_page_range': custom_page_range,
        'max_amount':  price_range['max_amount'] or 10000,
        'min_amount': price_range['min_amount'] or 0,
        'selected_category_id': selected_category_id,
    }
    
    return render(request,'products/products.html',context)

class ProductDetailedView(DetailView):
        model = Product
        template_name = 'products/product_detail.html'
        context_object_name = 'product'
        slug_field = 'slug' # Product.objects.get(slug='nike-shoes')
        slug_url_kwarg = 'slug'

        def get_queryset(self):
            query_set =  super().get_queryset() # This get the queryset or the product details
            return query_set.prefetch_related('images','size') # Take related Items of that products like images and size from their respective tables
        
        
        def get_context_data(self, **kwargs): # This method is used when you want to add more data to send to the template.
            context = super().get_context_data(**kwargs)
            all_images = self.object.images.all() # In this we are taking the related_name, images from productimage table
            context["images_list_limited"] = all_images[:4] # In here we are limiting the images we are sending
            context["sizes"] = self.object.size.all() # in here the size is the field name .
            
            return context
