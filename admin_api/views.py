from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsAdmin
from authentication.models import User


# =========================================================
# ADMIN USERS LIST
# =========================================================

class AdminUsersListView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):

        data = request.data or {}

        queryset = User.objects.all()

        # =========================
        # FILTERS
        # =========================

        if data.get("id"):
            queryset = queryset.filter(id=data["id"])

        if data.get("username"):
            queryset = queryset.filter(username__icontains=data["username"])

        if data.get("email"):
            queryset = queryset.filter(email__icontains=data["email"])

        if data.get("user_type"):
            queryset = queryset.filter(user_type=data["user_type"])

        if data.get("is_active") is not None:
            queryset = queryset.filter(is_active=data["is_active"])

        if data.get("is_staff") is not None:
            queryset = queryset.filter(is_staff=data["is_staff"])

        if data.get("is_verified") is not None:
            queryset = queryset.filter(is_verified=data["is_verified"])

        # COMPANY FILTER (AGORA CORRETO)
        if data.get("company") is not None:
            queryset = queryset.filter(company=data["company"])

        if data.get("has_company") is True:
            queryset = queryset.exclude(company__isnull=True)

        if data.get("has_company") is False:
            queryset = queryset.filter(company__isnull=True)

        queryset = queryset.order_by("-date_joined")

        # =========================
        # PAGINATION
        # =========================

        page = int(data.get("page", 1))
        page_size = min(int(data.get("page_size", 10)), 100)

        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)

        # =========================
        # RESPONSE (SEM select_related!)
        # =========================

        users = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "user_type": u.user_type,

                "company": u.company,  # só ID

                "created_by": {
                    "id": u.created_by_id,
                    "email": u.created_by.email,
                } if u.created_by else None,

                "is_company_owner": False,

                "is_active": u.is_active,
                "is_staff": u.is_staff,
                "is_verified": u.is_verified,
                "date_joined": u.date_joined,
            }
            for u in current_page.object_list
        ]

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": current_page.number,
            "has_next": current_page.has_next(),
            "has_previous": current_page.has_previous(),
            "users": users
        })

# =========================================================
# ADMIN USER UPDATE
# =========================================================
class AdminUserUpdateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Usuário não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data

        # =========================
        # CAMPOS PERMITIDOS
        # =========================

        user.email = data.get("email", user.email)
        user.username = data.get("username", user.username)
        user.user_type = data.get("user_type", user.user_type)
        user.is_active = data.get("is_active", user.is_active)
        user.is_verified = data.get("is_verified", user.is_verified)

        # COMPANY (opcional)
        company = data.get("company")

        if company is not None:
            user.company_id = company

        user.save()

        return Response(
            {
                "detail": "Usuário atualizado com sucesso."
            },
            status=status.HTTP_200_OK
        )