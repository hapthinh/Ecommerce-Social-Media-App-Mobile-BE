from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from . import dao
from .models import *
from .serializers import *
from .paginators import *
from .permisssions import *
from .decorators import *

# ====ROLE====

# ==== ROLE ====
class RoleViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

# ==== CONFIRM STATUS ====
class ConfirmStatusViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = ConfirmStatus.objects.all()
    serializer_class = ConfirmStatusSerializer

# ==== USER ====
@method_decorator(authorization, name='dispatch')
class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPageSize

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            queries = self.queryset
            for name_part in name.split():
                queries = queries.filter(Q(first_name__icontains=name_part) | Q(last_name__icontains=name_part))
            return queries
        return self.queryset

    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy', 'current_user', 'get_account_by_user_id', 'search_user', 'get_user_by_status']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=False, url_path='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='account')
    def get_account_by_user_id(self, request, pk):
        try:
            account = self.get_object().account
            return Response(AccountSerializer(account, context={'request': request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==== POST ====
@method_decorator(authorization, name='dispatch')
class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Post.objects.filter(active=True)
    serializer_class = PostSerializer
    pagination_class = MyPageSize

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [PostOwner()]
        if self.action in ['create_post_survey', 'create_post_invitation']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    @api_view(['POST'])
    def create_post(request):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            post = post_serializer.save()
            return Response({'id': post.id}, status=status.HTTP_201_CREATED)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==== REACTION ====
class ReactionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Reaction.objects.filter(active=True)
    serializer_class = ReactionSerializer
    pagination_class = MyPageSize

# ==== POST REACTION ====
@method_decorator(authorization, name='dispatch')
class PostReactionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PostReaction.objects.select_related('account', 'post', 'reaction').filter(active=True)
    serializer_class = PostReactionSerializer
    pagination_class = MyPageSize

    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return [PostReactionOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostReactionSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostReactionSerializer
        return self.serializer_class

# ==== ACCOUNT ====
@method_decorator(authorization, name='dispatch')
class AccountViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Account.objects.select_related('role', 'user').filter(active=True)
    serializer_class = AccountSerializer
    pagination_class = MyPageSize
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        phone_number = self.request.data.get('phone_number')
        if phone_number and Account.objects.filter(phone_number=phone_number).exists():
            return Response({'error': f'Số điện thoại đã tồn tại: {phone_number}'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.data.get('user')
        if user and Account.objects.filter(user=user).exists():
            return Response({'error': f'User đã tạo tài khoản: {user}'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        phone_number = self.request.data.get('phone_number')
        if phone_number and Account.objects.filter(phone_number=phone_number).exists():
            return Response({'error': f'Số điện thoại đã tồn tại: {phone_number}'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    @action(methods=['GET'], detail=False, url_path='current-account')
    def current_account(self, request):
        try:
            account = request.user.account
            serializer = AccountSerializer(account, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=False, url_path='current-product-posts')
    def get_current_posts(self, request):
        product_posts = request.user.account.productpost_set.filter(active=True).order_by('-created_date')
        paginator = MyPageSize()
        paginated = paginator.paginate_queryset(product_posts, request)
        serializer = ProductPostSerializer(paginated, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

@method_decorator(authorization, name='dispatch')
class CommentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True).all()
    serializer_class = CommentSerializer
    pagination_class = MyPageSize
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [CommentOwner()]
        elif self.action == 'destroy':
            return [CommentOwner()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCommentSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCommentSerializer
        return self.serializer_class

@method_decorator(decorator=authorization, name='dispatch')
class PostPollViewSet(viewsets.ModelViewSet):
    queryset = PostPoll.objects.all()
    serializer_class = PostPollSerializer

    @api_view(['POST'])
    def create_poll(request):
        poll_data = request.data
        print("data:", request.data)
        # Kiểm tra xem postId đã được cung cấp hay chưa
        if 'postId' not in poll_data:
            return Response({'error': 'postId is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo Poll mới
        poll_serializer = PostPollSerializer(data=poll_data)
        if poll_serializer.is_valid():
            poll = poll_serializer.save()
            return Response(PostPollSerializer(poll).data, status=status.HTTP_201_CREATED)

        return Response(poll_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(decorator=authorization, name='dispatch')
class PollResponseViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                          generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PollResponse.objects.all()
    serializer_class = PollResponseSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [PollResponseOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePollResponseSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePollResponseSerializer
        return self.serializer_class

@method_decorator(decorator=authorization, name='dispatch')
class PollOptionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                        generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PollOption.objects.all()
    serializer_class = PollOptionSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [PollOptionOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePollOptionSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePollOptionSerializer
        return self.serializer_class

#ANOTHER VIEW

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        print(f"Received Username: {username}, Password: {password}")

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(username=username)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'error': 'Invalid Credentials 222'}, status=status.HTTP_401_UNAUTHORIZED)
        except UserModel.DoesNotExist:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SignUpView(APIView):

    def post(self, request):
        print("Request data:", request.data)
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'id': user.id,
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CurrentAccountViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        account = Account.objects.get(user=request.user)
        serializer = CurrentAccountSerializer(account)
        return Response(serializer.data)

@method_decorator(decorator=authorization, name='dispatch')
class ProductPostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                  generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = ProductPost.objects.all()
    serializer_class = ProductPostSerializer2

    def get_permissions(self):
        if self.action in ['update','partial_update', 'destroy']:
            return [PostOwner()]
        else :
            return [permissions.IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)

        # Lấy dữ liệu từ request
        product_data = request.data.get('product', {})
        account_data = request.data.get('account', {})

        print("Account data:", account_data)
        print("Product data before modification:", product_data)

        if isinstance(account_data, dict) and account_data.get('id'):
            owner_id = account_data['id']  # Lưu ID vào biến owner_id
        else:
            return Response({"error": "Account ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        product_data['owner'] = owner_id

        print("Product data after adding owner:", product_data)

        # Tạo sản phẩm
        product_serializer = ProductSerializerForPost(data=product_data)
        product_serializer.is_valid(raise_exception=True)

        # Lưu sản phẩm
        product = product_serializer.save()

        post_data = request.data.copy()
        post_data['product'] = {
            "id": product.id,  # Gán ID của sản phẩm vào post_data như một dictionary
            "product_name": product.product_name,
            "description": product.description,
            "price": product.price,
            "category": {
                "category_name": product.category.category_name
            }
        }

        # Kiểm tra xem post_data có trường account không
        if isinstance(account_data, dict) and account_data.get('id'):
            post_data['account'] = account_data['id']  # Gán ID của account vào post_data

        post_serializer = self.get_serializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post_serializer.save()  # Lưu bài viết

        # Trả về phản hồi thành công
        return Response(post_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @api_view(['GET'])
    def get_post_by_id(request, post_id):
        print("Request ", request)
        try:
            post = ProductPost.objects.get(id=post_id)
            serializer = ProductPostSerializer(post)
            print(serializer.data)
            return Response(serializer.data)
        except ProductPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class GetPostsByCategoryView(APIView):
    def get(self, request, category_id):
        productposts = ProductPost.objects.filter(product__category_id=category_id)
        serializer = ProductPostSerializer(productposts, many=True)
        return Response(serializer.data)

class PostListView(APIView):
    serializer_class = ProductPostSerializer
    pagination_class = MyPageSize

    def get_queryset(self):
        return ProductPost.objects.all().order_by('-created_date')

    def get(self, request, *args, **kwargs):
        print("Request2 ", request)
        product_post_id = kwargs.get('product_post_id', None)
        if product_post_id:
            try:
                post = self.get_queryset().get(id=product_post_id)
                serializer = self.serializer_class(post)
                return Response(serializer.data)
            except ProductPost.DoesNotExist:
                return Response({"detail": "ProductPost not found"}, status=status.HTTP_404_NOT_FOUND)

        paginator = self.pagination_class()
        queryset = self.get_queryset()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        print(serializer.data)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        print("Request data:", request.data)  # In dữ liệu gửi lên để kiểm tra
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)  # In lỗi nếu serializer không hợp lệ
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, post_id):
        account_id = request.data.get("account", {}).get("id")
        print(account_id)

        return self.toggle_like(request, post_id, account_id)

    def toggle_like(self, request, post_id, account_id):

        existing_reaction = ProductPostReaction.objects.filter(
            product_post_id=post_id,
            account_id=account_id
        ).first()

        if existing_reaction:
            if existing_reaction.reaction_id == 1:
                existing_reaction.reaction_id = 2
                existing_reaction.save()
                return Response({"detail": "Unliked"}, status=status.HTTP_200_OK)
            else:
                existing_reaction.reaction_id = 1
                existing_reaction.save()
                return Response({"detail": "Liked"}, status=status.HTTP_200_OK)
        else:
            reaction = ProductPostReaction.objects.create(
                product_post_id=post_id,
                account_id=account_id,
                reaction_id=1
            )
            serializer = ProductPostReactionSerializer(reaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def add_comment(request, post_id):
        post = ProductPost.objects.get(id=post_id)

        comment_content = request.data.get("comment_content")

        if not comment_content:
            return Response({"comment_content": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "comment_content": comment_content,
            "post": post.id,
            "account": request.user.account.id
        }

        serializer = CommentSerializerForPost(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    def get_post_by_id(request, post_id):
        print("Request ", request)
        try:
            post = ProductPost.objects.get(id=post_id)
            serializer = ProductPostSerializer(post)
            print(serializer.data)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProductPostStatisticsView(APIView):
    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if month and year:
            statistics = ProductPost.objects.filter(
                created_date__month=month,
                created_date__year=year
            ).annotate(
                month=ExtractMonth('created_date'),
                year=ExtractYear('created_date')
            ).values('month', 'year').annotate(productpost_count=Count('id'))

        else:
            statistics = ProductPost.objects.annotate(
                month=ExtractMonth('created_date'),
                year=ExtractYear('created_date')
            ).values('month', 'year').annotate(productpost_count=Count('id'))

        return Response(statistics)
