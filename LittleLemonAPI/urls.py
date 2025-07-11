from django.urls import path
from . import views

urlpatterns = [
  path('categories', views.categories_view),
  path('menu-items', views.menu_items_view),
  path('menu-items/<int:menuItem>', views.single_menu_item_view),

  path('groups/manager/users', views.managers_view),
  path('groups/manager/users/<int:userId>', views.single_manager_view),
  path('groups/delivery-crew/users/<int:userId>', views.single_delivery_crew_view),
  
  path('cart/menu-items', views.cart_menu_items_view),
  path('orders', views.orders_view),

  path('orders/<int:orderId>', views.single_order_view),

  ]