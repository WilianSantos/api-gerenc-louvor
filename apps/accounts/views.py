from rest_framework import viewsets

from django.contrib.auth.models import User

from .serializers import UserSerializers, MemberSerializers, MemberFunctionSerializers
from .models import Member, MemberFunction


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializers


class MemberFunctionViewSet(viewsets.ModelViewSet):
    queryset = MemberFunction.objects.all()
    serializer_class = MemberFunctionSerializers
