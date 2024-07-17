from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile, Course, Lesson, Video, Comment, LikeVideo, DislikeVideo, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['user', 'img', 'fullname', 'address']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'author', 'name', 'description', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'author', 'course', 'title', 'content', 'created_at', 'updated_at']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'lesson', 'author', 'title', 'description', 'video', 'upload_date']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'video', 'author', 'content', 'created_at']


class LikeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeVideo
        fields = ['id', 'video', 'user', 'created_at']


class DislikeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DislikeVideo
        fields = ['id', 'video', 'user', 'created_at']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed_user', 'created_at']


class SendMailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=250, help_text="Message title")
    message = serializers.CharField(help_text="Message text")