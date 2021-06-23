from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()[:13]
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'group': group}
    return render(request, 'posts/group.html',
                  context=context)


@login_required
def new_post(request):
    title = 'Создать запись'
    button = 'Отправить'
    form = PostForm(request.POST or None, files=request.FILES or None)
    user = request.user
    if request.method == 'POST' and form.is_valid():
        new_data = form.save(commit=False)
        new_data.author = user
        new_data.save()
        return redirect('posts:index')
    return render(request, 'posts/new_post.html',
                  {'title': title, 'form': form, 'button': button})


@login_required
def post_edit(request, username, post_id):
    title = 'Редактировать запись'
    button = 'Сохранить'
    author = get_object_or_404(User, username=username)
    current_user = request.user
    post_kwargs = {'username': username, 'post_id': post_id}
    # пробуем кварги по реверсу
    if current_user == author:
        post = get_object_or_404(Post, author=author, id=post_id)
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('posts:post', kwargs=post_kwargs))
        return render(
            request, 'posts/new_post.html',
            {'form': form, 'title': title, 'button': button, 'post': post},
        )
    return redirect(reverse('posts:post', kwargs=post_kwargs))


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=author).order_by('-pub_date')
    posts_count = user_posts.count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts_count': posts_count,
        'page': page
    }
    return render(request, 'posts/profile.html', context=context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=username)
    comments = post.comments.all()
    posts_count = Post.objects.filter(author=author).count()
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "comments": comments,
        "author": author,
        "posts_count": posts_count,
        "form": form
    }
    return render(request, 'posts/post.html', context=context)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    post_kwargs = {'username': username, 'post_id': post_id}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
    return redirect(reverse('posts:post', kwargs=post_kwargs))


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user != author and \
            not Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)
