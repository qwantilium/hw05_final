import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Group, Post
import datetime as dt
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # Создаем запись в базе данных для проверки сушествующего slug
        test_author = User.objects.create_user(username='Konst1')
        pub_date = dt.datetime.now().date()
        cls.group_test = Group.objects.create(
            title='test',
            slug='test-slug1'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый текст',
            author=test_author,
            pub_date=pub_date
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):

        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        self.post_kwargs = {'username': self.post_test.author,
                            'post_id': self.post_test.id}
        self.author_kwargs = {'username': self.post_test.author}
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        # Логиним юзера - тестового автора
        self.authorized_client.force_login(self.post_test.author)

    def test_new_post_create_task(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(text='Тестовый текст',
                                image='posts/small.gif').exists()
        )

    def test_post_edit_create_task(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в TasSk
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст1',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'username': self.post_test.author,
                'post_id': self.post_test.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post',
                                               kwargs=self.post_kwargs))
        # Проверяем, НЕ увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что запись СМЕНИЛАСЬ
        self.assertTrue(
            Post.objects.filter(text='Тестовый текст1',
                                image='posts/small1.gif').exists()
        )
