import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, Follow, Comment
from django import forms
import datetime as dt
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_author = User.objects.create_user(username='Konst1')
        pub_date = dt.datetime.now().date()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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

        cls.group_test = Group.objects.create(
            title='test',
            slug='test-slug1'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый текст',
            author=test_author,
            pub_date=pub_date,
            group=cls.group_test,
            image=uploaded
        )
        cls.posts_count = Post.objects.filter(author=test_author).count()
        cls.user_post = Post.objects.filter(
            author=test_author).order_by('-pub_date')

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        self.post_kwargs = {'username': self.post_test.author,
                            'post_id': self.post_test.id}
        self.author_args = {'username': self.post_test.author}
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        # Логиним юзера - тестового автора
        self.authorized_client.force_login(self.post_test.author)

    @classmethod
    def tearDownClass(cls):
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/new_post.html': reverse('posts:post_edit',
                                           kwargs=self.post_kwargs),
            'posts/group.html': reverse('posts:groups',
                                        args=[self.group_test.slug]),
            'posts/post.html': reverse('posts:post',
                                       kwargs=self.post_kwargs),
            'posts/profile.html': reverse('posts:profile',
                                          args=[self.post_test.author]),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        context_index = response.context['page'][0]
        sum_posts = (response.context['page'].
                     end_index() - response.context['page'].start_index()) + 1
        self.assertEqual(
            context_index.text, 'Тестовый текст'
        )
        self.assertEqual(
            context_index.author,
            self.post_test.author,
        )
        self.assertEqual(
            context_index.pub_date, self.post_test.pub_date
        )
        self.assertEqual(
            context_index.image, self.post_test.image
        )
        self.assertLessEqual(
            sum_posts, 10)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:groups',
                                                 args=[self.group_test.slug]))
        context_group = response.context['page'][0]
        sum_posts = (response.context['page'].
                     end_index() - response.context['page'].start_index()) + 1
        self.assertEqual(
            context_group.text, 'Тестовый текст'
        )
        self.assertEqual(
            context_group.author,
            self.post_test.author,
        )
        self.assertEqual(
            context_group.pub_date, self.post_test.pub_date
        )
        self.assertEqual(
            context_group.image, self.post_test.image
        )
        self.assertLessEqual(
            sum_posts, 10)
        self.assertEqual(response.context['group'].title, 'test')
        self.assertEqual(response.context['group'].slug, 'test-slug1')

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs=self.post_kwargs))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs=self.author_args))
        sum_posts = (response.context['page'].
                     end_index() - response.context['page'].start_index()) + 1
        context_profile = response.context['page'][0]
        self.assertEqual(
            context_profile.text,
            'Тестовый текст'
        )
        self.assertEqual(
            context_profile.author,
            self.post_test.author,
        )
        self.assertEqual(
            context_profile.pub_date,
            self.post_test.pub_date
        )
        self.assertEqual(
            context_profile.image, self.post_test.image
        )
        self.assertLessEqual(
            sum_posts, 10)
        self.assertEqual(
            response.context['author'],
            self.post_test.author)
        self.assertEqual(
            response.context['posts_count'],
            self.posts_count)

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post', kwargs=self.post_kwargs)
        )
        post = Post.objects.get(id=self.post_test.id)

        self.assertEqual(
            response.context['author'],
            self.post_test.author)
        self.assertEqual(
            response.context['post'],
            post)
        self.assertEqual(
            response.context['posts_count'],
            self.posts_count)

    def test_initial_value(self):
        """Предустановленнное значение формы."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        title_inital = response.context['form'].fields['text'].initial
        self.assertEqual(title_inital, None)

    def test_add_comment_autorized_client_value(self):
        """Добавляется ли пост авторизированным пользователем
        и не добавляется гостем"""
        posts_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст1',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'username': self.post_test.author,
                'post_id': self.post_test.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post',
                                               kwargs=self.post_kwargs))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), posts_count + 1)

    def test_add_comment_guest_client_value(self):
        """Добавляется ли пост авторизированным пользователем
        и не добавляется гостем"""
        posts_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст1',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'username': self.post_test.author,
                'post_id': self.post_test.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, НЕ увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), posts_count)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author1 = User.objects.create_user(username='Konst1')
        cls.test_author2 = User.objects.create_user(username='Konst2')
        cls.test_author3 = User.objects.create_user(username='Konst3')

    def setUp(self):
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.test_author1)

        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.test_author2)

        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.test_author3)

    def test_follow_view(self):
        """Тестируем авторизированный пользователь может подписаться."""
        self.authorized_client1.get(
            reverse('posts:profile_follow',
                    args=[self.test_author2])
        )

        self.assertTrue(
            Follow.objects.filter(
                user=self.test_author1,
                author=self.test_author2,
            ).exists()
        )

    def test_follow_adding_subscibe_view(self):
        """Тестируем Новая запись пользователя появляется в ленте тех,
         кто на него подписан и не появляется в ленте тех,
         кто не подписан на него."""
        follows_count = Follow.objects.count()
        # Подпишем
        self.authorized_client1.get(
            reverse(
                'posts:profile_follow',
                args=[self.test_author2])
        )
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        # Отпишем
        self.authorized_client1.get(
            reverse('posts:profile_unfollow',
                    args=[self.test_author2])
        )
        self.assertNotEqual(Follow.objects.count(), follows_count + 1)

    def test_unfollow_view(self):
        """Тестируем отписку пользователем"""
        Follow.objects.create(
            user=self.test_author1,
            author=self.test_author2
        )
        self.authorized_client1.get(
            reverse(
                'posts:profile_unfollow',
                args=[self.test_author2]
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.test_author1,
                author=self.test_author2
            ).exists()
        )


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        cls.test_author_page = User.objects.create_user(username='Konst_page')
        cls.pub_date = dt.datetime.now().date()
        super().setUpClass()
        cls.group_page = Group.objects.create(
            title='test_page',
            slug='test-slug-page'
        )
        objs = [
            Post(text=f'{i} Текст тестового поста',
                 group=cls.group_page,
                 author=cls.test_author_page)
            for i in range(1, 14)
        ]
        cls.post_page = Post.objects.bulk_create(objs)

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент

        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_author_page)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_index_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:groups',
                                           args=[self.group_page.slug]))
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_group_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse('posts:groups', args=[self.group_page.slug]) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', args=[self.test_author_page])
        )
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_profile_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse('posts:profile', args=[self.test_author_page]) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_page_not_found_template_response(self):
        # Проверка на 404 код
        response = self.client.get('/blablablablablablablagbl/')
        self.assertEqual(response.status_code, 404)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Konst_cache'),
        )

    def setUp(self):
        self.user = User.objects.get(username=self.post1.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        """Проверяется работа кэширования страницы index.html"""
        one = self.authorized_client.get(reverse('posts:index'))
        post1 = Post.objects.get(pk=1)
        post1.text = 'Измененный текст'
        post1.save()
        two = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(one.content, two.content)
        cache.clear()
        three = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(one.content, three.content)
