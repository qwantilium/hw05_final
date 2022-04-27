# Generated by Django 2.2.6 on 2021-06-22 03:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст вашей публикации', verbose_name='Текст публикации')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')),
                ('author', models.ForeignKey(help_text='Автор этого комментария', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(blank=True, help_text='Пост над комментарием', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Пост комментария')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-created', 'text'],
            },
        ),
    ]