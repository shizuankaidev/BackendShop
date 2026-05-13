from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from authentication.permissions import IsAdmin
from authentication.models import User

from .models import Company
from .serializers import CompanySerializer


class CompanyAdminViewSet(ModelViewSet):

    queryset = Company.objects.all()

    serializer_class = CompanySerializer

    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    # =====================================================
    # SET OWNER
    # =====================================================

    def set_owner(self, request, pk=None):

        company = self.get_object()

        user_id = request.data.get("user_id")

        if not user_id:

            return Response(
                {
                    "detail": "user_id é obrigatório."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(
            User,
            pk=user_id
        )

        # =================================================
        # VALIDA USER TYPE
        # =================================================

        if user.user_type != User.UserType.EMPRESA:

            return Response(
                {
                    "detail": "Apenas usuários EMPRESA podem ser owner."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # JÁ POSSUI OWNER
        # =================================================

        if (
            getattr(user, "owned_company", None)
            and user.owned_company != company
        ):

            return Response(
                {
                    "detail": "Usuário já possui outra empresa."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # DEFINE OWNER
        # =================================================

        company.owner = user

        company.save(
            update_fields=["owner"]
        )

        return Response(
            {
                "detail": "Owner definido com sucesso."
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # REMOVE OWNER
    # =====================================================

    def revoke_owner(self, request, pk=None):

        company = self.get_object()

        if not company.owner:

            return Response(
                {
                    "detail": "Empresa não possui owner."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        company.owner = None

        company.save(
            update_fields=["owner"]
        )

        return Response(
            {
                "detail": "Owner removido com sucesso."
            },
            status=status.HTTP_200_OK
        )