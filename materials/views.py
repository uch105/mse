from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from matscichat.models import Material, MaterialProperty


def materials_home(request):
    """Main materials page with periodic table and search"""
    return render(request, 'materials/home.html')


def search_materials(request):
    """AJAX search for materials"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search in name, other_names, category, description
    materials = Material.objects.filter(
        Q(name__icontains=query) |
        Q(other_names__icontains=query) |
        Q(category__icontains=query) |
        Q(description__icontains=query)
    )[:20]
    
    results = [{
        'id': mat.id,
        'name': mat.name,
        'category': mat.category,
        'description': mat.description[:100] + '...' if mat.description and len(mat.description) > 100 else mat.description or ''
    } for mat in materials]
    
    return JsonResponse({'results': results})


def material_detail(request, material_id):
    """Detailed view of a specific material"""
    material = get_object_or_404(Material, id=material_id)
    
    # Get all additional properties and format them
    properties_raw = MaterialProperty.objects.filter(material=material)
    properties = []
    for prop in properties_raw:
        properties.append({
            'key_display': prop.key.replace('_', ' ').title(),
            'key': prop.key,
            'float_value': prop.float_value,
            'text_value': prop.text_value
        })
    
    # Get environment compatibility
    from matscichat.models import MaterialEnvironmentCompatibility
    compatibilities = MaterialEnvironmentCompatibility.objects.filter(
        material=material
    ).select_related('environment')
    
    # Get application compatibility
    from matscichat.models import MaterialApplicationCompatibility
    applications = MaterialApplicationCompatibility.objects.filter(
        material=material
    ).select_related('application')
    
    context = {
        'material': material,
        'properties': properties,
        'compatibilities': compatibilities,
        'applications': applications,
    }
    
    return render(request, 'materials/detail.html', context)


def element_detail(request, symbol):
    """Show materials related to a specific element"""
    # Search for materials containing the element
    materials = Material.objects.filter(
        Q(name=symbol) |
        Q(other_names=symbol)
    )
    
    context = {
        'symbol': symbol,
        'materials': materials,
    }
    
    return render(request, 'materials/element_detail.html', context)