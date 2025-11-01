from django.shortcuts import render
from .models import Product,ProductImage,Category
from django.utils import timezone
from datetime import date,timedelta
from django.core.paginator import Paginator
from django.db.models import Max,Min
from django.views.generic import TemplateView,DetailView,ListView

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
    products = Product.objects.filter(stock__gte = 1).order_by('name')

    selected_category_id = request.GET.get('category')
    selected_price = request.GET.get('price_range')
    selected_sort = request.GET.get('sort')
    search = request.GET.get('search')


    if selected_sort == 'newest':
        products = products.order_by('-created_at')
    elif selected_sort == 'price_low_high':
        products = products.order_by('price')
    elif selected_sort == 'price-high-low':
        products = products.order_by('-price')
    elif selected_sort == 'name-asc':
        products = products.order_by('name')
    elif selected_sort == 'name-desc':
        products = products.order_by('-name')
    elif selected_sort == 'popularity':
        products = products.order_by('-popularity_score')
    elif selected_sort == 'rating':
        products = products.order_by('-average_rating')
    elif selected_sort == 'featured':
        products = products.order_by('-is_featured', '-created_at')

    if selected_category_id and selected_category_id != 'all':
        products = products.filter(category = selected_category_id)
    
    price_range = products.aggregate(
        min_amount=Min('price'),
        max_amount=Max('price')
    )


    if selected_price:
        try:
            price_limit = float(selected_price)
            products = products.filter(price__lte = price_limit)
        except ValueError:
            pass

    if search:
        products = products.filter(name__icontains=search)
    """
        Paginaton Logic Start here 
    """
    paginator = Paginator(products, 9) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 
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
        'categorys': categorys,
        'page_obj': page_obj,
        'custom_page_range': custom_page_range,
        'max_amount':  price_range['max_amount'] or 10000,
        'min_amount': price_range['min_amount'] or 0,
        'selected_category_id': selected_category_id,
        'selected_price' : selected_price,
        'selected_sort' : selected_sort,
        'search' : search
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
            product = self.object
            product_category = product.category
            related_products = Product.objects.filter(category=product_category).select_related('category').exclude(pk=product.pk)
            context['related_products'] = related_products[:4]
            
            
            return context
