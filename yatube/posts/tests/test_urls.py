from django.test import TestCase, Client
from django.contrib.auth.models import User
from posts.models import Post, Group
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создадим запись в БД для проверки доступности адреса task/test-slug/

        cls.test_group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Konst'),
            pub_date='22.04.2021',
            group=cls.test_group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.post_kwargs = {'username': self.post.author,
                            'post_id': self.post.id}
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

        # Проверяем общедоступные страницы

    def test_home_url_available_any_user(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, 200)

    def test_group_available_any_user(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:groups',
                                                 args=[self.test_group.slug]))
        self.assertEqual(response.status_code, 200)

    def test_profile_available_any_user(self):
        """Страница /<str:username>/ (profile) доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:profile',
                                                 args=[self.post.author]))
        self.assertEqual(response.status_code, 200)

    def test_new_authorized(self):
        """Страница /new/ доступна авторизированному пользователю."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        self.assertEqual(response.status_code, 200)

    def test_profile1_available_any_user(self):
        """Страница /<str:username>/<int:post_id>/ (post)
         доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:post', kwargs=self.post_kwargs))
        self.assertEqual(response.status_code, 200)

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        assert_reverse = reverse('posts:new_post')
        response = self.guest_client.get(
            reverse('posts:new_post'), follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={assert_reverse}')

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /<str:username>/<int:post_id>/edit/
        перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs=self.post_kwargs), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=%s' % reverse(
                'posts:post_edit', kwargs=self.post_kwargs))

    # Проверка вызываемых шаблонов для каждого адреса
    # во view тоже самое...переделать под обычный url?
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/new_post.html': reverse('posts:post_edit',
                                           kwargs=self.post_kwargs),
            'posts/group.html': reverse('posts:groups',
                                        args=[self.test_group.slug]),
            'posts/post.html': reverse('posts:post',
                                       kwargs=self.post_kwargs),
            'posts/profile.html': reverse('posts:profile',
                                          args=[self.post.author]),
        }
        for template, url in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
