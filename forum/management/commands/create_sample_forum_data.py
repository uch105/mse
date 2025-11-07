"""
Management command to create sample forum data for testing.
Place this file in: forum/management/commands/create_sample_forum_data.py

Run with: python manage.py create_sample_forum_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Tag, Topic, Reply, UserProfile
import random


class Command(BaseCommand):
    help = 'Creates sample forum data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample forum data...')
        
        # Create categories
        categories_data = [
            {'name': 'Announcements', 'icon': '📢', 'color': '#667eea', 'description': 'Official announcements and news'},
            {'name': 'General Discussion', 'icon': '💬', 'color': '#764ba2', 'description': 'General materials science discussions'},
            {'name': 'Technical Support', 'icon': '🔧', 'color': '#f093fb', 'description': 'Get help with technical issues'},
            {'name': 'Research & Development', 'icon': '🔬', 'color': '#4facfe', 'description': 'Share your research and findings'},
            {'name': 'Career & Education', 'icon': '🎓', 'color': '#43e97b', 'description': 'Career advice and educational resources'},
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
        
        # Create tags
        tags_data = ['bug', 'feature', 'question', 'discussion', 'help-wanted', 
                     'polymers', 'ceramics', 'metals', 'composites', 'nanomaterials',
                     'characterization', 'processing', 'simulation', 'testing']
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        self.stdout.write(f'  Created/found {len(tags)} tags')
        
        # Create sample users if they don't exist
        users = []
        for i in range(1, 6):
            username = f'testuser{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Test',
                    'last_name': f'User {i}'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        self.stdout.write(f'  Created/found {len(users)} test users')
        
        # Create sample topics
        topics_data = [
            {
                'title': 'Welcome to MatSci Hub Forum!',
                'content': '''Hello everyone! 👋

We're thrilled to launch our new community forum. This platform has been designed to foster collaboration, knowledge sharing, and innovation in materials science.

**What's New?**
- Enhanced discussion features
- Better organization with categories
- Advanced search capabilities
- User profiles and reputation system

**Community Guidelines**
Please remember to be respectful, stay on topic, and cite your sources when sharing research.

Looking forward to great discussions!''',
                'category': categories[0],
                'tags': ['announcements', 'community'],
                'is_pinned': True,
            },
            {
                'title': 'Best practices for polymer characterization?',
                'content': '''I'm working on characterizing a new polymer blend and would love to hear about your experiences.

What techniques do you find most useful for determining:
- Molecular weight distribution
- Thermal properties
- Mechanical behavior
- Morphology

Any recommendations for equipment or protocols would be greatly appreciated!''',
                'category': categories[1],
                'tags': ['polymers', 'characterization', 'question'],
            },
            {
                'title': 'Issue with XRD pattern interpretation',
                'content': '''I'm getting some unusual peaks in my XRD pattern that I can't identify. The material is supposed to be single-phase, but I'm seeing additional peaks at 2θ = 28° and 32°.

Has anyone encountered something similar? Could this be an impurity or instrumental artifact?

Sample preparation: powder, Cu Kα radiation, 2θ range 10-80°''',
                'category': categories[2],
                'tags': ['help-wanted', 'characterization', 'xrd'],
            },
            {
                'title': 'New method for nanoparticle synthesis',
                'content': '''Our lab has developed a novel sol-gel method for synthesizing uniform metal oxide nanoparticles. We're seeing much better size control compared to traditional methods.

Key advantages:
- Room temperature synthesis
- Narrow size distribution (±2nm)
- Scalable process
- Lower cost

Would love to discuss potential applications and get feedback from the community!''',
                'category': categories[3],
                'tags': ['nanomaterials', 'research', 'synthesis'],
            },
            {
                'title': 'Career advice: Industry vs Academia',
                'content': '''I'm finishing up my PhD in materials science and trying to decide between pursuing a postdoc or going into industry.

For those who have made this decision, what factors did you consider? Any advice for someone trying to figure out the right path?

My research interests are in biomaterials and drug delivery systems.''',
                'category': categories[4],
                'tags': ['career', 'advice', 'discussion'],
            },
        ]
        
        created_topics = []
        for i, topic_data in enumerate(topics_data):
            topic, created = Topic.objects.get_or_create(
                title=topic_data['title'],
                defaults={
                    'content': topic_data['content'],
                    'author': random.choice(users),
                    'category': topic_data['category'],
                    'is_pinned': topic_data.get('is_pinned', False),
                    'views': random.randint(50, 500)
                }
            )
            
            if created:
                # Add tags
                for tag_name in topic_data.get('tags', []):
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    topic.tags.add(tag)
                
                # Add some random upvotes
                voters = random.sample(users, random.randint(1, 4))
                for voter in voters:
                    topic.upvotes.add(voter)
            
            created_topics.append(topic)
            self.stdout.write(f'  {"Created" if created else "Found"} topic: {topic.title}')
        
        # Create sample replies
        replies_data = [
            "This is fantastic! Really excited to be part of this community.",
            "Great question! I've had similar experiences with polymer characterization.",
            "Have you tried using GPC for molecular weight determination? It's been very reliable for me.",
            "Those peaks might be from an oxide layer. What's your sample storage condition?",
            "This research looks promising! Have you published any papers on this?",
            "I went the industry route and it's been great. Happy to discuss more!",
            "Academia offers more freedom but industry has better resources in my experience.",
            "Thanks for sharing! Will definitely try this method in our lab.",
        ]
        
        reply_count = 0
        for topic in created_topics:
            # Add 2-5 replies to each topic
            num_replies = random.randint(2, 5)
            for j in range(num_replies):
                reply_content = random.choice(replies_data)
                reply, created = Reply.objects.get_or_create(
                    topic=topic,
                    content=reply_content + f" (Reply {j+1})",
                    defaults={
                        'author': random.choice(users)
                    }
                )
                
                if created:
                    # Add some random upvotes to replies
                    voters = random.sample(users, random.randint(0, 3))
                    for voter in voters:
                        reply.upvotes.add(voter)
                    
                    reply_count += 1
        
        self.stdout.write(f'  Created {reply_count} replies')
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Categories: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'Tags: {len(tags)}'))
        self.stdout.write(self.style.SUCCESS(f'Topics: {len(created_topics)}'))
        self.stdout.write(self.style.SUCCESS(f'Replies: {reply_count}'))
        self.stdout.write(self.style.SUCCESS(f'Test Users: {len(users)} (password: password123)'))