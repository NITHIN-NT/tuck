from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('defaultadmin/', admin.site.urls),
    path('',include('userFolder.products.urls')),
    path('profile/',include('userFolder.userprofile.urls')),

    path('superuser/',include('admin_dashboard.urls'))
]
