from django.shortcuts import render

def blogs(request):
    context = {}
    return render(request, 'blogs/blogs.html', context)