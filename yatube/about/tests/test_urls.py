from django.test import TestCase, Client
from django.contrib.auth.models import User
from posts.models import Post, Group
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        self.guest_client = Client()
        self.post_kwargs = {'username': self.post.author,
                            'post_id': self.post.id}
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_about_tech_url_available_any_user(self):
        """Страница tech доступна любому пользователю."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_about_author_url_available_any_user(self):
        """Страница author доступна любому пользователю."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

        # А почему всетаки проверка шаблонов только по ревесам?
        # а если тебе именно этот путь хочется использовать?
        # и это запланировано в проекте?
