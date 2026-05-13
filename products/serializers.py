from rest_framework import serializers
from .models import Product, ProductImage, Category


# =========================================================
# PRODUCT IMAGE
# =========================================================

class ProductImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
            "order"
        ]


# =========================================================
# CATEGORY
# =========================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = [
            "id",
            "company",
            "created_at",
            "updated_at",
            "is_active"
        ]


# =========================================================
# PRODUCT
# =========================================================

class ProductSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(many=True, read_only=True)

    profit = serializers.ReadOnlyField()
    margin = serializers.ReadOnlyField()

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = [
            "id",
            "company",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
            "profit",
            "margin"
        ]