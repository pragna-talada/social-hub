from django.contrib.auth import authenticate
from rest_framework import serializers

from default.helpers import check_request_rate_limit
from default.models import User, FriendRequest


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "username"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validate_data):
        user = User(email=validate_data["email"].lower(),username=validate_data["username"])
        user.set_password(validate_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    # email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class FriendRequestSerializer(serializers.ModelSerializer, ):
    class Meta:
        model = FriendRequest
        fields = ['receiver', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def create(self, validated_data):
        sender = self.context['request'].user  # Automatically assign the sender as the logged-in user
        receiver = validated_data['receiver']

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError("Friend request already sent.")

        # Ensure the sender is not sending a request to themselves
        if sender == receiver:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")

        check_request_rate_limit(sender)

        # Create a new friend request
        return FriendRequest.objects.create(sender=sender, receiver=receiver)


class FriendRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])


class PendingFriendRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['sender', "status", 'created_at']
