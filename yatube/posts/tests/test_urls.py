from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='tester')
        Post.objects.create(
            text='Текст. Тест URL',
            pub_date='02.02.1999',
            author=PostURLTests.author,
            group=Group.objects.create(
                title='Тест URL. Модель Post',
                slug='url-test',
                description='Группа для тестирования URL'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='url tester 2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.clients_list = [self.guest_client, self.authorized_client]
        self.routes_list = ['/', '/group/url-test/']
        self.templates_urls = {
            'index.html': '/',
            'group.html': '/group/url-test/',
            'new.html': '/new/'
        }
        # Фикстуры для итогового задания спринта:
        self.new_routes_list = [
            reverse('profile', kwargs={'username': 'tester'}),
            reverse('post', kwargs={'username': 'tester', 'post_id': 1})
        ]
        self.post_edit_reverse_name = reverse(
            'post_edit',
            kwargs={'username': 'tester', 'post_id': 1}
        )
        self.alien = User.objects.create_user(username='alien')
        self.alien_client = Client()
        self.alien_client.force_login(self.alien)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.author)

    def test_anybody_gets_routes_list(self):
        """Проверка доступности главной страницы и страницы группы для
        авторизованного и неавторизованного пользователя.
        """
        for client in self.clients_list:
            for route in self.routes_list:
                with self.subTest(route=route):
                    response = client.get(route)
                    self.assertEqual(response.status_code, 200)

    def test_guest_gets_new(self):
        """Проверка перенаправления неавторизованного пользователя при попытке
        доступа к странице создания нового поста на страницу авторизации.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/new/'))

    def test_authorized_gets_new(self):
        """Проверка доступности страницы создания нового поста для
        авторизованного пользователя.
        """
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_gets_correct_templates_using_urls(self):
        """Проверка вызова ожидаемых шаблонов."""
        for template, route in self.templates_urls.items():
            with self.subTest(route=route):
                response = self.authorized_client.get(route)
                self.assertTemplateUsed(response, template)

    # Новые тесты финального задания:
    def test_authorized_client_gets_profile_and_post(self):
        """Проверка доступности профайла пользователя и отдельного поста для
        авторизованного пользователя.
        """
        for route in self.new_routes_list:
            with self.subTest(route=route):
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_guest_client_gets_profile_and_post(self):
        """Проверка доступности профайла пользователя и отдельного поста для
        НЕавторизованного пользователя.
        """
        for route in self.new_routes_list:
            with self.subTest(route=route):
                response = self.guest_client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_guest_client_gets_post_edit(self):
        """"Проверка доступности страницы редактирования поста для неавторизованного
        пользователя.
        """
        response = self.guest_client.get(self.post_edit_reverse_name)
        self.assertEqual(response.status_code, 302)

    def test_author_client_gets_post_edit(self):
        """"Проверка доступности страницы редактирования поста для автора поста.
        """
        response = self.author_client.get(self.post_edit_reverse_name)
        self.assertEqual(response.status_code, 200)

    def test_alien_client_gets_post_edit(self):
        """"Проверка доступности страницы редактирования поста для авторизованного
        НЕ автора поста.
        """
        response = self.alien_client.get(self.post_edit_reverse_name)
        self.assertEqual(response.status_code, 302)

    def test_author_client_using_correct_tempate_for_post_edit(self):
        """Проверка вызова ожидаемого шаблона при вызове страницы
        редактирования поста."""
        response = self.author_client.get(self.post_edit_reverse_name)
        self.assertTemplateUsed(response, 'new.html')

    def test_guest_client_redirects_from_post_edit(self):
        """Проверка перенаправления неавторизованного пользователя при попытке
        доступа к странице редактирования поста на страницу авторизации.
        """
        response = self.guest_client.get(
            self.post_edit_reverse_name, follow=True
        )
        self.assertRedirects(
            response,
            ('/auth/login/?next=/tester/1/edit/')
        )

    def test_alien_client_redirects_from_post_edit(self):
        """Проверка перенаправления авторизованного НЕ автора поста при попытке
        доступа к странице редактирования поста на страницу просмотра поста.
        """
        response = self.alien_client.get(
            self.post_edit_reverse_name, follow=True
        )
        self.assertRedirects(
            response,
            ('/tester/1/')
        )
