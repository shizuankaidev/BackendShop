import os
from django.utils.text import slugify
from django.db.models import Q, F

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsEmpresa

from .models import Product, ProductImage, Category
from .serializers import ProductSerializer, CategorySerializer


# =========================================================
# CATEGORY VIEWSET (MVP CLEAN)
# =========================================================

class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmpresa]

    def get_queryset(self):
        return Category.objects.filter(
            company=self.request.user.owned_company,
            is_active=True
        ).order_by("name")

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.owned_company)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save()
        return Response({"detail": "Categoria removida."})


# =========================================================
# PRODUCT VIEWSET (MVP FINAL)
# =========================================================

class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmpresa]

    parser_classes = [MultiPartParser, FormParser]

    # ----------------------------
    # QUERYSET
    # ----------------------------

    def get_queryset(self):

        return Product.objects.filter(
            company=self.request.user.owned_company,
            is_active=True
        ).select_related(
            "category",
            "company",
            "created_by"
        ).prefetch_related(
            "images"
        ).order_by("-id")

    # ----------------------------
    # CREATE (MVP INTELIGENTE)
    # ----------------------------

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = request.user.owned_company

        product = serializer.save(
            company=company,
            created_by=request.user
        )

        # =====================================================
        # AUTO ID PREFIX NO NOME (MVP FEATURE)
        # =====================================================

        product.name = f"#{product.id:05d} {product.name}"

        product.slug = slugify(product.name)

        product.save()

        # =====================================================
        # IMAGENS
        # =====================================================

        images = request.FILES.getlist("images")

        if images:

            for index, image in enumerate(images):

                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(index == 0),
                    order=index
                )

        product.refresh_from_db()

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )

    # ----------------------------
    # UPDATE (MVP CLEAN)
    # ----------------------------

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)

        product = serializer.save()

        images = request.FILES.getlist("images")

        if images:

            ProductImage.objects.filter(product=product).delete()

            for index, image in enumerate(images):

                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(index == 0),
                    order=index
                )

        product.refresh_from_db()

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_200_OK
        )

    # ----------------------------
    # SOFT DELETE
    # ----------------------------

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()
        product.is_active = False
        product.save()

        return Response({"detail": "Produto removido."})