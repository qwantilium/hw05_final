from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group


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

    def test_about_tech_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(
            response.context['just_title'],
            'Какие там технологии?')
        self.assertEqual(
            response.context['just_text'],
            'Как тут много всего писать')

    def test_about_author_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(
            response.context['just_title'],
            'Об Авторе')
        self.assertEqual(
            response.context['just_text'],
            'Тут дооолгая история.')

    def test_about_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
