from rest_framework.permissions import BasePermission


def in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or in_group(request.user, 'Admin'))


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or in_group(request.user, 'Admin') or in_group(request.user, 'Manager')
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return in_group(request.user, 'Manager') or request.user.is_superuser


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return in_group(request.user, 'DeliveryCrew')


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not (
            request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Manager', 'DeliveryCrew']).exists()
        )