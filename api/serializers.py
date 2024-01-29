from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import *
from icecream import ic


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser', 'is_staff')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser',
            'is_staff', 'password')


class UserRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser', 'is_staff')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user
    

class VendeurRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser', 'is_staff', 'deletion_id',
            'deletion_type', 'created_by', 'is_archive', 'is_active')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.user_type = VENDEUR
        user.save()
        return user


class VisiteurRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser', 'is_staff', 'deletion_id',
            'deletion_type', 'created_by', 'is_archive', 'is_active')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.user_type = VISITEUR
        user.save()
        return user


class AdminUserSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        exclude = (
            'user_permissions', 'groups', 'is_superuser',
            'is_staff')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.user_type = ADMIN
        user.admin_type = ADMIN
        user.is_active = True
        user.save()
        return user
    

class AdminUserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        exclude = (
            'user_permissions', 'groups', 'is_superuser',
            'is_staff', 'password')


class ModePaiementSerializer(ModelSerializer):

    class Meta:
        model = ModePaiement
        fields = '__all__'


class PasswordResetSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    code = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RequestPasswordSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    email = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class LoginSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')


class SuppressionCompteSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('password',)


class AccountActivationSerializer(ModelSerializer):

    class Meta:
        model = AccountActivation
        fields = '__all__'


class CallbackPaymentSerializer(ModelSerializer):

    class Meta:
        model = CallbackPayment
        fields = '__all__'  


class NotificationSerializer(ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'


class NotificationGetSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ContactSerializer(ModelSerializer):

    class Meta:
        model = Contact
        fields = '__all__'


class ContactGetSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    responses = serializers.SerializerMethodField("get_responses")

    def get_responses(self, obj):
        return ResponseContactGetSerializer(ResponseContact.objects.filter(
            message=obj.id), many=True).data

    class Meta:
        model = Contact
        fields = '__all__'


class ResponseContactSerializer(ModelSerializer):

    class Meta:
        model = ResponseContact
        fields = '__all__'


class ResponseContactGetSerializer(ModelSerializer):
    message = ContactSerializer()
    user = UserGetSerializer()

    class Meta:
        model = ResponseContact
        fields = '__all__'


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'


class ForumSerializer(ModelSerializer):

    class Meta:
        model = Forum
        fields = '__all__'


class ForumGetSerializer(ModelSerializer):
    author = UserGetSerializer()
    theme = ThemeSerializer()
    comments = serializers.SerializerMethodField("get_comments")
    def get_comments(self, obj):
        return obj.comment_forum.count()
    
    class Meta:
        model = Forum
        fields = '__all__'


class ConversationSerializer(ModelSerializer):

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationGetSerializer(ModelSerializer):
    last_message = serializers.SerializerMethodField("get_last_message")
    messages_received_non_lus = serializers.SerializerMethodField("get_messages_received_non_lus")
    def get_last_message(self, obj):
        return MessageGetSerializer(obj.messages.last()).data

    def get_messages_received_non_lus(self, obj):
        user_slug = self.context.get("sender")
        return obj.messages.filter(read=False,receiver__slug=user_slug).count()

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationGetWebSerializer(ModelSerializer):
    participants = UserGetSerializer(many=True)
    messages = serializers.SerializerMethodField("get_messages")
    def get_messages(self, obj):
        return MessageGetSerializer(obj.messages.order_by('id')[:20], many=True ).data

    class Meta:
        model = Conversation
        fields = '__all__'



class MessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


class MessageGetSerializer(ModelSerializer):
    sender = UserGetSerializer()
    receiver = UserGetSerializer()
    conversation = ConversationSerializer()
    class Meta:
        model = Message
        fields = '__all__'


class ConversationWebPostGetSerializer(ModelSerializer):
    participants = UserGetSerializer(many=True)
    messages = serializers.SerializerMethodField("get_messages")
    def get_messages(self, obj):
        return MessageGetSerializer(obj.messages.order_by('id')[:20], many=True ).data

    class Meta:
        model = Conversation
        fields = '__all__'


class MessageGetPostSerializer(ModelSerializer):
    conversation = ConversationWebPostGetSerializer()
    class Meta:
        model = Message
        fields = '__all__'


class CommentForumSerializer(ModelSerializer):
    class Meta:
        model = CommentForum
        fields = '__all__'


class CommentForumGetSerializer(ModelSerializer):
    created_by = UserGetSerializer()
    forum = ForumSerializer()
    class Meta:
        model = CommentForum
        fields = '__all__'


class SignalementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Signalement
        fields = '__all__'


class SignalementGetSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()
    forum = ForumSerializer()
    comment = CommentForumSerializer()
    class Meta:
        model = Signalement
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Condition
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'


class BlockUserSerializer(ModelSerializer):
    causes = serializers.CharField()
    class Meta:
        model = User
        fields = '__all__'


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class CategorieSerializer(ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'


class ProduitSerializer(ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'


class ProduitGetSerializer(ModelSerializer):
    categorie = CategorieSerializer()
    images = ImageSerializer(many=True)
    class Meta:
        model = Produit
        fields = '__all__'


class VoucherSerializer(ModelSerializer):
    class Meta:
        model = Voucher
        fields = '__all__'