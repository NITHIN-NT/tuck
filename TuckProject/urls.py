from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('defaultadmin/', admin.site.urls),
    path('',include('products.urls')),
    path('profile/',include('userFolder.userprofile.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),


    path('superuser/',include('Admin.urls'))
]
