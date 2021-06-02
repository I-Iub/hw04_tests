from django.test import Client, TestCase
from django.urls import reverse


class AboutTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # Создаём неавторизованного пользователя
        self.guest_client = Client()

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
