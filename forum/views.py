from django.shortcuts import render

def forum(request):
    context = {}
    return render(request, 'forum/forum.html', context)