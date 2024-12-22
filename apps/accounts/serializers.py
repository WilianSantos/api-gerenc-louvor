from django.contrib.auth.models import User
from .models import Member, MemberFunction

from rest_framework import serializers


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        

class MemberFunctionSerializers(serializers.ModelSerializer):
    class Meta:
        model = MemberFunction
        fields = '__all__'