from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField()  # type: ignore
    pub_date = models.DateTimeField(auto_now_add=True)  # type: ignore
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )  # type: ignore
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )  # type: ignore

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)  # type: ignore
    slug = models.SlugField(max_length=50, unique=True)  # type: ignore
    description = models.TextField()  # type: ignore

    def __str__(self) -> str:
        return self.title
