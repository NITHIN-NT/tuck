from django.urls import path
from . import views
from .views import HomePageView,ProductDetailedView
urlpatterns = [
    path('',HomePageView.as_view(),name='Home_page_user'),
    path('products/',views.product_list_view,name='products_page_user'),
    path('products/<slug:slug>',ProductDetailedView.as_view(),name='Product_card_view')
]
