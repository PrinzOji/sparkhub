from django.contrib import admin
from .models import UserProfile, CharityActivity, Event, EventRegistration, Donation, Post, Comment, Like

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'phone_number']
    search_fields = ['user__username', 'phone_number']
    list_filter = ['points']

@admin.register(CharityActivity)
class CharityActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'date_posted', 'points_earned']
    search_fields = ['user__username', 'description']
    list_filter = ['date_posted', 'points_earned']
    readonly_fields = ['date_posted']
    fieldsets = (
        ('Activity Information', {'fields': ('user', 'description', 'image')}),
        ('Points', {'fields': ('points_earned',)}),
        ('Timestamps', {'fields': ('date_posted',)}),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'location', 'required_points', 'created_at']
    search_fields = ['title', 'location', 'description']
    list_filter = ['event_date', 'required_points', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Event Details', {'fields': ('title', 'description', 'image')}),
        ('Event Info', {'fields': ('event_date', 'location', 'required_points')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registration_date', 'attended']
    search_fields = ['user__username', 'event__title']
    list_filter = ['attended', 'registration_date']
    readonly_fields = ['registration_date']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount_kes', 'date_donated', 'message']
    search_fields = ['user__username', 'message']
    list_filter = ['date_donated', 'amount_kes']
    readonly_fields = ['date_donated']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created_at', 'updated_at']
    search_fields = ['user__username', 'content']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Post Content', {'fields': ('user', 'content', 'image', 'video')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'content']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'post__id']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
