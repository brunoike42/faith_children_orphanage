from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory

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

def post_form(request, pk=None):
    """Form for creating/editing posts - admin only"""
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)
    
    post = None
    if pk:
        post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        # Handle form submission
        pass
    
    context = {
        'post': post,
        'categories': BlogCategory.objects.all(),
    }
    return render(request, 'blog/post_form.html', context)
