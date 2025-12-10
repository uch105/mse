import json
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage
from .utils import MaterialQueryEngine
from .intent_classifier import IntentClassifier


# Initialize global instances
#query_engine = MaterialQueryEngine()
intent_classifier = IntentClassifier()


@login_required(login_url='/login/')
def matscichat(request):
    """Main chat interface"""
    return render(request, 'matscichat/chat.html')


@login_required(login_url='/login/')
@require_http_methods(["GET"])
def get_chat_sessions(request):
    """Get all chat sessions for the current user"""
    sessions = ChatSession.objects.filter(user=request.user)
    
    data = [{
        'id': session.id,
        'title': session.title,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat(),
        'message_count': session.messages.count()
    } for session in sessions]
    
    return JsonResponse({'sessions': data})


@login_required(login_url='/login/')
@require_http_methods(["POST"])
def create_chat_session(request):
    """Create a new chat session"""
    session = ChatSession.objects.create(
        user=request.user,
        title="New Chat"
    )
    
    return JsonResponse({
        'id': session.id,
        'title': session.title,
        'created_at': session.created_at.isoformat()
    })


@login_required(login_url='/login/')
@require_http_methods(["GET"])
def get_chat_messages(request, session_id):
    """Get all messages for a specific chat session"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    
    messages = session.messages.all()
    data = [{
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'intent': msg.intent,
        'confidence': msg.confidence,
        'created_at': msg.created_at.isoformat()
    } for msg in messages]
    
    return JsonResponse({'messages': data})


@login_required(login_url='/login/')
@require_http_methods(["DELETE"])
def delete_chat_session(request, session_id):
    """Delete a chat session"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.delete()
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


def generate_response(query: str, session_id: int):
    """Generator function that yields response chunks"""
    # Analyze the query
    analysis = intent_classifier.analyze_query(query)
    intents = analysis.get('intents', [])
    materials = analysis.get('materials', [])
    applications = analysis.get('applications', [])
    confidence = analysis['confidence']
    
    # Yield metadata first
    yield f"data: {json.dumps({'type': 'metadata', 'intents': intents, 'materials': materials, 'applications': applications, 'confidence': confidence})}\n\n"
    
    # Generate answer using the advanced query engine
    full_response = ""
    try:
        generator = query_engine.generate_answer(query, analysis)
        
        for chunk in generator:
            full_response += chunk
            yield f"data: {json.dumps({'type': 'content', 'chunk': chunk})}\n\n"
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}\n"
        full_response += error_msg
        yield f"data: {json.dumps({'type': 'content', 'chunk': error_msg})}\n\n"
    
    # Save the complete interaction to database
    try:
        session = ChatSession.objects.get(id=session_id)
        
        # Save assistant's response
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=full_response,
            intent=','.join(intents),
            confidence=confidence,
            entities={
                'materials': materials,
                'applications': applications
            }
        )
        
        # Update session title if it's the first message
        if session.messages.count() <= 2:  # User + Assistant message
            # Generate title from first user query (truncate if needed)
            title = query[:50] + "..." if len(query) > 50 else query
            session.title = title
            session.save()
        
    except Exception as e:
        print(f"Error saving message: {e}")
    
    # Signal completion
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@login_required(login_url='/login/')
@csrf_exempt
@require_http_methods(["POST"])
def chat_stream(request):
    """Stream chat responses using Server-Sent Events"""
    try:
        data = json.loads(request.body)
        query = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not query:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)
        
        # Verify session belongs to user
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session'}, status=404)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=query
        )
        
        # Create streaming response
        response = StreamingHttpResponse(
            generate_response(query, session_id),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)