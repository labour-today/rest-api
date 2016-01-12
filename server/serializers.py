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
            raise serializers.ValidationError('The email you entered is already in use. Enter another.')
        except User.DoesNotExist:
            return value
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password')
        

class LabourerSerializer(serializers.ModelSerializer): 
    last_name = serializers.ReadOnlyField(source = 'user.last_name')
    first_name= serializers.ReadOnlyField(source = 'user.first_name')
    username = serializers.ReadOnlyField(source = 'user.username')
    class Meta:
        model = Labourer
        fields = ('id', 'last_name', 'first_name', 'available', 'username', 'phone_number', 
                'address', 'sin', 'user', 'device', 'rating',
                'carpentry', 'concrete_forming', 'general_labour'
                )

class ContractorSerializer(serializers.ModelSerializer): 
    last_name = serializers.ReadOnlyField(source = 'user.last_name')
    first_name= serializers.ReadOnlyField(source = 'user.first_name')
    username = serializers.ReadOnlyField(source = 'user.username')

    class Meta:
        model = Contractor
        fields = ('id', 'first_name', 'last_name', 'username', 'phone_number',
                'company_name', 'device', 'user', 'customer_id'
                )
