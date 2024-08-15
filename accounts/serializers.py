from rest_framework import serializers
from accounts.models import Users

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'password','confirm_password']
    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Password dose not match")
        return super().validate(attrs)
    def create(self, validated_data):
        user = Users(
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user