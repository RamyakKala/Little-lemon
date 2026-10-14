"""
URL configuration for LittleLemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from LittleLemonAPI.views import CategoryViewSet, MenuItemViewSet, CartViewSet, OrderViewSet
from LittleLemonAPI.group_views import DeliveryCrewUsersView, ManagerUsersView
from restaurant import views as restaurant_views

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('menu-items', MenuItemViewSet, basename='menu-item')
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')
router.register('bookings', restaurant_views.BookingViewSet, basename='booking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', restaurant_views.booking_form, name='booking-form'),
    path('menu/', restaurant_views.menu_page, name='menu-page'),
    path('bookings', restaurant_views.bookings, name='bookings'),
    path('api/', include(router.urls)),
    path('api/registration/', UserViewSet.as_view({'post': 'create'}), name='api-registration'),
    path('api/', include('djoser.urls.authtoken')),
    path('api/groups/manager/users', ManagerUsersView.as_view()),
    path('api/groups/manager/users/<int:pk>', ManagerUsersView.as_view()),
    path('api/groups/delivery-crew/users', DeliveryCrewUsersView.as_view()),
    path('api/groups/delivery-crew/users/<int:pk>', DeliveryCrewUsersView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
