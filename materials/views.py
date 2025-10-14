from django.shortcuts import render

def materials(request):
    context = {}
    return render(request, 'materials/materials.html', context)