from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Course, Lesson, Video, Comment, LikeVideo, DislikeVideo, Follow


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'address', 'display_image')

    def display_image(self, obj):
        return format_html('<img src="{}" width="50px" height="50px"/>',
                           obj.img.url) if obj.img else None
    display_image.short_description = 'Image'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at', 'updated_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'course', 'created_at', 'updated_at')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'lesson', 'upload_date', 'display_video')

    def display_video(self, obj):
        return format_html('<video width="320" height="240" controls><source src="{}" type="video/mp4"></video>',
                           obj.video.url) if obj.video.url else None
    display_video.short_description = 'Video'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'video', 'created_at')


@admin.register(LikeVideo)
class LikeVideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'created_at')


@admin.register(DislikeVideo)
class DislikeVideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'created_at')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed_user', 'created_at')