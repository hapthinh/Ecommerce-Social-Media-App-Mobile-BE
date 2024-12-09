from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

class EcommerceSocialMediaAppAdminSite(admin.AdminSite):
    site_header = "MXH TMDT"

my_admin_site = EcommerceSocialMediaAppAdminSite(name='ThinhAdmin')

class RoleAdmin(admin.ModelAdmin):
    pass

class ConfirmStatusAdmin(admin.ModelAdmin):
    pass

class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username','confirm_status']
    search_fields = ['username']
    list_filter = ['confirm_status']

class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'role', 'user', 'account_status']
    search_fields = ['phone_number']
    list_filter = ['role_id', 'account_status']
    readonly_fields = ['show_avatar']

    @staticmethod
    def show_avatar(account):
        if account:
            return mark_safe(
                '<img src="/static/{url}" width="120" />'.format(url=account.avatar.name)
            )


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_content', 'account']
    search_fields = ['post_content', 'account']

class ReactionAdmin(admin.ModelAdmin):
    list_filter = ['reaction_name']


class PostReactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_id', 'post', 'reaction', 'account']


class PostImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_image_url']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_id', 'comment_content', 'comment_image_url', 'post_id']
    search_fields = ['comment_content']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','product_name']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','category_name']

class PollAdmin(admin.ModelAdmin):
    pass

class PollOptionAdmin(admin.ModelAdmin):
    pass

class PollResponseAdmin(admin.ModelAdmin):
    pass

class RoomAdmin(admin.ModelAdmin):
    pass

class MessageAdmin(admin.ModelAdmin):
    pass

my_admin_site.register(Role, RoleAdmin)
my_admin_site.register(ConfirmStatus, ConfirmStatusAdmin)
my_admin_site.register(User, UserAdmin)
my_admin_site.register(Account, AccountAdmin)
my_admin_site.register(Post, PostAdmin)
my_admin_site.register(Reaction, ReactionAdmin)
my_admin_site.register(PostReaction, PostReactionAdmin)
my_admin_site.register(Comment, CommentAdmin)
my_admin_site.register(PostPoll,PollAdmin)
my_admin_site.register(PollOption,PollOptionAdmin)
my_admin_site.register(PollResponse,PollResponseAdmin)