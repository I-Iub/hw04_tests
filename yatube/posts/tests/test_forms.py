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

    def setUp(self):
        # Создаём клиента
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
            'text': 'Текст! Текст! Текст!'
        }

        # Отправляем POST-запрос на создание нового поста
        self.authorized_client.post(
            reverse('new_post'),
            data=form,
            follow=True
        )

        # Проверяем, что количество постов в базе posts_count увеличилось на
        # один
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверяем, что при редактировании поста через форму изменяется
        соотвествующая запись в базе данных.
        """
        form = {
            'text': 'Текст! *3'
        }

        # Отправляем POST-запрос на редактирования поста
        self.author_client.post(
            reverse(
                'post_edit',
                kwargs={'username': 'mr tester', 'post_id': 1}
            ),
            data=form,
            follow=True
        )

        # # Делаем запрос к странице поста
        # response = self.author_client.get(
        #     reverse(
        #         'post',
        #         kwargs={'username': 'mr tester', 'post_id': 1}
        #     )
        # )
        # post_0 = response.context['post']
        # post_text = post_0.text
        # post_pub_date = post_0.pub_date.strftime('%d.%m.%Y//%H:%M')
        # post_author = str(post_0.author)
        # # post_group = str(post_0.group)
        # self.assertEqual(post_text, 'Текст! *3')
        # self.assertEqual(
        #     post_pub_date, dt.datetime.utcnow().strftime(
        #         '%d.%m.%Y//%H:%M'
        #     )
        # )
        # self.assertEqual(post_author, 'mr tester')
        # # self.assertEqual(post_group, 'Test form')

        response = self.authorized_client.get(reverse('index'))
        post_0 = response.context.get('page').object_list[0]
        post_text = post_0.text
        post_pub_date = post_0.pub_date.strftime('%d.%m.%Y//%H:%M')
        post_author = str(post_0.author)
        # post_group = str(post_0.group)
        self.assertEqual(post_text, 'Текст! *3')
        self.assertEqual(
            post_pub_date, dt.datetime.utcnow().strftime(
                '%d.%m.%Y//%H:%M'
            )
        )
        self.assertEqual(post_author, 'mr tester')
        # self.assertEqual(post_group, 'Test form')
