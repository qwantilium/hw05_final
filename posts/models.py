from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название',
                             help_text='Название группы',)
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес для группы',
                            help_text='Укажите адрес для страницы задачи.'
                            ' Используйте только'
                            'латиницу, цифры, дефисы и знаки подчёркивания',)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Описание группы', )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Текст вашей публикации')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='Автор',
                               help_text='Автор этой публикации',
                               related_name='posts')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              verbose_name='Группа публикации',
                              help_text='Сообщество',
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date', 'text'][:10]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Текст вашей публикации')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата комментария', )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='Автор',
                               help_text='Автор этого комментария',
                               related_name='comments')
    post = models.ForeignKey(Post,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE,
                             verbose_name='Пост комментария',
                             help_text='Пост над комментарием',
                             related_name='comments')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created', 'text'][:10]

    def __str__(self):
        return self.text[:15]


class Follow (models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             verbose_name='Подписчик',
                             help_text='Подписчик этой публикации',
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='Автор',
                               help_text='Автор для подписки',
                               related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-author'][:10]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name="unique_followers")
        ]

    def __str__(self):
        return self.author[:15]
