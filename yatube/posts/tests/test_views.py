from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
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
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с указанием группы',
            group=cls.group,
        )
        cls.new_group = Group.objects.create(
            title='Пустая группа',
            slug='empty-group',
            description='Тестовое описание пустой группы',
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

# view-классы используют ожидаемые HTML-шаблоны

    def test_pages_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

# в шаблон передан правильный контекст + дополнительные проверки

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 2)

        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовый пост')

        second_object = response.context['page_obj'][1]
        post_group_1 = second_object.group.title
        self.assertEqual(post_group_1, 'Тестовая группа')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        group_slug_0 = first_object.group.slug
        group_description_0 = first_object.group.description
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text

        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(group_title_0, 'Тестовая группа')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertEqual(group_description_0, 'Тестовое описание')
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовый пост с указанием группы')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(response.context['author'].username, 'auth')
        self.assertEqual(response.context['posts_qty'], 2)
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        self.assertEqual(response.context['post'].id, self.post.id)
        self.assertEqual(response.context['posts_qty'], 2)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        self.assertEqual(response.context['post'].id, self.post.id)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)

    def test_post_with_group_not_in_new_group(self):
        """Post_with_group не попал в группу, для которой
        не был предназначен."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'empty-group'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        posts_numbers = 13
        for num in range(posts_numbers):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {num}',
                group=cls.group,
            )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)

    def setUp(self):
        self.guest_client = Client()

    def test_first_pages_contains_ten_records(self):
        """Количество постов на первых страницах index,
        group_list, profile равно 10."""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_pages_contains_three_records(self):
        """Количество постов на вторых страницах index,
        group_list, profile равно 3."""
        reverse_names = (
            (reverse('posts:index') + '?page=2'),
            (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': 'test-slug'}
                ) + '?page=2'
            ),
            (reverse('posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 3)
