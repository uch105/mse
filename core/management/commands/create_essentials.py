from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Creates sample forum data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample categories for forum...')

        categories_data = [
            {'name': 'Announcements', 'icon': '📢', 'color': '#667eea', 'description': 'Official announcements and news'},
            {'name': 'General Discussion', 'icon': '💬', 'color': '#764ba2', 'description': 'General materials science discussions'},
            {'name': 'Technical Support', 'icon': '🔧', 'color': '#f093fb', 'description': 'Get help with technical issues'},
            {'name': 'Research & Development', 'icon': '🔬', 'color': '#4facfe', 'description': 'Share your research and findings'},
            {'name': 'Education', 'icon': '🎓', 'color': '#43e97b', 'description': 'Career advice and educational resources'},
            {'name': 'Feedback & Suggestions', 'icon': '💡', 'color': '#FFD700', 'description': 'Share ideas and feedback to improve the platform'},
            {'name': 'Career Opportunities', 'icon': '💼', 'color': '#FF5733', 'description': 'Job postings, internships, and career advice'},
            {'name': 'Learning Resources', 'icon': '📚', 'color': '#33FF57', 'description': 'Share tutorials, papers, and educational content'},
            {'name': 'Off-Topic Lounge', 'icon': '🧋', 'color': '#AAAAAA', 'description': 'Casual conversations about non-materials topics'}
        ]
        
        categories = []
        for i, cat_data in enumerate(categories_data):
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'description': cat_data['description'],
                    'order': i
                }
            )
            categories.append(cat)
            self.stdout.write(f'  {"Created" if created else "Found"} category: {cat.name}')

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Categories: {len(categories)}'))