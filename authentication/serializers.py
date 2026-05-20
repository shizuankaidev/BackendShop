from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# =====================================================
# HELPERS
# =====================================================

def get_company_object(user):

    company = getattr(user, 'company', None)

    if not company:
        return None

    # SAFE:
    # evita erro quando company vira int
    # ou qualquer valor inválido

    if isinstance(company, int):
        return None

    if not hasattr(company, 'id'):
        return None

    return company


# =====================================================
# ME
# =====================================================

class MeSerializer(serializers.ModelSerializer):

    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'user_type',
            'company',
            'is_active',
            'is_verified',
        )

    def get_company(self, obj):

        company = get_company_object(obj)

        if not company:
            return None

        return {
            'id': company.id,
            'name': company.name,
        }


# =====================================================
# JWT CUSTOM
# =====================================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        company = get_company_object(user)

        token['user_type'] = user.user_type
        token['email'] = user.email
        token['is_verified'] = user.is_verified

        token['company'] = (
            company.id
            if company else None
        )

        token['company_name'] = (
            company.name
            if company else None
        )

        return token


# =====================================================
# REGISTER
# =====================================================

class RegisterSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    class Meta:
        model = User

        fields = (
            'id',
            'email',
            'username',
            'password',
            'user_type',
        )

        read_only_fields = ('id',)

    # =================================================
    # VALIDATE USER TYPE
    # =================================================

    def validate_user_type(self, value):

        request = self.context.get('request')

        if (
            not request or
            not request.user.is_authenticated
        ):

            raise serializers.ValidationError(
                'Usuário não autenticado.'
            )

        creator = request.user

        if creator.user_type == User.UserType.ADMIN:

            return value

        if creator.user_type == User.UserType.EMPRESA:

            allowed = [
                User.UserType.AFILIADO,
                User.UserType.CLIENTE,
            ]

            if value not in allowed:

                raise serializers.ValidationError(
                    'Empresa só pode criar Afiliado ou Cliente.'
                )

            return value

        if creator.user_type == User.UserType.AFILIADO:

            if value != User.UserType.CLIENTE:

                raise serializers.ValidationError(
                    'Afiliado só pode criar Cliente.'
                )

            return value

        raise serializers.ValidationError(
            'Este tipo de usuário não pode criar outros.'
        )

    # =================================================
    # CREATE
    # =================================================

    def create(self, validated_data):

        password = validated_data.pop(
            'password'
        )

        request = self.context.get(
            'request'
        )

        creator = request.user

        user = User(
            **validated_data
        )

        user.set_password(password)

        user.created_by = creator

        # SAFE COMPANY

        company = get_company_object(
            creator
        )

        if company:
            user.company = company

        user.save()

        return user


# =====================================================
# PROFILE
# =====================================================

class ProfileSerializer(
    serializers.ModelSerializer
):

    company = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            'id',
            'email',
            'username',
            'user_type',
            'company',
            'is_active',
            'is_verified',
        )

    def get_company(self, obj):

        company = get_company_object(obj)

        if not company:
            return None

        return {
            'id': company.id,
            'name': company.name,
        }


# =====================================================
# USER LIST SERIALIZER
# =====================================================

class UserSerializer(
    serializers.ModelSerializer
):

    company = serializers.SerializerMethodField()

    created_by = serializers.SerializerMethodField()

    is_company_owner = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = User

        fields = (
            'id',
            'email',
            'username',
            'user_type',
            'company',
            'created_by',
            'is_company_owner',
            'is_active',
            'is_verified',
        )

    # =================================================
    # COMPANY
    # =================================================

    def get_company(self, obj):

        company = get_company_object(obj)

        if not company:
            return None

        return {
            'id': company.id,
            'name': company.name,
        }

    # =================================================
    # CREATED BY
    # =================================================

    def get_created_by(self, obj):

        created_by = getattr(
            obj,
            'created_by',
            None
        )

        if not created_by:
            return None

        return {
            'id': created_by.id,
            'email': created_by.email,
            'username': created_by.username,
        }

    # =================================================
    # OWNER
    # =================================================

    def get_is_company_owner(self, obj):

        company = get_company_object(obj)

        if not company:
            return False

        return company.owner_id == obj.id