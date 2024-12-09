from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register('roles', RoleViewSet, basename='roles')

router.register('confirm_status', ConfirmStatusViewSet, basename='confirm_status')

router.register('users', UserViewSet, basename='users')

router.register('posts', PostViewSet, basename='posts')

router.register('reactions', ReactionViewSet, basename='reactions')

router.register('post_reactions', PostReactionViewSet, basename='post_reactions')

router.register('accounts', AccountViewSet, basename='accounts')

router.register('comment', CommentViewSet, basename='comment')

router.register('categories', CategoryViewSet, basename='categories')

router.register('product-posts', ProductPostViewSet, basename='product-posts')

router.register(r'polls', PostPollViewSet)

router.register(r'poll-options', PollOptionViewSet)

router.register(r'poll-responses', PollResponseViewSet)

app_name = 'app'
urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('accounts/current-product-posts/', AccountViewSet.as_view({'get': 'get_current_product_posts'}),
         name='current-product-posts'),
    path('accounts/current-account/', CurrentAccountViewSet.as_view({'get': 'retrieve'}), name='current-account'),
    path('categories/get-posts-by-categories/<int:category_id>/', GetPostsByCategoryView.as_view()),
    path('new-feeds/', PostListView.as_view(), name='post-list'),
    path('product-posts/<int:post_id>/like/', PostListView.as_view(), name='toggle-like'),
    path('product-posts/<int:post_id>/', PostListView.get_post_by_id, name='get_post_by_id'),
    path('product-posts/detail/<int:product_post_id>/', PostListView.as_view(), name='product-post-detail'),
    path('product-posts/<int:post_id>/comments/', PostListView.add_comment),
    path('posts/', PostViewSet.as_view({'create':'create_post'}), name='create_post'),
    path('polls/', PostPollViewSet.as_view({'create':'create_poll'}), name='create_poll'),
    path('productposts/statistics/', ProductPostStatisticsView.as_view(), name='productpost-statistics'),
]
