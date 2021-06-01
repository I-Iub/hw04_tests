import datetime as dt
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from time import sleep

from ..models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём пользователя-создателя постов
        cls.user = User.objects.create_user(username='tester')
        # Создаём группу "Тест views. Модель Post" для тринадцати постов
        cls.group = Group.objects.create(
            title='Тест views. Модель Post',
            slug='views-test',
            description='Группа для тестирования views'
        )
        # Создаём другую группу, чтобы проверить не попали ли в неё посты, для
        # которых указана другая группа - "Тест views. Модель Post"
        cls.another_group = Group.objects.create(
            title='Другая группа.',
            slug='views-test-another-group',
            description='Другая группа для тестирования views'
        )

        # Создаём 13 постов, указывает для них группу
        # "Тест views. Модель Post"
        for post_number in range(1, 14, 1):
            Post.objects.create(
                text=f'Текст поста #{post_number}. Тест views',
                author=PostPagesTest.user,
                group=PostPagesTest.group
            )
            sleep(0.01)

    def setUp(self):
        self.user = User.objects.create_user(username='mr_view_tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаём клиента-автора поста
        self.author_client = Client()
        self.author_client.force_login(PostPagesTest.user)
        # Создаём неавторизованного пользователя
        self.guest_client = Client()

    def test_pages_use_correct_template(self):
        """Задание 1: Проверяем будет ли вызван корректный шаблон при обращении к
        view-классам через соответствующий name.
        """
        templates_vs_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'group_slug': 'views-test'}
            ),
            'new.html': reverse('new_post')
        }
        for template, reverse_name in templates_vs_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_in_index_and_group_posts(self):
        """Задание 2: Проверка context главной страницы и страницы группы.
        А также Задание 3: Проверка, что пост с указанной группой появляется
        на главной странице и странице группы.
        """
        reverse_names = [
            reverse('index'),
            reverse('group_posts', kwargs={'group_slug': 'views-test'}),
            reverse('profile', kwargs={'username': 'tester'})
        ]
        for element in reverse_names:
            with self.subTest(element=element):
                response = self.authorized_client.get(element)
                post_0 = response.context.get('page').object_list[0]
                post_text = post_0.text
                post_pub_date = post_0.pub_date.strftime('%d.%m.%Y//%H:%M')
                post_author = str(post_0.author)
                post_group = str(post_0.group)
                self.assertEqual(post_text, 'Текст поста #13. Тест views')
                self.assertEqual(
                    post_pub_date, dt.datetime.utcnow().strftime(
                        '%d.%m.%Y//%H:%M'
                    )
                )
                self.assertEqual(post_author, 'tester')
                self.assertEqual(post_group, 'Тест views. Модель Post')

    def test_context_post(self):
        """Задание 2: Проверка context страницы отдельного поста."""
        reverse_name = reverse(
            'post', kwargs={'username': 'tester', 'post_id': 13}
        )
        response = self.authorized_client.get(reverse_name)
        post_0 = response.context['post']
        post_text = post_0.text
        post_pub_date = post_0.pub_date.strftime('%d.%m.%Y//%H:%M')
        post_author = str(post_0.author)
        post_group = str(post_0.group)
        self.assertEqual(post_text, 'Текст поста #13. Тест views')
        self.assertEqual(
            post_pub_date, dt.datetime.utcnow().strftime(
                '%d.%m.%Y//%H:%M'
            )
        )
        self.assertEqual(post_author, 'tester')
        self.assertEqual(post_group, 'Тест views. Модель Post')

    def test_context_new_post(self):
        """Задание 2: Проверка context страницы создания поста (типа полей
        формы).
        """
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_context_post_edit(self):
        """Задание 2: Проверка context страницы редактирования поста (типа полей
        формы).
        """
        response = self.author_client.get(
            reverse('post_edit', kwargs={'username': 'tester', 'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_first_page_paginator(self):
        """Задание 4: Проверка паджинатора: количество постов на первой
        странице - 10.
        """
        reverse_list = [
            reverse('index'),
            reverse('group_posts', kwargs={'group_slug': 'views-test'}),
            reverse('profile', kwargs={'username': 'tester'})
        ]
        for element in reverse_list:
            with self.subTest(element=element):
                response = self.authorized_client.get(element)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    10
                )

    def test_second_page_paginator(self):
        """Задание 4: Проверка паджинатора: количество постов на второй
        странице - 3.
        """
        reverse_list = [
            reverse('index'),
            reverse('group_posts', kwargs={'group_slug': 'views-test'}),
            reverse('profile', kwargs={'username': 'tester'})
        ]
        for element in reverse_list:
            with self.subTest(element=element):
                response = self.authorized_client.get(element + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    3
                )

    def test_another_group(self):
        """Задание 3: Проверяем не попали ли в another_group посты, в поле group
        которых указано "Тест views. Модель Post" (cls.group в setUpClass).
        """
        # Получаем пост из группы "Тест views. Модель Post"
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'group_slug': 'views-test'})
        )
        post_0 = response.context.get('page').object_list[0]

        # Получаем список постов в группе "Другая группа."
        response = self.authorized_client.get(
            reverse(
                'group_posts',
                kwargs={'group_slug': 'views-test-another-group'}
            )
        )

        # # Получаем список постов в группе "Тест views. Модель Post"
        # response = self.authorized_client.get(
        #     reverse(
        #         'group_posts',
        #         kwargs={'group_slug': 'views-test'}
        #     )
        # )

        # Проверяем что post_0 не содержится в списке постов группы
        # "Другая группа."
        self.assertNotIn(post_0, response.context.get('page').object_list)

    def test_static_pages_accessible_by_name(self):
        """Задание 5: Проверяем что статические страницы доступны
        неавторизованному пользователю.
        """
        reverse_names = [
            reverse('about:author'),
            reverse('about:tech')
        ]
        for name in reverse_names:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, 200)

    def test_static_pages_uses_correct_templates(self):
        """Задание 5: Проверяем, что при запросе неавторизованного
        пользователя статических страниц отображаются ожидаемые шаблоны.
        """
        templates_vs_names = {
            'tech.html': reverse('about:tech'),
            'author.html': reverse('about:author')
        }
        for template, name in templates_vs_names.items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)
