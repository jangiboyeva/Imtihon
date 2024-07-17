from rest_framework import viewsets, status, permissions, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .models import UserProfile, Course, Lesson, Video, Comment, LikeVideo, DislikeVideo, Follow
from .serializers import (UserSerializer, UserProfileSerializer, CourseSerializer, LessonSerializer, VideoSerializer,
                          CommentSerializer, LikeVideoSerializer, DislikeVideoSerializer, FollowSerializer,
                          UserRegistrationSerializer, SendMailSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        UserProfile.objects.create(user=user)

        emails = [user.email]
        subject = "Hush kelibsiz online kurs dunyosiga"
        message = f"Salom {user.username}, bizning sajifamizda ro'yxatdan o'tganingizdan hursandmiz"

        """Emailga ro'yxatdan o'tkanligi haqida ma'lumot jo'natish uchun"""
        send_mail_to_email(emails, subject, message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update this profile'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to delete this profile'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        courses = Course.objects.filter(author=instance.user)
        lessons = Lesson.objects.filter(author=instance.user)
        videos = Video.objects.filter(author=instance.user)
        comments = Comment.objects.filter(author=instance.user)
        likes = LikeVideo.objects.filter(user=instance.user).count()
        dislikes = DislikeVideo.objects.filter(user=instance.user).count()
        followers = Follow.objects.filter(followed_user=instance.user)

        course_serializer = CourseSerializer(courses, many=True)
        lesson_serializer = LessonSerializer(lessons, many=True)
        video_serializer = VideoSerializer(videos, many=True)
        comment_serializer = CommentSerializer(comments, many=True)

        followers_data = [{'username': follower.follower.username} for follower in followers]

        data = {
            'profile': UserProfileSerializer(instance).data,
            'courses': course_serializer.data,
            'lessons': lesson_serializer.data,
            'videos': video_serializer.data,
            'comments': comment_serializer.data,
            'likes': likes,
            'dislikes': dislikes,
            'followers_count': followers.count(),
            'followers': followers_data,
        }

        return Response(data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.author == request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update this course'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.author == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to delete this course'}, status=status.HTTP_403_FORBIDDEN)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = Course.objects.get(pk=course_id)
        if request.user.is_superuser or course.author == request.user:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            emails = []
            for follow in Follow.objects.filter(followed_user=course.author):
                emails.append(follow.follower.email)


            subject = "Siz obuna bo'lgan foydalanuvchi yangi dars qo'shdi"
            message = (f'Foydalnuvchi usernami: {course.author.username}, emaili: {course.author.email},\n '
                       f'lesson nomi: {serializer.data["title"]}')
            send_mail_to_email(emails, subject, message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'You are not allowed to create a lesson for this course'},
                            status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.course.author == request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update this lesson'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.course.author == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to delete this lesson'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        videos = Video.objects.filter(lesson=instance)
        video_serializer = VideoSerializer(videos, many=True)

        data = {
            'lesson': LessonSerializer(instance).data,
            'videos_count': videos.count(),
            'videos': video_serializer.data,
        }

        return Response(data)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def create(self, request, *args, **kwargs):
        lesson_id = request.data.get('lesson')
        lesson = Lesson.objects.get(pk=lesson_id)
        if request.user.is_superuser or lesson.course.author == request.user:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            emails = []
            for follow in Follow.objects.filter(followed_user=lesson.author):
                emails.append(follow.follower.email)


            subject = "Siz obuna bo'lgan odam yangi video qo'shdi"
            message = (f"Username: {lesson.author.username}, email: {lesson.author.email}n/"
                       f"Lesson nomi: {lesson.title}n/"
                       f"Vaqti: {lesson.updated_at}")

            send_mail_to_email(emails, subject, message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'You are not allowed to create a video for this lesson'},
                            status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()


        if request.user.is_superuser or instance.lesson.course.author == request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update this video'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()


        if request.user.is_superuser or instance.lesson.course.author == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to delete this video'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):


        instance = self.get_object()

        likes = LikeVideo.objects.filter(video=instance)
        dislikes = DislikeVideo.objects.filter(video=instance)
        comments = Comment.objects.filter(video=instance)

        like_serializer = LikeVideoSerializer(likes, many=True)
        dislike_serializer = DislikeVideoSerializer(dislikes, many=True)
        comment_serializer = CommentSerializer(comments, many=True)

        data = {
            'video': VideoSerializer(instance).data,
            'likes_count': likes.count(),
            'likes': like_serializer.data,
            'dislikes_count': dislikes.count(),
            'dislikes': dislike_serializer.data,
            'comments': comment_serializer.data,
        }

        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        if request.user == instance.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update this comment'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        if request.user == instance.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to delete this comment'}, status=status.HTTP_403_FORBIDDEN)


class LikeVideoViewSet(viewsets.ModelViewSet):
    queryset = LikeVideo.objects.all()
    serializer_class = LikeVideoSerializer


    def create(self, request, *args, **kwargs):
        video_id = request.data.get('video')
        existing_dislike = DislikeVideo.objects.filter(video=video_id, user=request.user).first()


        if existing_dislike:
            existing_dislike.delete()
        existing_like = LikeVideo.objects.filter(video=video_id, user=request.user).first()

        if existing_like:
            existing_like.delete()
            return Response({'message': 'Like removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DislikeVideoViewSet(viewsets.ModelViewSet):
    queryset = DislikeVideo.objects.all()
    serializer_class = DislikeVideoSerializer

    def create(self, request, *args, **kwargs):
        video_id = request.data.get('video')
        existing_like = LikeVideo.objects.filter(video=video_id, user=request.user).first()


        if existing_like:
            existing_like.delete()
        existing_dislike = DislikeVideo.objects.filter(video=video_id, user=request.user).first()

        if existing_dislike:
            existing_dislike.delete()
            return Response({'message': 'Dislike removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed_user')
        existing_follow = Follow.objects.filter(followed_user_id=followed_user_id, follower=request.user).first()

        if existing_follow:
            return Response({'message': 'You are already following this user'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(follower=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):


        instance = self.get_object()
        if instance.follower == request.user:
            instance.delete()
            return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not allowed to unfollow this user'}, status=status.HTTP_403_FORBIDDEN)


class SendNotificationAPIView(APIView):


    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = SendMailSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = SendMailSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']

            emails = list(User.objects.values_list('email', flat=True))

            send_mail_to_email(emails, subject, message)


            return Response({'message': 'Notification sent'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchView(APIView):

    def get(self, request):
        query = request.GET.get('q', '')
        courses = Course.objects.filter(name__icontains=query)
        lessons = Lesson.objects.filter(title__icontains=query)
        videos = Video.objects.filter(title__icontains=query)

        course_serializer = CourseSerializer(courses, many=True)
        lesson_serializer = LessonSerializer(lessons, many=True)
        video_serializer = VideoSerializer(videos, many=True)

        return Response({
            'courses': course_serializer.data,
            'lessons': lesson_serializer.data,
            'videos': video_serializer.data,
        })


def send_mail_to_email(recive_emails: list, subject: str, message: str):

    email_from = settings.EMAIL_HOST_USER
    recipient_list = recive_emails
    send_mail(subject, message, email_from, recipient_list)
