from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdmin, IsManager


class GroupUsersView(APIView):
    permission_classes = [IsAdmin]
    group_name = 'Manager'

    def get_permission(self):
        return IsAdmin() if self.group_name == 'Manager' else IsManager()

    def get_permissions(self):
        return [self.get_permission()]

    def get(self, request):
        group = Group.objects.get(name=self.group_name)
        return Response(list(group.user_set.values('id', 'username', 'email')))

    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'detail': 'username is required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        group = Group.objects.get(name=self.group_name)
        user.groups.add(group)
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.groups.remove(Group.objects.get(name=self.group_name))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerUsersView(GroupUsersView):
    group_name = 'Manager'


class DeliveryCrewUsersView(GroupUsersView):
    group_name = 'DeliveryCrew'
