from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from default import serializers
from default.models import User, FriendRequest
from default.serializers import FriendRequestSerializer, PendingFriendRequestsSerializer


@extend_schema(
    request=serializers.SignupSerializer,
    responses={
        400: "Bad Request",
        200: serializers.SignupSerializer,
    },
    methods=["POST"],
)
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        srz = serializers.SignupSerializer(data=request.data)
        if srz.is_valid():
            user = srz.save()
            return Response(data={"Message": "User created successfully. Login with the user."}, status=status.HTTP_201_CREATED)
        return Response(srz.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=serializers.LoginSerializer,
    responses={
        400: "Error",
        200: serializers.LoginSerializer,
    },
    methods=["POST"],
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        srz = serializers.LoginSerializer(data=request.data)
        if srz.is_valid():
            user = authenticate(username=srz.validated_data["username"].lower(), password=srz.validated_data["password"])
            if user is not None:
                login(request, user)
                return Response({'Message': "Login Successful"}, status=status.HTTP_200_OK)
            return Response(data={"Message": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(srz.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response(data={"Message": "Logged out successfully"}, status=status.HTTP_200_OK)


@extend_schema(
    request=serializers.UserSerializer,
    responses={
        400: "Bad Request",
        200: serializers.UserSerializer,
    },
    methods=["GET"],
    parameters=[
        OpenApiParameter(name="keyword", type=str, required=False, location=OpenApiParameter.QUERY)
    ],
)
class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', None)

        if keyword:
            # Exact email match
            if User.objects.filter(email__iexact=keyword).exists():
                return User.objects.filter(email__iexact=keyword)

            # Partial name match
            return User.objects.filter(
                username__icontains=keyword
            )

        # Return empty queryset if no keyword is provided
        return User.objects.all()


class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class AcceptRejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.filter(status='pending')
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FriendRequestActionSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.receiver != request.user:
            return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        if action == 'accept':
            instance.status = 'accepted'
        elif action == 'reject':
            instance.status = 'rejected'

        instance.save()
        return Response({"message": f"Friend request {action}ed."})


class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
        )


class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = PendingFriendRequestsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, status='pending')
