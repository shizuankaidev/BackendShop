from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.permissions import IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
User = get_user_model()


class AdminUsersListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().values(
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "date_joined"
        )

        return Response({
            "count": users.count(),
            "users": list(users)
        })