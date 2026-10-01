from .models import Product,ProductImage
from rest_framework import serializers
from.models import *

class ProductImageSerializer(serializers.ModelSerializer):
    image=serializers.SerializerMethodField()

    class Meta:
        model=ProductImage
        fields=[
            "image"
        ]
        read_only_fields=[
            "id",
            "created_at",
       ]
    def get_image(self,obj):
        if not obj.image:
            return None

        return obj.image.url

    
class ProductSerializer(serializers.ModelSerializer):
    images= ProductImageSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model=Product

        fields=[
            "id",
            "name",
            "price",
            "category",
            "images",
            "create_at",
            "updated_at",
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

class AdminLoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity"
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "items",
            "created_at",
            "updated_at"
        ]

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = "__all__"



class OrderSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"