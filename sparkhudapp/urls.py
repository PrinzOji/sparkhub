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
    path('like-post/', views.like_post, name='like_post'),
    path('comment-post/', views.comment_post, name='comment_post'),
]
