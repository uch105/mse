from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.template.loader import render_to_string
import json
from core.models import Topic, Reply, Category, Tag, Attachment, Bookmark, Report, UserProfile
from django.contrib.auth.models import User


def forum_feed(request):
    """Main forum feed view"""
    # Get filter parameters
    category_filter = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('q', '')
    
    # Base queryset with optimized queries
    topics = Topic.objects.select_related('author', 'category').prefetch_related(
        'tags',
        'upvotes',
        'downvotes',
        'replies',
        'attachments'
    )
    
    # Apply category filter
    if category_filter != 'all':
        category = get_object_or_404(Category, slug=category_filter)
        topics = topics.filter(category=category)
    
    # Apply search filter
    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Apply sorting
    if sort_by == 'newest':
        topics = topics.order_by('-is_pinned', '-created_at')
    elif sort_by == 'popular':
        topics = topics.annotate(
            vote_count=Count('upvotes') - Count('downvotes'),
            reply_count_annotated=Count('replies')
        ).order_by('-is_pinned', '-vote_count', '-reply_count_annotated')
    elif sort_by == 'active':
        topics = topics.order_by('-is_pinned', '-last_activity')
    elif sort_by == 'unanswered':
        topics = topics.filter(replies__isnull=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(topics, 20)  # 20 topics per page
    page_number = request.GET.get('page', 1)
    topics_page = paginator.get_page(page_number)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('forum/partials/topic_list.html', {
            'topics': topics_page,
            'user': request.user
        })
        return JsonResponse({
            'html': html,
            'has_next': topics_page.has_next(),
            'page': topics_page.number
        })
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    # Get forum statistics
    total_topics = Topic.objects.count()
    total_replies = Reply.objects.count()
    total_members = User.objects.filter(is_active=True).count()
    
    context = {
        'topics': topics_page,
        'categories': categories,
        'current_category': category_filter,
        'current_sort': sort_by,
        'search_query': search_query,
        'total_topics': total_topics,
        'total_replies': total_replies,
        'total_members': total_members,
    }
    
    return render(request, 'forum/feed.html', context)


def topic_detail(request, slug):
    """View for individual topic with replies"""
    # Get topic with optimized queries
    topic = get_object_or_404(
        Topic.objects.select_related('author', 'category')
        .prefetch_related(
            'tags',
            'upvotes',
            'downvotes',
            'attachments',
            Prefetch(
                'replies',
                queryset=Reply.objects.select_related('author').prefetch_related(
                    'upvotes',
                    'downvotes',
                    Prefetch(
                        'children',
                        queryset=Reply.objects.select_related('author').prefetch_related('upvotes', 'downvotes')
                    )
                ).filter(parent__isnull=True)  # Only top-level replies
            )
        ),
        slug=slug
    )
    
    # Increment view count (you might want to use sessions to track unique views)
    if not request.session.get(f'topic_viewed_{topic.id}'):
        topic.increment_views()
        request.session[f'topic_viewed_{topic.id}'] = True
    
    # Get sort parameter for comments
    sort_comments = request.GET.get('sort_comments', 'oldest')
    
    replies = topic.replies.all()
    if sort_comments == 'newest':
        replies = replies.order_by('-created_at')
    elif sort_comments == 'popular':
        replies = replies.annotate(
            vote_count=Count('upvotes') - Count('downvotes')
        ).order_by('-vote_count')
    else:  # oldest (default)
        replies = replies.order_by('created_at')
    
    # Check if user has voted on this topic
    user_upvoted = False
    user_downvoted = False
    user_bookmarked = False
    
    if request.user.is_authenticated:
        user_upvoted = topic.upvotes.filter(id=request.user.id).exists()
        user_downvoted = topic.downvotes.filter(id=request.user.id).exists()
        user_bookmarked = Bookmark.objects.filter(user=request.user, topic=topic).exists()
    
    context = {
        'topic': topic,
        'replies': replies,
        'reply_count': topic.reply_count(),
        'user_upvoted': user_upvoted,
        'user_downvoted': user_downvoted,
        'user_bookmarked': user_bookmarked,
        'sort_comments': sort_comments,
    }
    
    return render(request, 'forum/post.html', context)


@login_required
def create_topic(request):
    """View for creating a new topic"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            category_id = request.POST.get('category')
            tags_json = request.POST.get('tags', '[]')
            
            # Validation
            if not title or len(title) < 5:
                return JsonResponse({'error': 'Title must be at least 5 characters'}, status=400)
            
            if not content or len(content) < 10:
                return JsonResponse({'error': 'Content must be at least 10 characters'}, status=400)
            
            if not category_id:
                return JsonResponse({'error': 'Please select a category'}, status=400)
            
            # Get category
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Invalid category'}, status=400)
            
            # Create topic
            topic = Topic.objects.create(
                title=title,
                content=content,
                author=request.user,
                category=category
            )
            
            # Add tags
            import json
            try:
                tags_list = json.loads(tags_json)
                for tag_name in tags_list:
                    if tag_name.strip():
                        tag, created = Tag.objects.get_or_create(name=tag_name.strip().lower())
                        topic.tags.add(tag)
            except json.JSONDecodeError:
                pass
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                # Validate file size (5MB max)
                if file.size > 5 * 1024 * 1024:
                    continue
                
                Attachment.objects.create(
                    topic=topic,
                    file=file,
                    uploaded_by=request.user
                )
            
            return JsonResponse({
                'success': True,
                'redirect_url': topic.get_absolute_url()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'forum/create_topic.html', context)


@login_required
def edit_topic(request, topic_id):
    """View for editing an existing topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Check if user is the author
    if topic.author != request.user:
        messages.error(request, 'You can only edit your own topics.')
        return redirect('forum:topic_detail', slug=topic.slug)
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            category_id = request.POST.get('category')
            tags_json = request.POST.get('tags', '[]')
            removed_attachments_json = request.POST.get('removed_attachments', '[]')
            
            # Validation
            if not title or len(title) < 5:
                return JsonResponse({'error': 'Title must be at least 5 characters'}, status=400)
            
            if not content or len(content) < 10:
                return JsonResponse({'error': 'Content must be at least 10 characters'}, status=400)
            
            if not category_id:
                return JsonResponse({'error': 'Please select a category'}, status=400)
            
            # Get category
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Invalid category'}, status=400)
            
            # Update topic
            topic.title = title
            topic.content = content
            topic.category = category
            topic.save()
            
            # Update tags
            import json
            try:
                tags_list = json.loads(tags_json)
                topic.tags.clear()
                for tag_name in tags_list:
                    if tag_name.strip():
                        tag, created = Tag.objects.get_or_create(name=tag_name.strip().lower())
                        topic.tags.add(tag)
            except json.JSONDecodeError:
                pass
            
            # Remove attachments
            try:
                removed_ids = json.loads(removed_attachments_json)
                for attachment_id in removed_ids:
                    try:
                        attachment = Attachment.objects.get(id=attachment_id, topic=topic)
                        attachment.file.delete()  # Delete file from storage
                        attachment.delete()
                    except Attachment.DoesNotExist:
                        pass
            except json.JSONDecodeError:
                pass
            
            # Handle new file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                # Validate file size (5MB max)
                if file.size > 5 * 1024 * 1024:
                    continue
                
                Attachment.objects.create(
                    topic=topic,
                    file=file,
                    uploaded_by=request.user
                )
            
            return JsonResponse({
                'success': True,
                'redirect_url': topic.get_absolute_url()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request
    categories = Category.objects.all()
    existing_tags = list(topic.tags.values_list('name', flat=True))
    
    context = {
        'topic': topic,
        'categories': categories,
        'existing_tags': json.dumps(existing_tags),
    }
    return render(request, 'forum/edit_topic.html', context)


@login_required
@require_POST
def add_reply(request, topic_slug):
    """Add a reply to a topic"""
    topic = get_object_or_404(Topic, slug=topic_slug)
    
    # Check if topic is locked
    if topic.is_locked:
        return JsonResponse({'success': False, 'error': 'This topic is locked.'}, status=403)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Content is required.'}, status=400)
    
    if len(content) < 3:
        return JsonResponse({'success': False, 'error': 'Reply must be at least 3 characters long.'}, status=400)
    
    # Create reply
    parent = None
    if parent_id:
        try:
            parent = Reply.objects.get(id=parent_id, topic=topic)
        except Reply.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Parent reply not found.'}, status=404)
    
    try:
        reply = Reply.objects.create(
            topic=topic,
            author=request.user,
            content=content,
            parent=parent
        )
        
        return JsonResponse({
            'success': True,
            'reply_id': reply.id,
            'message': 'Reply posted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def vote_topic(request, topic_id):
    """Handle upvote/downvote on topics"""
    topic = get_object_or_404(Topic, id=topic_id)
    vote_type = request.POST.get('vote_type')  # 'upvote' or 'downvote'
    
    if vote_type == 'upvote':
        # Toggle upvote
        if topic.upvotes.filter(id=request.user.id).exists():
            topic.upvotes.remove(request.user)
            action = 'removed_upvote'
        else:
            topic.upvotes.add(request.user)
            topic.downvotes.remove(request.user)  # Remove downvote if exists
            action = 'added_upvote'
    
    elif vote_type == 'downvote':
        # Toggle downvote
        if topic.downvotes.filter(id=request.user.id).exists():
            topic.downvotes.remove(request.user)
            action = 'removed_downvote'
        else:
            topic.downvotes.add(request.user)
            topic.upvotes.remove(request.user)  # Remove upvote if exists
            action = 'added_downvote'
    else:
        return JsonResponse({'error': 'Invalid vote type.'}, status=400)
    
    return JsonResponse({
        'success': True,
        'action': action,
        'upvote_count': topic.upvote_count(),
        'downvote_count': topic.downvote_count()
    })


@login_required
@require_POST
def vote_reply(request, reply_id):
    """Handle upvote/downvote on replies"""
    reply = get_object_or_404(Reply, id=reply_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type == 'upvote':
        if reply.upvotes.filter(id=request.user.id).exists():
            reply.upvotes.remove(request.user)
            action = 'removed_upvote'
        else:
            reply.upvotes.add(request.user)
            reply.downvotes.remove(request.user)
            action = 'added_upvote'
    
    elif vote_type == 'downvote':
        if reply.downvotes.filter(id=request.user.id).exists():
            reply.downvotes.remove(request.user)
            action = 'removed_downvote'
        else:
            reply.downvotes.add(request.user)
            reply.upvotes.remove(request.user)
            action = 'added_downvote'
    else:
        return JsonResponse({'error': 'Invalid vote type.'}, status=400)
    
    return JsonResponse({
        'success': True,
        'action': action,
        'upvote_count': reply.upvote_count(),
        'downvote_count': reply.downvote_count()
    })


@login_required
@require_POST
def toggle_bookmark(request, topic_id):
    """Toggle bookmark on a topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        topic=topic
    )
    
    if not created:
        bookmark.delete()
        action = 'removed'
    else:
        action = 'added'
    
    return JsonResponse({
        'success': True,
        'action': action
    })


@login_required
@require_POST
def report_content(request):
    """Report a topic or reply"""
    content_type = request.POST.get('content_type')  # 'topic' or 'reply'
    content_id = request.POST.get('content_id')
    report_type = request.POST.get('report_type')
    description = request.POST.get('description', '').strip()
    
    # Validation
    if not all([content_type, content_id, report_type, description]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
    
    if len(description) < 10:
        return JsonResponse({'success': False, 'error': 'Description must be at least 10 characters.'}, status=400)
    
    try:
        # Create report
        report = Report.objects.create(
            reporter=request.user,
            report_type=report_type,
            description=description
        )
        
        # Link to content
        if content_type == 'topic':
            try:
                topic = Topic.objects.get(id=content_id)
                report.topic = topic
            except Topic.DoesNotExist:
                report.delete()
                return JsonResponse({'success': False, 'error': 'Topic not found.'}, status=404)
        elif content_type == 'reply':
            try:
                reply = Reply.objects.get(id=content_id)
                report.reply = reply
            except Reply.DoesNotExist:
                report.delete()
                return JsonResponse({'success': False, 'error': 'Reply not found.'}, status=404)
        else:
            report.delete()
            return JsonResponse({'success': False, 'error': 'Invalid content type.'}, status=400)
        
        report.save()
        
        return JsonResponse({'success': True, 'message': 'Report submitted successfully.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def category_view(request, slug):
    """View topics in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    
    # Get topics in this category
    topics = Topic.objects.filter(category=category).select_related(
        'author', 'category'
    ).prefetch_related('tags', 'replies', 'upvotes', 'downvotes', 'author__forum_profile')
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        topics = topics.order_by('-is_pinned', '-created_at')
    elif sort_by == 'popular':
        topics = topics.annotate(
            vote_count=Count('upvotes') - Count('downvotes')
        ).order_by('-is_pinned', '-vote_count')
    elif sort_by == 'active':
        topics = topics.order_by('-is_pinned', '-last_activity')
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    topics_page = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'topics': topics_page,
        'current_sort': sort_by,
    }
    
    return render(request, 'forum/category.html', context)


def tag_view(request, slug):
    """View topics with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    
    topics = Topic.objects.filter(tags=tag).select_related(
        'author', 'category'
    ).prefetch_related('tags', 'replies', 'upvotes', 'downvotes', 'author__forum_profile')
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        topics = topics.order_by('-is_pinned', '-created_at')
    elif sort_by == 'popular':
        topics = topics.annotate(
            vote_count=Count('upvotes') - Count('downvotes')
        ).order_by('-is_pinned', '-vote_count')
    elif sort_by == 'active':
        topics = topics.order_by('-is_pinned', '-last_activity')
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    topics_page = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'topics': topics_page,
    }
    
    return render(request, 'forum/tag.html', context)


def user_profile(request, username):
    """View user's forum profile"""
    user = get_object_or_404(User, username=username)
    
    # Get or create forum profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's topics
    topics = Topic.objects.filter(author=user).select_related(
        'category'
    ).prefetch_related('tags', 'replies')
    
    # Get user's replies
    replies = Reply.objects.filter(author=user).select_related(
        'topic', 'topic__category'
    ).prefetch_related('upvotes', 'downvotes')
    
    # Pagination for topics
    topics_paginator = Paginator(topics, 10)
    topics_page = topics_paginator.get_page(request.GET.get('topics_page'))
    
    # Pagination for replies
    replies_paginator = Paginator(replies, 10)
    replies_page = replies_paginator.get_page(request.GET.get('replies_page'))
    
    context = {
        'profile_user': user,
        'profile': profile,
        'topics': topics_page,
        'replies': replies_page,
    }
    
    return render(request, 'forum/user_profile.html', context)


@login_required
def my_bookmarks(request):
    """View user's bookmarked topics"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'topic', 'topic__author', 'topic__category', 'topic__author__forum_profile'
    ).prefetch_related('topic__tags', 'topic__replies', 'topic__upvotes')
    
    # Pagination
    paginator = Paginator(bookmarks, 20)
    page_number = request.GET.get('page')
    bookmarks_page = paginator.get_page(page_number)
    
    context = {
        'bookmarks': bookmarks_page,
    }
    
    return render(request, 'forum/bookmarks.html', context)


@login_required
@require_POST
def delete_topic(request, topic_id):
    """Delete a topic (only by author)"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Check if user is the author
    if topic.author != request.user:
        return JsonResponse({'error': 'You can only delete your own topics.'}, status=403)
    
    # Delete the topic
    topic.delete()
    
    messages.success(request, 'Topic deleted successfully.')
    return JsonResponse({'success': True})