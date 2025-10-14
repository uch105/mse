from django.shortcuts import render

def matscichat(request):
    context = {}
    return render(request, 'matscichat/matscichat.html', context)