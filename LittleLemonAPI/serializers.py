from django.db import transaction
from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
      model = Category
      fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
  category = CategorySerializer(read_only=True)
  category_id = serializers.IntegerField(write_only=True)

  class Meta:
    model = MenuItem
    fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class GroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = Group
    fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
  groups = serializers.SlugRelatedField(
    many=True,
    slug_field='name',
    queryset=Group.objects.all()
  )

  class Meta:
    model = User
    fields = ['id', 'username','email', 'first_name', 'last_name', 'groups']
    read_only_fields = ['first_name', 'last_name', 'groups']


class CartSerializer(serializers.ModelSerializer):
  menuitem = MenuItemSerializer(read_only=True)
  menuitem_id = serializers.IntegerField(write_only=True)
  # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2,read_only=True)
  class Meta:
    model = Cart
    fields = ['id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price', 'user']
    read_only_fields = ['user','unit_price','price']

  def create(self, validated_data):
    validated_data["user"] = self.context['request'].user
    menuitem = MenuItem.objects.get(id=validated_data["menuitem_id"])
    validated_data["unit_price"] = menuitem.price
    validated_data["price"] = validated_data["quantity"] * validated_data["unit_price"]
    return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
  delivery_crew_id = serializers.PrimaryKeyRelatedField(
      source='delivery_crew',
      queryset=User.objects.all(),
      required=False,
      write_only=True
  )
  status = serializers.BooleanField(required=False)
  class Meta:
    model = Order
    fields = ['id', 'user', 'delivery_crew','delivery_crew_id', 'status', 'total', 'date']
    read_only_fields = ['id','user','delivery_crew', 'total', 'date']

  def create(self, _):
    user = self.context['request'].user
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
      raise serializers.ValidationError("El carrito está vacío.")
    
    with transaction.atomic():
      order = Order.objects.create(user=user, total=0)      
      total = 0
      for item in cart_items:
        total += item.price
        OrderItem.objects.create(
          order = order,
          menuitem = item.menuitem,
          quantity=item.quantity,
          unit_price=item.unit_price,
          price=item.price,
        )
      order.total = total
      order.save()
      cart_items.delete()
    return order