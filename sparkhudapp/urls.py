from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('post-activity/', views.post_charity_activity, name='post_activity'),
    path('donate/', views.donate, name='donate'),
    path('events/', views.events, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('register-event/<int:event_id>/', views.register_for_event, name='register_event'),
    path('social-feed/', views.social_feed, name='social_feed'),
    path('create-post/', views.create_post, name='create_post'),
    path('settings/', views.settings, name='settings'),
    path('settings/edit-profile/', views.edit_profile, name='edit_profile'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('settings/two-factor/', views.two_factor, name='two_factor'),
    path('settings/email-preferences/', views.email_preferences, name='email_preferences'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/privacy/', views.privacy_settings, name='privacy_settings'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('like-post/', views.like_post, name='like_post'),
    path('comment-post/', views.comment_post, name='comment_post'),
    path('process-donation/', views.process_donation, name='process_donation'),
]
