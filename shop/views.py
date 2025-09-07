from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Product, CartItem, Category
from .serializers import ProductSerializer, CartItemSerializer, CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend

# ----------------- Auth -----------------
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({"error":"Username and password required"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error":"Username already exists"}, status=400)
    user = User.objects.create_user(username=username, password=password)
    return Response({"message":"User created successfully"})

# ----------------- Product ViewSet -----------------
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'category__name': ['exact'],
        'price': ['lte']
    }

# ----------------- Category -----------------
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'detail': 'Product ID required'}, status=400)

        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)