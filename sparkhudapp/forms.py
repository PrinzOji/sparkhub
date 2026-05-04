from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, CharityActivity, Event, Post, Donation


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "bio", "profile_picture"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class CharityActivityForm(forms.ModelForm):
    class Meta:
        model = CharityActivity
        fields = ["description", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe your charity activity..."}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }
        labels = {
            "description": "Activity Description",
            "image": "Activity Image (Optional)",
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "event_date", "location", "required_points", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "event_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "video"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5, "placeholder": "Share your story..."}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
            "video": forms.FileInput(attrs={"accept": "video/*"}),
        }
        labels = {
            "content": "Post Content",
            "image": "Add Image (Optional)",
            "video": "Add Video (Optional)",
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["amount_kes", "message"]
        widgets = {
            "amount_kes": forms.NumberInput(attrs={"placeholder": "Enter amount in KES", "min": "1"}),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a message (optional)"}),
        }
        labels = {
            "amount_kes": "Donation Amount (KES)",
            "message": "Message",
        }
