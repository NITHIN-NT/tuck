from django.urls import path
from . import views
from .views import AdminProductsView,AdminCategoryView
urlpatterns = [
    path('',views.admin_home,name='admin_home'),
    
    path('users/',views.admin_user_view,name='admin_user'),
    path('users/edit',views.admin_user_edit,name='admin_user_edit'),
    path('users/add',views.admin_user_add,name='admin_user_add'),

    path('products/',AdminProductsView.as_view(),name='admin_products'),
    # path('products/edit',views.admin_products_edit,name='admin_products_edit'),
    # path('products/add',views.admin_products_add,name='admin_products_add'),

    path('category/',AdminCategoryView.as_view(),name='admin_category'),
    # path('category/edit',views.admin_category_edit,name='admin_category_edit'),
    # path('category/add',views.admin_category_add,name='admin_category_add'),

]
