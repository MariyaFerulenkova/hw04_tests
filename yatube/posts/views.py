from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    """Главная страница."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Обработка страниц сообществ отфильтрованных по группам."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Обработка профайла пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.all().filter(author__username=username)
    posts_qty = len(post_list)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts_qty': posts_qty,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Обработка страницы отдельного поста."""
    post = get_object_or_404(Post, pk=post_id)
    posts_qty = Post.objects.filter(author_id=post.author.id).count()
    context = {
        'post': post,
        'posts_qty': posts_qty,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание новой записи."""
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                'posts:profile',
                username=request.user.get_username()
            )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)

    if request.user != post.author:
        return redirect(
            'posts:post_detail',
            post_id=post_id
        )

    if form.is_valid():
        post.save()
        return redirect(
            'posts:post_detail',
            post_id=post_id
        )

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post, 'is_edit': True}
    )
