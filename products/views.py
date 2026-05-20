import os
from django.utils.text import slugify

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsEmpresa

from .models import Product, ProductImage, Category
from .serializers import ProductSerializer, CategorySerializer


# =========================================================
# SAFE COMPANY HELPER
# =========================================================

def get_company(user):
    """
    Retorna a company do user de forma segura.
    Evita crash quando não existe owned_company.
    """
    return getattr(user, "owned_company", None)


# =========================================================
# CATEGORY VIEWSET (MVP CLEAN)
# =========================================================

class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmpresa]

    def get_queryset(self):

        company = get_company(self.request.user)

        if not company:
            return Category.objects.none()

        return Category.objects.filter(
            company=company,
            is_active=True
        ).order_by("name")

    def perform_create(self, serializer):

        company = get_company(self.request.user)

        if not company:
            raise Exception("Usuário não possui empresa vinculada.")

        serializer.save(company=company)

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

        company = get_company(self.request.user)

        if not company:
            return Product.objects.none()

        return Product.objects.filter(
            company=company,
            is_active=True
        ).select_related(
            "category",
            "company",
            "created_by"
        ).prefetch_related(
            "images"
        ).order_by("-id")

    # ----------------------------
    # CREATE
    # ----------------------------

    def create(self, request, *args, **kwargs):

        company = get_company(request.user)

        if not company:
            return Response(
                {"detail": "Usuário sem empresa vinculada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.save(
            company=company,
            created_by=request.user
        )

        # auto nome MVP
        product.name = f"#{product.id:05d} {product.name}"
        product.slug = slugify(product.name)
        product.save()

        # imagens
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
    # UPDATE
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
    # DELETE (SOFT)
    # ----------------------------

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()
        product.is_active = False
        product.save()

        return Response({"detail": "Produto removido."})