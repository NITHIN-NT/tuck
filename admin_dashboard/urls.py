from django.urls import path
from . import views
from .views import AdminProductsView,AdminCategoryView,AdminUserView,AdminHome
urlpatterns = [

    path('',views.admin_login,name='admin_login'),
    path('forget/',views.admin_forgot,name='admin_forgot_password'),
    path('verifi/',views.admin_otp_verification,name='admin_otp_verification'),
    path('reset/',views.admin_reset,name='admin_reset'),

    path('strap/',AdminHome.as_view(),name='admin_home'),

    path('users/',AdminUserView.as_view(),name='admin_user'),
    path('users/edit',views.admin_user_edit,name='admin_user_edit'),
    path('users/add',views.admin_user_add,name='admin_user_add'),

    path('products/',AdminProductsView.as_view(),name='admin_products'),
    # path('products/edit',views.admin_products_edit,name='admin_products_edit'),
    # path('products/add',views.admin_products_add,name='admin_products_add'),

    path('category/',AdminCategoryView.as_view(),name='admin_category'),
    # path('category/edit',views.admin_category_edit,name='admin_category_edit'),
    # path('category/add',views.admin_category_add,name='admin_category_add'),

]
