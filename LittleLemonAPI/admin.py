from django.contrib import admin
from .models import Category,MenuItem, Cart, Order, OrderItem

@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin): 
    list_display = ("slug", "title")
    search_fields = ("title__startswith", )

@admin.register(MenuItem) 
class MenuItemAdmin(admin.ModelAdmin): 
    list_display = ("title", "price", "category")
    search_fields = ("title__startswith", )

@admin.register(Cart) 
class CartAdmin(admin.ModelAdmin): 
    list_display = ("user", "menuitem", "quantity", "unit_price", "price")
    search_fields = ("user", )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): 
    list_display = ("id","user", "delivery_crew", "status", "total", "date")
    search_fields = ("user", )
admin.site.register(OrderItem)
class OrderAdmin(admin.ModelAdmin): 
    list_display = ("id","user", "delivery_crew", "status", "total", "date")
    search_fields = ("user", )
