from rest_framework import serializers
from home.models import BlogModel, transfer
from userauths.models import User


# ---------------------------- Blog ----------------------------
class BlogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlogModel
        fields = ['id', 'title', 'slug', 'content', 'user', 'image', 'created_at', 'upload_to']


# ---------------------------- Transfer ----------------------------
class TransferSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = transfer
        fields = ['id', 'title', 'slug', 'content', 'user', 'image', 'created_at', 'upload_to']



# ===============================================================
#         UPDATED USER REGISTRATION SERIALIZER (CORRECT)
# ===============================================================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password2",
            "bio",
            "phone",
            "state",
            "country",
        ]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")

        # create user with your custom model fields
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            bio=validated_data.get("bio", ""),
            phone=validated_data.get("phone", ""),
            state=validated_data.get("state", None),
            country=validated_data.get("country", None),
        )
        return user



# ===============================================================
#                 OPTIONAL: USER LOGIN SERIALIZER
# ===============================================================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
