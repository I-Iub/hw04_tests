import datetime as dt
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test form',
            slug='test-form',
            description='Group For Testing Form'
        )
        cls.user = User.objects.create_user(username='mr tester')
        Post.objects.create(
            text='Text! Text! Text!',
            author=PostCreateFormTests.user,
            group=PostCreateFormTests.group
        )
        cls.another_group = Group.objects.create(
            title='Another group',
            slug='another-group',
            description='Another group for tests'
        )

    def setUp(self):
        # Создаём неавторизованного клиента
        self.guest_client = Client()
        # Создаём авторизованного клиента
        self.user = User.objects.create_user(username='mr_view_tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаём клиента-автора поста
        self.author_client = Client()
        self.author_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Проверяем, что при отправке формы создаётся новая запись в базе
        данных.
        """
        # Считаем количество постов
        posts_count = Post.objects.count()

        # Создаём "форму"
        form = {
            'text': 'Текст! Текст! Текст!',
            'group': PostCreateFormTests.group.id
        }

        # Отправляем POST-запрос на создание нового поста:
        self.authorized_client.post(
            reverse('new_post'),
            data=form,
            follow=True
        )

        # Проверяем, что текст, группа и автор у созданного поста совпадают с
        # указанными при создании:
        response = self.authorized_client.get(reverse('index'))
        post = response.context.get('page').object_list[0]
        post_text = post.text
        post_group = str(post.group)
        post_author = str(post.author)
        self.assertEqual(post_text, 'Текст! Текст! Текст!')
        self.assertEqual(post_group, 'Test form')
        self.assertEqual(post_author, 'mr_view_tester')

        # Проверяем, что количество постов в базе posts_count увеличилось на
        # один:
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверяем, что при редактировании поста через форму изменяется
        соответствующая запись в базе данных.
        """
        form = {
            'text': 'Текст! *3',
            'group': PostCreateFormTests.another_group.id  # другая группа
        }

        # Отправляем POST-запрос на редактирование поста
        self.author_client.post(
            reverse(
                'post_edit',
                kwargs={'username': 'mr tester', 'post_id': 1}
            ),
            data=form,
            follow=True
        )

        response = self.authorized_client.get(reverse('index'))
        post_0 = response.context.get('page').object_list[0]
        post_text = post_0.text
        post_pub_date = post_0.pub_date.strftime('%d.%m.%Y//%H:%M')
        post_author = str(post_0.author)
        post_group = str(post_0.group)
        post_group_slug = str(post_0.group.slug)
        self.assertEqual(post_text, 'Текст! *3')
        self.assertEqual(
            post_pub_date, dt.datetime.utcnow().strftime(
                '%d.%m.%Y//%H:%M'
            )
        )
        self.assertEqual(post_author, 'mr tester')
        self.assertEqual(post_group, 'Another group')
        self.assertEqual(post_group_slug, 'another-group')

        # Проверяем, что пост исчез со старой страницы по слагу группы
        response_old_group = self.authorized_client.get(
            reverse('group_posts', kwargs={'group_slug': 'test-form'})
        )
        self.assertNotIn(
            post_0,
            response_old_group.context.get('page').object_list,
            'Ошибка. Пост не исчез со старой страницы.'
        )
        self.assertEqual(
            response_old_group.context.get('page').object_list.count(), 0
        )

    def test_guest_client_posts_new_and_edit(self):
        """Проверка перенаправления неавторизованного пользователя при попытке
        опубликовать пост (через POST-запрос) на страницу авторизации, и что
        пост при этом не создаётся.
        """
        expected_vs_revnames = {
            '/auth/login/?next=/new/': reverse('new_post'),
            '/auth/login/?next=/tester/1/edit/': reverse(
                'post_edit',
                kwargs={'username': 'tester', 'post_id': 1}
            )
        }
        # Считаем количество постов
        posts_count = Post.objects.count()

        # Создаём "форму"
        form = {
            'text': 'guest_client: "Текст!"',
            'group': PostCreateFormTests.group.id
        }
        for expected, name in expected_vs_revnames.items():
            with self.subTest(name=name):
                # Отправляем POST-запрос на создание нового поста
                response = self.guest_client.post(
                    name,
                    data=form,
                    follow=True
                )
                # Проверяем, что неавторизованный пользователь
                # перенаправляется на страницу авторизации
                self.assertRedirects(response, expected)
                # Проверяем, что количество постов в базе posts_count не
                # изменилось
                self.assertEqual(Post.objects.count(), posts_count)

    # def test_guest_client_posts_new(self):
    #     """Проверка перенаправления неавторизованного пользователя при попытке
    #     опубликовать пост на страницу авторизации, и что
    #     пост при этом не создаётся.
    #     """
    #     # Считаем количество постов
    #     posts_count = Post.objects.count()

    #     # Создаём "форму"
    #     form = {
    #         'text': 'guest_client: "Текст!"',
    #         'group': PostCreateFormTests.group.id
    #     }

    #     # Отправляем POST-запрос на создание нового поста
    #     response = self.guest_client.post(
    #         reverse('new_post'),
    #         data=form,
    #         follow=True
    #     )
    #     # Проверяем, что неавторизованный пользователь перенаправляется на
    #     # страницу авторизации
    #     self.assertRedirects(response, ('/auth/login/?next=/new/'))
    #     # Проверяем, что количество постов в базе posts_count не изменилось
    #     self.assertEqual(Post.objects.count(), posts_count)

    # def test_guest_client_gets_post_edit(self):
    #     """Проверка перенаправления неавторизованного пользователя при попытке
    #     отредактировать пост на страницу авторизации, и что
    #     пост при этом не создаётся.
    #     """
    #     # Считаем количество постов
    #     posts_count = Post.objects.count()

    #     # Создаём "форму"
    #     form = {
    #         'text': 'guest_client: "Текст!"',
    #         'group': PostCreateFormTests.group.id
    #     }

    #     # Отправляем POST-запрос на создание нового поста
    #     response = self.guest_client.post(
    #         reverse(
    #             'post_edit',
    #             kwargs={'username': 'tester', 'post_id': 1}
    #         ),
    #         data=form,
    #         follow=True
    #     )
    #     # Проверяем, что неавторизованный пользователь перенаправляется на
    #     # страницу авторизации
    #     self.assertRedirects(response, ('/auth/login/?next=/tester/1/edit/'))
    #     # Проверяем, что количество постов в базе posts_count не изменилось
    #     self.assertEqual(Post.objects.count(), posts_count)
