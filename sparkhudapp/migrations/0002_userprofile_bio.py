from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkhudapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
    ]
