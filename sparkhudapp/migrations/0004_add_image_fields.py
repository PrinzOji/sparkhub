# Generated migration file for adding image fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkhudapp', '0003_post_video_alter_post_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='charityactivity',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='activity_images/'),
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='event_images/'),
        ),
    ]
