from django.urls import path
from cart.views import UserRegisterView,UserLoginView,AdminLoginView,ProductViewSet,CartView,AdminOrderView,OrderView,SalesAnalysisView,LogoutView
from cart.views import AdminLogoutView
urlpatterns = [
    path("register/",UserRegisterView.as_view(),name="register"),
    path("login/",UserLoginView.as_view(),name="login"),
    path("admin/",AdminLoginView.as_view(),name="admin"),
    path("products/",ProductViewSet.as_view({"post":"create"})),
    path("products/<uuid:pk>/",ProductViewSet.as_view({"put":"update","patch":"partial_update"})),
    path("cart/",CartView.as_view(),name="cart"),
    path("admin/orders/",AdminOrderView.as_view()),
    path("order/",OrderView.as_view(),name="order"),
    path("admin/sales/",SalesAnalysisView.as_view(),name="sales-analysis"),
    path("logout/", AdminLoginView.as_view(), name="logout"),
    path("user/logout/", LogoutView.as_view(), name="logout"),
]