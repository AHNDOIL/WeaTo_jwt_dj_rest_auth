from rest_framework import serializers
from users.models import NewUser
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class RegisterUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=68,
        write_only=True,
        validators = [validate_password],
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True
    )

    class Meta:
        model = NewUser
        fields = ('email', 'user_name', 'password', 'password2')
    
    def validate(self, instance):
        if instance['password'] != instance['password2']:
            raise serializers.ValidationError(
                {"password": 'Password fields didnt match'}
            )
        return instance
    
    def create(self, validated_data):
        return NewUser.objects.create_user(**validated_data)



class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=68, write_only=True)

    user_name = serializers.CharField(max_length=255, read_only=True)
    tokens = serializers.CharField(max_length=68, read_only = True)

    class Meta:
        model = NewUser
        fields = ['email', 'user_name', 'password', 'tokens']

    def validate(self, instance):
        email = instance.get('email','')
        password = instance.get('password','')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        

        return {
            'email' : user.email,
            'user_name' : user.user_name,
            'tokens' : user.tokens
        }
        


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, instance):
        self.token = instance['refresh']
        return instance

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')
