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

        user_id = request.data.get(
            "user_id"
        )

        if not user_id:

            return Response(
                {
                    "detail":
                    "user_id é obrigatório."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(
            User,
            pk=user_id
        )

        # =================================================
        # USER TYPE
        # =================================================

        if user.user_type != User.UserType.EMPRESA:

            return Response(
                {
                    "detail":
                    "Apenas usuários EMPRESA podem ser owner."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # ALREADY HAS COMPANY
        # =================================================

        if (
            user.company
            and user.company != company.id
        ):

            return Response(
                {
                    "detail":
                    "Usuário já possui outra empresa."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # REMOVE OLD OWNER
        # =================================================

        if (
            company.owner
            and company.owner != user
        ):

            old_owner = company.owner

            old_owner.company = None

            old_owner.save(
                update_fields=["company"]
            )

        # =================================================
        # SET OWNER
        # =================================================

        company.owner = user

        company.save(
            update_fields=["owner"]
        )

        # =================================================
        # UPDATE USER COMPANY
        # =================================================

        user.company = company.id

        user.save(
            update_fields=["company"]
        )

        return Response(
            {
                "detail":
                "Owner definido com sucesso."
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
                    "detail":
                    "Empresa não possui owner."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        owner = company.owner

        # =================================================
        # REMOVE COMPANY FROM USER
        # =================================================

        owner.company = None

        owner.save(
            update_fields=["company"]
        )

        # =================================================
        # REMOVE OWNER
        # =================================================

        company.owner = None

        company.save(
            update_fields=["owner"]
        )

        return Response(
            {
                "detail":
                "Owner removido com sucesso."
            },
            status=status.HTTP_200_OK
        )