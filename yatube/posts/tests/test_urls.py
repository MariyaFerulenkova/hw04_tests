from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Создаем экземпляр клиента,
        делаем запрос к главной странице,
        проверяем, что статус код равен 200."""
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_not_author = User.objects.create_user(username='NotAuthor')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user_not_author)

    def test_common_posts_urls_exists_at_desired_location(self):
        """ Страницы /, /group/slug/, /profile/username/,
        /posts/post_id/ доступны любому пользователю."""
        urls = (
            '/',
            '/group/test-slug/',
            '/profile/HasNoName/',
            f'/posts/{self.post.id}/',
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_url_exists_at_desired_location(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_url_redirect_not_author_on_post(self):
        """Страница /posts/post_id/edit/ перенаправляет не автора
        поста на страницу поста."""
        response = self.not_author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_unexisting_page_return_404(self):
        """Страница /unexisting_page/ вернет ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
