from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser
# from django.contrib.auth.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=CustomUser.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=CustomUser.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'phone_number','address','area_code','last_logout','zone_name','is_superuser','is_staff','login_user_name']


    # role=serializers.CharField(max_length=50)
    # phone_number=serializers.CharField(max_length=50)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            phone_number=validated_data['phone_number'],
            address=validated_data['address'],
            area_code=validated_data['area_code'],
            zone_name=validated_data['zone_name'],
            is_superuser=validated_data['is_superuser'],
            is_staff=validated_data['is_staff'],
            login_user_name=validated_data['login_user_name'],
            last_logout=validated_data['last_logout'],
        )
        return user

   
     