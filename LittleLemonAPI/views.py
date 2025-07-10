from django.shortcuts import get_object_or_404
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem, Cart, Order
from django.contrib.auth.models import User, Group
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer

def user_is_in_group(user, group_name):
  return user.groups.filter(name=group_name).exists()

def get_user_role_flags(user):
  return {
    "is_authenticated": user.is_authenticated,
    "is_manager": user_is_in_group(user, "Manager"),
    "is_delivery": user_is_in_group(user, "Delivery crew")
  }

@api_view(['GET', 'POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def menu_items_view(request):
  role = get_user_role_flags(request.user)
  if request.method == 'GET':
    menu_items = MenuItem.objects.select_related('category').all()
    ordering = request.query_params.get('ordering')
    perpage = request.query_params.get('perpage', default=3)
    page = request.query_params.get('page', default=1)
    if ordering:
      ordering_fields = ordering.split(',')
      items = items.order_by(*ordering_fields)
    paginator = Paginator(menu_items, per_page=perpage)
    try:
      menu_items = paginator.page(page)
      pass
    except EmptyPage:
      menu_items = []
    serialized_item = MenuItemSerializer(menu_items, many = True, context={'request': request})
    return Response(serialized_item.data, status=status.HTTP_200_OK)
  elif request.method == 'POST' and role["is_manager"]:
      serialized_item = MenuItemSerializer(data=request.data)
      serialized_item.is_valid(raise_exception=True)
      serialized_item.save()
      return Response(serialized_item.data, status=status.HTTP_201_CREATED)
  return Response(status= status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item_view(request, menuItem):
  item = get_object_or_404(MenuItem,pk=menuItem)
  role = get_user_role_flags(request.user)
  if request.method == 'GET':
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data, status=status.HTTP_200_OK)
  elif request.method in ['PUT', 'PATCH'] and role["is_manager"]:
      serialized_item = MenuItemSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
      serialized_item.is_valid(raise_exception=True)
      serialized_item.save()
      return Response(serialized_item.data, status=status.HTTP_200_OK)
  elif request.method == 'DELETE' and role["is_manager"]:
      item.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
  return Response(status= status.HTTP_403_FORBIDDEN)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def managers_view(request):
  if not user_is_in_group(request.user,  "Manager"):
    return Response(status=status.HTTP_403_FORBIDDEN)
  if request.method == 'GET':
    users = User.objects.filter(groups__name="Manager")
    serialized_users = UserSerializer(users, many = True, context={'request': request})
    return Response(serialized_users.data, status=status.HTTP_200_OK)
  if request.method == 'POST':
    serialized_user = UserSerializer(data=request.data)
    serialized_user.is_valid(raise_exception=True)
    user_instance = serialized_user.save()
    manager_group = Group.objects.get(name="Manager")
    user_instance.groups.add(manager_group)
    new_serialized = UserSerializer(user_instance, context={'request': request})
    return Response(new_serialized.data, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def single_manager_view(request, userId):
  if not user_is_in_group(request.user,  "Manager"):
    return Response(status=status.HTTP_403_FORBIDDEN)
  
  user = get_object_or_404(User,pk=userId)
  if user_is_in_group(user, "Manager"):
    if user == request.user:
      return Response({"detail": "No puedes eliminarte a ti mismo."}, status=400)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  
  return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def delivery_crews_view(request):
  if not user_is_in_group(request.user,  "Manager"):
    return Response(status=status.HTTP_403_FORBIDDEN)
  if request.method == 'GET':
    users = User.objects.filter(groups__name="Delivery crew")
    serialized_users = UserSerializer(users, many = True, context={'request': request})
    return Response(serialized_users.data, status=status.HTTP_200_OK)
  if request.method == 'POST':
    serialized_user = UserSerializer(data=request.data)
    serialized_user.is_valid(raise_exception=True)
    user_instance = serialized_user.save()
    delivery_group = Group.objects.get(name="Delivery crew")
    user_instance.groups.add(delivery_group)
    new_serialized = UserSerializer(user_instance, context={'request': request})
    return Response(new_serialized.data, status=status.HTTP_201_CREATED)
  return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def single_delivery_crew_view(request, userId):
  if not user_is_in_group(request.user,  "Manager"):
    return Response(status=status.HTTP_403_FORBIDDEN)
  user = get_object_or_404(User,pk=userId)
  if user_is_in_group(user, "Delivery crew"):
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items_view(request):
  if request.method == 'GET':
    cart_items =  Cart.objects.filter(user=request.user)
    serialized_cart = CartSerializer(cart_items, many = True, context={'request': request})
    return Response(serialized_cart.data, status=status.HTTP_200_OK)
  if request.method == 'POST':
    serialized_cart = CartSerializer(data=request.data, context={'request': request})
    serialized_cart.is_valid(raise_exception=True)
    serialized_cart.save()
    return Response(serialized_cart.data, status=status.HTTP_201_CREATED)
  if request.method == 'DELETE':
    cart_items = Cart.objects.filter(user=request.user)
    cart_items.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  return Response(status= status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_view(request):
  role = get_user_role_flags(request.user)
  if request.method == 'GET':
    orders = []
    if not role["is_manager"] and not role["is_delivery"]:
      orders = Order.objects.filter(user=request.user)
    elif role["is_manager"]:
      orders = Order.objects.all()
    elif role["is_delivery"]:
      orders = Order.objects.filter(delivery_crew=request.user)
    ordering = request.query_params.get('ordering')
    perpage = request.query_params.get('perpage', default=3)
    page = request.query_params.get('page', default=1)
    if ordering:
      ordering_fields = ordering.split(',')
      items = items.order_by(*ordering_fields)
    paginator = Paginator(orders, per_page=perpage)
    try:
      orders = paginator.page(page)
      pass
    except EmptyPage:
      orders = []
    serialized_orders = OrderSerializer(orders, many = True, context={'request': request})
    return Response(serialized_orders.data, status=status.HTTP_200_OK)
  if request.method == 'POST':
    serialized_order = OrderSerializer(data=request.data, context={'request': request})
    serialized_order.is_valid(raise_exception=True)
    order = serialized_order.save()
    response_data = OrderSerializer(order).data
    return Response(response_data, status=status.HTTP_201_CREATED)
  return Response(status= status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def single_order_view(request,orderId):
  user = request.user
  role = get_user_role_flags(request.user)
  if request.method == 'GET':
    if not role["is_manager"] and not role["is_delivery"]:
      order = get_object_or_404(Order, id=orderId, user=user)
    else:
      order = get_object_or_404(Order, id=orderId)

    serializer = OrderSerializer(order, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  if request.method in ['PUT', 'PATCH']:
    order = get_object_or_404(Order, id=orderId)
    if role["is_manager"]:
      serializer = OrderSerializer(order, data=request.data, partial=True, context={'request': request})
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    elif role["is_delivery"]:
      status_data = {"status": request.data.get("status")}
      if order.delivery_crew != user:
        return Response({"detail": "No autorizado para modificar esta orden."}, status=status.HTTP_403_FORBIDDEN)
      serializer = OrderSerializer(order, data=status_data, partial=True, context={'request': request})
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

  if request.method == 'DELETE' and role["is_manager"]:
    order = get_object_or_404(Order, id=orderId)
    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  return Response(status= status.HTTP_403_FORBIDDEN)