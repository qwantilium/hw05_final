from django.test import TestCase
from posts.models import Post, Group
from django.contrib.auth.models import User


class ModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем ее в качестве переменной класса
        # Проверяем Post модель
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(username='auth'),
        )
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-slug',
            description='X' * 50,
        )

    def test_verbose_post_name(self):
        """verbose_name в полях Модели Post совпадает с ожидаемым."""
        post = ModelTest.post
        field_verboses = {
            'text': 'Текст публикации',
            'author': 'Автор',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)

    def test_verbose_group_name(self):
        """verbose_name в полях Модели Group совпадает с ожидаемым."""

        group = ModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Адрес для группы',
            'description': 'Описание',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected)

    def test_help_post_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_help_texts = {
            'text': 'Текст вашей публикации',
            'author': 'Автор этой публикации',
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected)

    def test_help_group_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = ModelTest.group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Укажите адрес для страницы задачи. Используйте только'
                    'латиницу, цифры, дефисы и знаки подчёркивания',
            'description': 'Описание группы',
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected)

    def test_object_post_name_is_title_fild(self):
        """В поле __str__  объекта Post записано значение поля post.text."""
        post = ModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_object_group_name_is_title_fild(self):
        """В поле __str__  объекта Post записано значение поля post.text."""
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
