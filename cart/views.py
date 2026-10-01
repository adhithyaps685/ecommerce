from django.shortcuts import render
from rest_framework import status,viewsets
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from.models import *
from.serializers import *
from.models import Product,ProductImage
from.serializers import ProductSerializer
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import AdminLoginSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .authentication import CustomJWTAuthentication



class ProductViewSet(viewsets.ModelViewSet):
   # permission_classes = [IsAuthenticated]
    queryset=Product.objects.prefetch_related("images")
    serializer_class=ProductSerializer

    parser_classes=[
        MultiPartParser,
        FormParser,
    ]
    def create(self, request, *args, **kwargs):
        
        product=Product.objects.create(
            name=request.data.get("name"),
            description=request.data.get("description",""),
            price=request.data.get("price"),
            category=request.data.get("category")

        )
        images=request.FILES.getlist("images")

        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image
            )
        serializer=self.get_serializer(product)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    def update(self, request, *args, **kwargs):
        product=self.get_object()
        product.name=request.data.get(
            "name",
            product.name
        )
        product.description=request.data.get(
            "description",
            product.description
        )
        product.price=request.data.get(
            "price",
            product.price
        )
        product.save()
        images=request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image
            )
        serializer=self.get_serializer(product)
        return Response(serializer.data)

from rest_framework_simplejwt.tokens import AccessToken

class UserRegisterView(APIView):

    def post(self, request):

        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        phone = request.data.get("phone")
        address = request.data.get("address")

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            phone=phone,
            address=address
        )


from rest_framework_simplejwt.tokens import AccessToken

class UserLoginView(APIView):

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid username or password"},
                status=401
            )

        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid username or password"},
                status=401
            )

        access = AccessToken()

        access["user_id"] = user.id
        access["username"] = user.username

        return Response({
            "message": "Login successful",
            "access": str(access)
        }, status=200)

class AdminLoginView(APIView):
    def post(self,request):
        serializer=AdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        username=serializer.validated_data["username"]
        password=serializer.validated_data["password"]
        user=authenticate(
            username=username,
            password=password
        )
        print("USERNAME:",username)
        print("USER:",user)

        if user is not None and user.is_superuser:
            refresh=RefreshToken.for_user(user)

            return Response(
                {
                    "message":"Admin login successful",
                    "refresh":str(refresh),
                    "access":str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error":"invalid admin username or password"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

class CartView(APIView):

    def get(self, request):
        cart = Cart.objects.first()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):

        user_id = request.data.get("user")
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        cart, created = Cart.objects.get_or_create(
            user_id=user_id
        )

        product = Product.objects.get(id=product_id)

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

class AdminOrderView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):

        orders = Order.objects.all()

        serializer = OrderSerializer(orders, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
    def post(self, request):
        user = request.user

        cart = Cart.objects.get(user=user)

        order = Order.objects.create(
            user=user,
            total_amount=0,
            status="Pending"
        )

        total = 0

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total += item.product.price * item.quantity

        order.total_amount = total
        order.save()

        return Response(
            {"message": "Order placed successfully"},
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        user = request.user

        orders = Order.objects.filter(user=user)

        serializer = OrderSerializer(orders, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class SalesAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
    
    def get(self, request):

        total_orders = Order.objects.count()

        total_price = sum(
            order.total_amount for order in Order.objects.all()
        )

        total_products_sold = sum(
            item.quantity for item in OrderItem.objects.all()
        )

        return Response({
            "total_orders": total_orders,
            "total_price": total_price,
            "total_products_sold": total_products_sold
        })

class AdminLogoutView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {"message": "Logout successful"},
            status=200
        )