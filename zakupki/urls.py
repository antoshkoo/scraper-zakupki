from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from zakupki import views
from zakupki.views import MainView, CustomerView, CustomerDetailView, TestView, UserLoginView, UserLogoutView

urlpatterns = [
    path('', MainView.as_view(), name='main_url'),
    path('login/', UserLoginView.as_view(), name='login_url'),
    path('logout/', UserLogoutView.as_view(), name='logout_url'),
    path('customer/', CustomerView.as_view(), name='customer_url'),
    path('customer/<inn>/', CustomerDetailView.as_view(), name='customer_detail_url'),
    path('test/', TestView.as_view(), name='test_url'),
    path('customer/<inn>/export/csv/', views.export, name='export_url'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
