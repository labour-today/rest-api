from rest_framework import serializers
from server.models import Labourer, Contractor
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(error_messages = {'required': 'Please enter your email address',})
    password = serializers.CharField(required = True, error_messages = {'required': 'Please enter a password'})
    first_name = serializers.CharField(required = True, error_messages = {'required': 'Please enter your first name'})
    last_name = serializers.CharField(required = True, error_messages = {'required': 'Please enter your last name'})

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
    
    def validate_username(self, value):
        try:
            User.objects.get(username = value)
            raise serializers.ValidationError('The username you specified is already taken. Please enter a different username')
        except User.DoesNotExist:
            return value

    def validate_email(self, value):
        try:
            User.objects.get(email = value)
            raise serializers.ValidationError('The email you specified is already in use. Please enter a different email address')
        except User.DoesNotExist:
            return value
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email')
        

class LabourerSerializer(serializers.ModelSerializer): 
    last_name = serializers.ReadOnlyField(source = 'user.last_name')
    first_name= serializers.ReadOnlyField(source = 'user.first_name')
    email = serializers.ReadOnlyField(source = 'user.email')
    username = serializers.ReadOnlyField(source = 'user.username')
    class Meta:
        model = Labourer
        fields = ('id', 'last_name', 'first_name', 'email', 'username', 'phone_number', 
                'address', 'sin', 'user', 'device',
                'carpentry', 'concrete_forming'
                )

class ContractorSerializer(serializers.ModelSerializer): 
    last_name = serializers.ReadOnlyField(source = 'user.last_name')
    first_name= serializers.ReadOnlyField(source = 'user.first_name')
    email = serializers.ReadOnlyField(source = 'user.email')
    username = serializers.ReadOnlyField(source = 'user.username')

    class Meta:
        model = Contractor
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'phone_number',
                'company_name', 'device', 'user'
                )
