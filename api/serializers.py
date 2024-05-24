from rest_framework.serializers import ModelSerializer
from api.models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ('user_permissions', 'groups', 'is_superuser', 'is_staff', 'password')


class UserRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups', 'is_superuser', 'is_staff',
                   'user_type', 'is_active', 'last_login')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.user_type = USER
        user.save()
        return user


class LoginSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'