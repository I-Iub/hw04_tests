from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Текст поста 3456789012345',
            pub_date='01.01.1999',
            author=User.objects.create_user(username='mr_test'),
            group=Group.objects.create(
                title='Тестовая группа для модели Post',
                slug='testgroup',
                description='<Описание тестовой группы>'
            )
        )
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test',
            description='Описание группы'
        )

    def test_post(self):
        """Значение поля __str__ в модели Post отображается правильно."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group(self):
        """Значение поля __str__ в модели Group отображается правильно."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
