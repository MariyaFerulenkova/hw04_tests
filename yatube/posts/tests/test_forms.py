from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
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
            group=cls.group,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """При отправке валидной формы со страницы
        создания поста, создается новая запись в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст',
                group=self.group.id,
            ).exists()
        )

    def test_post_edit(self):
        """При отправке валидной формы со страницы
        редактирования поста, происходит изменение поста в базе данных."""
        form_data = {
            'text': 'Новый текст. Отредактировано',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(self.post.id,)
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст. Отредактировано',
                group=self.group.id,
            ).exists()
        )

    def test_labels(self):
        text_label = PostFormTests.form.fields['text'].label
        group_label = PostFormTests.form.fields['group'].label
        self.assertEqual(text_label, 'Текст поста')
        self.assertEqual(group_label, 'Группа')

    def test_help_texts(self):
        text_help_text = PostFormTests.form.fields['text'].help_text
        group_help_text = PostFormTests.form.fields['group'].help_text
        self.assertEqual(text_help_text, 'Текст нового поста')
        self.assertEqual(
            group_help_text,
            'Группа, к которой будет относиться пост'
        )
