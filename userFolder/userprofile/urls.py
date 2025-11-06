from django.urls import path
from .views import ProfileView,ProfileAddressView,ProfilePaymentView,ProfilePaymentView,ProfileOrderView
urlpatterns = [
    path('info/',ProfileView.as_view(),name = 'profile_view_user'),
    path('address/',ProfileAddressView.as_view(),name = 'profile_adress'),
    path('payment/',ProfilePaymentView.as_view(),name = 'profile_payment'),
    path('order/',ProfileOrderView.as_view(),name = 'profile_order'),
]
