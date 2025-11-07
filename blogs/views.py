from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from core.models import Blog, BlogCategory, BlogComment, BlogShare, BlogSection


def blogs_list(request):
    """Display all published blogs with filtering and search"""
    blogs = Blog.objects.filter(status='published').select_related('author', 'category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        blogs = blogs.filter(category__slug=category_slug)
    
    # Sorting
    sort_by = request.GET.get('sort', '-published_at')
    if sort_by == 'popular':
        blogs = blogs.order_by('-views')
    elif sort_by == 'trending':
        blogs = blogs.filter(is_trending=True)
    else:
        blogs = blogs.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(blogs, 9)  # 9 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = BlogCategory.objects.annotate(blog_count=Count('blogs'))
    
    # Featured blogs
    featured_blogs = Blog.objects.filter(status='published', is_featured=True)[:3]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'featured_blogs': featured_blogs,
        'search_query': search_query,
        'current_category': category_slug,
        'current_sort': sort_by,
    }
    
    return render(request, 'blogs/blogs_list.html', context)


def blog_detail(request, slug):
    """Display single blog with comments"""
    blog = get_object_or_404(Blog, slug=slug, status='published')
    
    # Increment views
    blog.increment_views()
    
    # Get sections
    sections = blog.sections.all()
    
    # Get approved comments
    comments = blog.comments.filter(is_approved=True, parent=None).select_related('user')
    
    # Related blogs
    related_blogs = Blog.objects.filter(
        status='published',
        category=blog.category
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'sections': sections,
        'comments': comments,
        'related_blogs': related_blogs,
        'share_url': request.build_absolute_uri(),
    }
    
    return render(request, 'blogs/blog_detail.html', context)


@login_required
def add_comment(request, slug):
    """Add a comment to a blog"""
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=slug, status='published')
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('blog_detail', slug=slug)
        
        parent = None
        if parent_id:
            parent = get_object_or_404(BlogComment, id=parent_id)
        
        BlogComment.objects.create(
            blog=blog,
            user=request.user,
            parent=parent,
            content=content
        )
        
        messages.success(request, "Your comment has been posted successfully!")
        return redirect('blog_detail', slug=slug)
    
    return redirect('blogs_list')


@login_required
def share_blog(request, slug):
    """Track blog shares"""
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=slug, status='published')
        platform = request.POST.get('platform', 'unknown')
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        BlogShare.objects.create(
            blog=blog,
            user=request.user,
            platform=platform,
            ip_address=ip
        )
        
        return JsonResponse({'success': True, 'message': 'Blog shared successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def create_blog(request):
    """Admin page to create a new blog with rich editor"""
    categories = BlogCategory.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        excerpt = request.POST.get('excerpt')
        content = request.POST.get('content')
        status = request.POST.get('status', 'draft')
        is_featured = request.POST.get('is_featured') == 'on'
        is_trending = request.POST.get('is_trending') == 'on'
        meta_description = request.POST.get('meta_description', '')
        meta_keywords = request.POST.get('meta_keywords', '')
        
        # Handle featured image
        featured_image = request.FILES.get('featured_image')
        
        # Create blog
        blog = Blog.objects.create(
            title=title,
            author=request.user,
            category_id=category_id if category_id else None,
            excerpt=excerpt,
            content=content,
            status=status,
            is_featured=is_featured,
            is_trending=is_trending,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            featured_image=featured_image,
            published_at=timezone.now() if status == 'published' else None
        )
        
        messages.success(request, f"Blog '{title}' has been created successfully!")
        return redirect('blog_detail', slug=blog.slug)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'blogs/create_blog.html', context)


@login_required
@user_passes_test(is_admin)
def edit_blog(request, slug):
    """Admin page to edit an existing blog"""
    blog = get_object_or_404(Blog, slug=slug)
    categories = BlogCategory.objects.all()
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.category.id = request.POST.get('category') or None
        blog.excerpt = request.POST.get('excerpt')
        blog.content = request.POST.get('content')
        blog.status = request.POST.get('status', 'draft')
        blog.is_featured = request.POST.get('is_featured') == 'on'
        blog.is_trending = request.POST.get('is_trending') == 'on'
        blog.meta_description = request.POST.get('meta_description', '')
        blog.meta_keywords = request.POST.get('meta_keywords', '')
        
        # Handle featured image
        if request.FILES.get('featured_image'):
            blog.featured_image = request.FILES.get('featured_image')
        
        # Update published_at if status changes to published
        if blog.status == 'published' and not blog.published_at:
            blog.published_at = timezone.now()
        
        blog.save()
        
        messages.success(request, f"Blog '{blog.title}' has been updated successfully!")
        return redirect('blog_detail', slug=blog.slug)
    
    context = {
        'blog': blog,
        'categories': categories,
    }
    
    return render(request, 'blogs/edit_blog.html', context)


@login_required
@user_passes_test(is_admin)
def delete_blog(request, slug):
    """Delete a blog"""
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=slug)
        title = blog.title
        blog.delete()
        messages.success(request, f"Blog '{title}' has been deleted successfully!")
        return redirect('blogs_list')
    
    return redirect('blogs_list')