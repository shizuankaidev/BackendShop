# authentication/views.py

from django.contrib.auth import get_user_model

from rest_framework import generics, permissions, serializers
from rest_framework.pagination import LimitOffsetPagination

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication
)

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserSerializer,
)

User = get_user_model()


# =========================================================
# PAGINATION
# =========================================================

class SafeLimitOffsetPagination(LimitOffsetPagination):

    default_limit = 20

    max_limit = 100


# =========================================================
# LOGIN JWT
# =========================================================

class LoginView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

    permission_classes = [
        permissions.AllowAny
    ]


# =========================================================
# REFRESH JWT
# =========================================================

class RefreshView(TokenRefreshView):

    permission_classes = [
        permissions.AllowAny
    ]


# =========================================================
# REGISTER
# =========================================================

class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer

    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.AllowAny
    ]

    # =====================================================
    # CREATE USER
    # =====================================================

    def perform_create(self, serializer):

        request_user = self.request.user

        requested_type = self.request.data.get(
            "user_type",
            User.UserType.CLIENTE
        )

        # =================================================
        # VALIDA USER TYPE
        # =================================================

        if requested_type not in User.UserType.values:

            raise serializers.ValidationError(
                {
                    "user_type": (
                        f"Tipo inválido: {requested_type}"
                    )
                }
            )

        # =================================================
        # NÃO AUTENTICADO
        # =================================================

        if (
            not request_user
            or not request_user.is_authenticated
        ):

            serializer.save(
                user_type=User.UserType.CLIENTE
            )

            return

        # =================================================
        # ADMIN
        # =================================================

        if (
            request_user.user_type == User.UserType.ADMIN
            or request_user.is_superuser
        ):

            serializer.save(
                created_by=request_user,
                user_type=requested_type
            )

            return

        # =================================================
        # EMPRESA
        # =================================================

        if request_user.user_type == User.UserType.EMPRESA:

            allowed_types = [
                User.UserType.AFILIADO,
                User.UserType.CLIENTE
            ]

            if requested_type not in allowed_types:

                raise serializers.ValidationError(
                    {
                        "user_type": (
                            "Empresa só pode criar "
                            "AFILIADO ou CLIENTE."
                        )
                    }
                )

            serializer.save(
                created_by=request_user,
                user_type=requested_type
            )

            return

        # =================================================
        # AFILIADO
        # =================================================

        if request_user.user_type == User.UserType.AFILIADO:

            serializer.save(
                created_by=request_user,
                user_type=User.UserType.CLIENTE
            )

            return

        # =================================================
        # CLIENTE
        # =================================================

        serializer.save(
            user_type=User.UserType.CLIENTE
        )


# =========================================================
# PROFILE
# =========================================================

class ProfileView(generics.RetrieveAPIView):

    serializer_class = ProfileSerializer

    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = User.objects.all()

    def get_object(self):

        return self.request.user


# =========================================================
# USER LIST
# =========================================================

class UserListView(generics.ListAPIView):

    serializer_class = UserSerializer

    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    pagination_class = SafeLimitOffsetPagination

    # =====================================================
    # QUERYSET
    # =====================================================

    def get_queryset(self):

        user = self.request.user

        # =================================================
        # ADMIN
        # =================================================

        if (
            user.user_type == User.UserType.ADMIN
            or user.is_superuser
        ):

            return User.objects.all().order_by("-id")

        # =================================================
        # EMPRESA
        # =================================================

        if user.user_type == User.UserType.EMPRESA:

            return User.objects.filter(
                created_by=user
            ).order_by("-id")

        # =================================================
        # AFILIADO
        # =================================================

        if user.user_type == User.UserType.AFILIADO:

            return User.objects.filter(
                created_by=user
            ).order_by("-id")

        # =================================================
        # CLIENTE
        # =================================================

        return User.objects.none()