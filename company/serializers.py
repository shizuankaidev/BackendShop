from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):

    owner_email = serializers.EmailField(
        source="owner.email",
        read_only=True
    )

    owner_username = serializers.CharField(
        source="owner.username",
        read_only=True
    )

    owner_company = serializers.IntegerField(
        source="owner.company",
        read_only=True
    )

    class Meta:

        model = Company

        fields = [
            "id",
            "name",
            "cnpj",

            "owner",
            "owner_email",
            "owner_username",
            "owner_company",

            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "owner",
            "owner_email",
            "owner_username",
            "owner_company",
            "created_at",
        ]