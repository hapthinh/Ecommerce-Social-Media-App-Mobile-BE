from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from ckeditor.fields import RichTextField



class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    deleted_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-id']


class Role(BaseModel):
    role_name = models.CharField(max_length=255)

    def __str__(self):
        return self.role_name


class ConfirmStatus(BaseModel):
    confirm_status_value = models.CharField(max_length=255)

    def __str__(self):
        return self.confirm_status_value


class User(AbstractUser):
    confirm_status = models.ForeignKey(ConfirmStatus, on_delete=models.CASCADE, default=3)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.username


class Account(BaseModel):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=255, unique=True, null=True)
    date_of_birth = models.DateField(null=True)
    avatar = models.ImageField(upload_to="images/accounts/avatar/%Y/%m", null=True, blank=True)
    account_status = models.BooleanField(default=False)
    gender = models.BooleanField(default=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=3)

    def __str__(self):
        return self.user.username

class Category(BaseModel):
    category_name = models.TextField()

class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

class PostBase(BaseModel):
    post_content = RichTextField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.post_content

class Post(PostBase):
    pass
    def __str__(self):
        return self.post_content

class Reaction(BaseModel):
    reaction_name = models.CharField(max_length=255)

    def __str__(self):
        return self.reaction_name


class ReactionBase(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class PostReaction(ReactionBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class ProductPost(PostBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    post_image_url = models.ImageField(upload_to="images/product_post_images/%Y/%m", null=True, blank=True)

class ProductPostReaction(ReactionBase):
    product_post = models.ForeignKey(ProductPost, on_delete=models.CASCADE)

    @property
    def reactions(self):
        return self.productpostreaction_set.all()

class Comment(BaseModel):
    comment_content = models.TextField()
    comment_image_url = models.ImageField(upload_to="images/comments/%Y/%m", null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(ProductPost, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_content

class PostPoll(BaseModel):
    title = models.CharField(max_length=255)
    start_time = models.DateField()
    end_time = models.DateField()
    is_closed = models.BooleanField(default=False)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class PollOption(BaseModel):
    poll = models.ForeignKey(PostPoll, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.option_text

class PollResponse(BaseModel):
    poll = models.ForeignKey(PostPoll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account.user.username} voted for {self.option.option_text} in poll {self.poll.title}"

class Room(BaseModel):
    first_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='first_user_room', null=True)
    second_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='second_user_room', null=True)
    received_message_date = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)

    class Meta:
        unique_together = ['first_user', 'second_user']

    def __str__(self):
        return str(self.first_user.id) + str(self.second_user.id)


class Message(BaseModel):
    who_sent = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=10000)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content
