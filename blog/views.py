from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import staff_required
from .models import BlogPost, BlogCategory
from .forms import BlogPostForm, BlogCategoryForm


def post_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    categories = BlogCategory.objects.all()

    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(pk=pk)[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


# ---------------------------------------------------------------------------
# Custom admin dashboard: blog post management
# ---------------------------------------------------------------------------

@staff_required
def manage_posts(request):
    posts = BlogPost.objects.select_related('author', 'category').order_by('-created_at')
    return render(request, 'blog/manage_posts.html', {'posts': posts})


@staff_required
def post_form(request, pk=None):
    """Form for creating/editing posts - staff only"""
    post = None
    if pk:
        post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.pk:
                obj.author = request.user
            obj.save()
            messages.success(request, f'Post "{obj.title}" saved successfully!')
            return redirect('manage_posts')
    else:
        form = BlogPostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'title': 'Edit Post' if post else 'Add New Post',
    }
    return render(request, 'blog/post_form.html', context)


@staff_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'Post "{title}" deleted.')
        return redirect('manage_posts')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@staff_required
def manage_blog_categories(request):
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('manage_blog_categories')
    else:
        form = BlogCategoryForm()

    context = {
        'form': form,
        'categories': BlogCategory.objects.all(),
    }
    return render(request, 'blog/manage_categories.html', context)


@staff_required
def delete_blog_category(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('manage_blog_categories')
