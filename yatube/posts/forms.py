from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа'),
        }
        help_texts = {
            'text': _('Текст нового поста'),
            'group': _('Группа, к которой будет относиться пост'),
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'cols': 40,
                'rows': 10,
            }),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
