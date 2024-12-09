from django.db.models import Count

from .models import User, Post, Account,ProductPost

def load_user(params={}):
    q = User.objects.filter(active=True)

    keyword = params.get("keyword")
    if keyword:
        q = q.filter(username__icontains=keyword)

    return q

def load_account(params={}):
    q = Account.objects.filter(active=True)

    keyword = params.get("keyword")
    if keyword:
        q = q.filte(phone_number__icontains=keyword)

    role_id = params.get("role_id")
    if role_id:
        q = q.filter(role_id=role_id)


    return q


def load_productpost(params={}):
    q = ProductPost.objects.filter(active=True)

    keyword = params.get("keyword")
    if keyword:
        q = q.filter(productpost_content__icontains=keyword)

    return q

