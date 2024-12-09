from rest_framework import serializers

from .models import *

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ConfirmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmStatus
        fields = '__all__'

# ====USER====
class CreateUserSerializer(serializers.ModelSerializer):
    id  = serializers.IntegerField(source='pk',read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.confirm_status_id = 1
        user.save()
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',read_only=True)

    class Meta:
        model = User
        fields = ['id','password','first_name','last_name','email','confirm_status']

    def update(self, instance, validate_data):
        password = validate_data.copy('password', None);
        if password:
            instance.set_password(password)
        return super().update(instance, validate_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']
        extra_kwargs = { 'password' : { 'write_only' : True}}

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class UserSerializerForSearch(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']

class UserSerializerForComment(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

# ====ACCOUNT====

class AccountSerializerForUser(serializers.ModelSerializer):
    user = UserSerializerForSearch()
    role = RoleSerializer()

    avatar = serializers.SerializerMethodField(source='avatar')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role'] = str(representation['role']['id']) +'/'+representation['role']['role_name']
        return representation

    @staticmethod
    def get_avatar(account):
        if account.avatar:
            return account.avatar.name

    class Meta:
        model = Account
        fields = ['user', 'avatar', 'phone_number','role']

class AccountSerializerForComment(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(source='avatar')

    @staticmethod
    def get_avatar(account):
        if account.avatar:
            return account.avatar.name

    @staticmethod
    def get_user(account):
        return UserSerializerForComment(account.user).data

    class Meta:
        model = Account
        fields = '__all__'

class AccountSerializerForComment2(serializers.ModelSerializer):
    user = UserSerializerForComment()
    avatar = serializers.SerializerMethodField(source='avatar')

    @staticmethod
    def get_avatar(account):
        if account.avatar:
            return account.avatar.name

    # def get_avatar(self, account):
    #     if account.avatar:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri('/static/%s' % account.avatar.name)
    #     return '/static/%s' % account.avatar.name

    class Meta:
        model = Account
        fields = ['id', 'user', 'role', 'avatar']


# ====POST====

class CreatePostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Post
        fields = ['id','post_content', 'account']

class UpdatePostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'post_content', 'comment_lock']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostSerializerForList(serializers.ModelSerializer):
    account = AccountSerializerForComment()

    class Meta:
        model = Post
        fields = '__all__'



class CommentSerializerForPost(serializers.ModelSerializer):
    account = AccountSerializerForComment(read_only=True)  # Để field này chỉ có thể đọc
 # Trả về None nếu không có hình ảnh

    class Meta:
        model = Comment
        fields = ['comment_content','account']

    def create(self, validated_data):
        # Lấy account từ request.user
        account_instance = self.context['request'].user.account

        # Lấy ID của post từ validated_data
        post_id = self.context['request'].parser_context['kwargs']['post_id']
        post_instance = ProductPost.objects.get(id=post_id)

        # Tạo comment với account instance và post instance
        comment = Comment.objects.create(account=account_instance, post=post_instance, **validated_data)
        return comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_name']

class UserSerializerForPostProduct(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class AccountSerializerForPostProduct(serializers.ModelSerializer):
    user = UserSerializerForPostProduct()

    class Meta:
        model = Account
        fields = ['id','user']



class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'description', 'price','category']


class ProductSerializerForPost(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'category']

    def create(self, validated_data):
        # Lấy category từ validated_data
        category_data = validated_data.pop('category')
        category_name = category_data.get('category_name')
        print("request2: ", category_data)
        print("request3: ", category_name)

        # Tìm kiếm danh mục theo category_name
        try:
            category = Category.objects.get(category_name=category_name)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category": "Category with this name does not exist."})

        # Gán owner từ validated_data
        owner = validated_data.pop('owner', None)  # Lấy owner từ validated_data
        print("request4: ", owner)

        # Tạo sản phẩm với danh mục đã tồn tại và owner
        product = Product.objects.create(category=category, owner=owner, **validated_data)
        return product

class ProductPostSerializer2(serializers.ModelSerializer):
    product = ProductSerializerForPost()
    class Meta:
        model = ProductPost
        fields = ['post_content', 'account', 'product']

    def create(self, validated_data):
        product_data = validated_data.pop('product')
        product_serializer = ProductSerializerForPost(data=product_data)

        if product_serializer.is_valid(raise_exception=True):
            product = product_serializer.save()  # Lưu product sau khi xử lý category

            # Tạo bài viết (ProductPost) với sản phẩm đã có
            return ProductPost.objects.create(product=product, **validated_data)
        else:
            raise serializers.ValidationError(product_serializer.errors)


# ====REACTION====

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'


# ====POST-REACTION====
class AccountSerializerForPostReaction(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id','user','role']

    def get_role(self, obj):
        return RoleSerializer(obj.role).data['role_name']

    def get_user(self, obj):
        return 'id:' + str(UserSerializer(obj.user).data['id']) + '/username:' + UserSerializer(obj.user).data['username']

class ReactionSerializerForPostReaction(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['id','reaction_name']

class PostSerializerForPostReaction(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','post_content']

class CreatePostReactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PostReaction
        fields = ['id','reaction','post','account']

class UpdatePostReactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PostReaction
        fields = ['id', 'reaction', 'post']

class PostReactionSerializer(serializers.ModelSerializer):
    account = AccountSerializerForPostReaction()
    reaction = ReactionSerializerForPostReaction()
    post = PostSerializerForPostReaction()

    class Meta:
        model = PostReaction
        fields = '__all__'

class TempSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id']

class AccountSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(source='avatar')
    role = RoleSerializer()
    user = UserSerializer()

    @staticmethod
    def get_avatar(account):
        if account.avatar:
            return account.avatar.name

    class Meta:
        model = Account
        fields = '__all__'


# ====PRODUCT-POST-REACTION====

class ProductPostReactionSerializer(serializers.ModelSerializer):
    account = AccountSerializerForPostProduct()
    reaction = ReactionSerializerForPostReaction()

    class Meta:
        model = ProductPostReaction
        fields = '__all__'
class CommentSerializerForPostProduct(serializers.ModelSerializer):
    comment_image_url = serializers.SerializerMethodField(source='comment_image_url')
    account = AccountSerializerForComment2()

    @staticmethod
    def get_comment_image_url(comment):
        if comment.comment_image_url:
            return comment.comment_image_url.name

    @staticmethod
    def get_user(account):
        return UserSerializerForComment(account.user).data

    class Meta:
        model = Comment
        fields = '__all__'


class PostProductPostSerializer(serializers.ModelSerializer):
    account = AccountSerializerForPostProduct()
    product = ProductSerializer()

    class Meta:
        model = ProductPost
        fields = ['id', 'post_content', 'account', 'product', 'created_date', 'updated_date', 'deleted_date', 'active']

    def validate_account(self, value):
        try:
            account = Account.objects.get(id=value['id'])
            return account
        except Account.DoesNotExist:
            raise serializers.ValidationError("Account not found.")


class ProductPostSerializer(serializers.ModelSerializer):
    account = AccountSerializerForPostProduct()
    product = ProductSerializer()
    comment = serializers.SerializerMethodField()
    reaction = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductPost
        fields = ['id', 'created_date', 'updated_date', 'deleted_date', 'active', 'post_content', 'account', 'product', 'comment', 'reaction','reaction_count','comment_count']

    def get_comment(self, obj):
        return CommentSerializerForPostProduct(obj.comment_set.all(), many=True).data

    def get_reaction(self, obj):
        return ProductPostReactionSerializer(obj.productpostreaction_set.all(), many=True).data

    def get_reaction_count(self, obj):
        return obj.productpostreaction_set.count()

    def get_comment_count(self, obj):
        return obj.comment_set.count()

    def add_reaction(self, post_id, account_id, reaction_name):
        reaction = Reaction.objects.create(reaction_name=reaction_name, account_id=account_id, post_id=post_id)
        return reaction

    def remove_reaction(self, post_id, account_id, reaction_name):
        Reaction.objects.filter(post_id=post_id, account_id=account_id, reaction_name=reaction_name).delete()

    def create(self, validated_data):
        # Xử lý tài khoản và sản phẩm từ validated_data
        account_data = validated_data.pop('account')
        product_data = validated_data.pop('product')

        # Lấy tài khoản và sản phẩm đã có từ ID
        account = Account.objects.get(id=account_data['id'])
        product = Product.objects.get(id=product_data['id'])

        # Tạo sản phẩm mới
        product_post = ProductPost.objects.create(account=account, product=product, **validated_data)
        return product_post

# ====ACCOUNT====

class CreateAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    date_of_birth = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Account
        fields = ['id', 'phone_number', 'gender', 'date_of_birth', 'avatar','account_status', 'user',
                  'role']

class UpdateAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'phone_number', 'date_of_birth', 'avatar', 'account_status', 'role']



class PostReactionSerializerForAccount(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['reaction_id']


# ====COMMENT====

class CreateCommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment_content', 'comment_image_url', 'account', 'post']


class UpdateCommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment_content', 'comment_image_url']


class CommentSerializer(serializers.ModelSerializer):
    comment_image_url = serializers.SerializerMethodField(source='comment_image_url')

    @staticmethod
    def get_comment_image_url(comment):
        if comment.comment_image_url:
            return comment.comment_image_url.name

    class Meta:
        model = Comment
        fields = '__all__'

# ====POLL====

class CreatePostPollSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PostPoll
        fields = ['id','title', 'start_time', 'end_time', 'post']

class UpdatePostPollSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PostPoll
        fields =  ['title', 'start_time', 'end_time', 'post']

class PostPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPoll
        fields = '__all__'

# ====POLL-OPTION====

class CreatePollOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PollOption
        fields = ['id', 'option_text', 'poll']

class UpdatePollOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PollOption
        fields = ['id', 'option_text']

class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = '__all__'

# ====POLL-RESPONSE====

class CreatePollResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = PollResponse
        fields = ['id', 'poll_option', 'account']

class PollResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollResponse
        fields = '__all__'

class UpdatePollResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollResponse
        fields = '__all__'

# ====ROOM-CHAT====

class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['first_user', 'second_user']


class UpdateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['seen']


class RoomSerializer(serializers.ModelSerializer):
    first_user = AccountSerializerForComment()
    second_user = AccountSerializerForComment()

    class Meta:
        model = Room
        fields = '__all__'

# ====MESSAGE====

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class CurrentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'user','role']


class ProductPostStatisticSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    post_count = serializers.IntegerField()
