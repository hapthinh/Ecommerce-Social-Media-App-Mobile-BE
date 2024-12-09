from rest_framework import permissions

class CommentOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, comment):
        if view.action == 'destroy':
            return request.user == comment.post.account.user \
                   or request.user == comment.account.user \
                   or request.user.account.role.role_name == 'Admin'
        elif view.action in ['update', 'partial_update']:
            return request.user == comment.account.user

class PostOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, post):
        if view.action == 'destroy':
            return request.user == post.account.user \
                   or request.user.account.role.role_name == 'Admin'
        elif view.action in ['update', 'partial_update']:
            return request.user == post.account.user

class PostOwnerAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, post):
        return request.user == post.account.user


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.account.role.role_name == 'Admin'


class PostReactionOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, post_reaction):
        return request.user == post_reaction.account.user

class PollResponseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

class PollOptionOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner

class IsPollAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class PostPollOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner

class PollResponseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

class PollOptionOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner