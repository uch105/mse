from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()


class ChatSession(models.Model):
    """Represents a chat conversation session"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Individual messages in a chat session"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    intent = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    entities = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.session.id} - {self.role}: {self.content[:50]}"
    
# ===========================================
# Material's Database Models
# ===========================================



class Material(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    other_names = models.TextField(blank=True, help_text="Comma-separated synonyms")

    category = models.CharField(max_length=100, db_index=True)

    # Commonly filtered properties (indexed for speed)
    density = models.FloatField(null=True, db_index=True)
    tensile_strength = models.FloatField(null=True, db_index=True)
    melting_point = models.FloatField(null=True, db_index=True)
    thermal_conductivity = models.FloatField(null=True, db_index=True)
    corrosion_resistance_score = models.FloatField(null=True, db_index=True)

    # Full property set (optional, non-indexed)
    raw_properties = JSONField(default=dict)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class MaterialProperty(models.Model):
    """
    Highly scalable key-value store for property queries.
    Allows indexing ANY property without JSON lookups.
    """
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="properties")

    key = models.CharField(max_length=200, db_index=True)
    float_value = models.FloatField(null=True, db_index=True)
    text_value = models.TextField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["key", "float_value"]),
            models.Index(fields=["key"]),
        ]


class Environment(models.Model):
    name = models.CharField(max_length=200, unique=True)
    other_names = models.TextField(blank=True, help_text="Comma-separated synonyms")
    properties = JSONField(default=dict)
    description = models.TextField(blank=True, null=True)


class Application(models.Model):
    name = models.CharField(max_length=200, unique=True)
    other_names = models.TextField(blank=True, help_text="Comma-separated synonyms")
    performance_requirements = JSONField(default=dict)
    description = models.TextField(blank=True, null=True)


class MaterialEnvironmentCompatibility(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    compatibility_score = models.FloatField(db_index=True)
    degradation_behavior = models.TextField(null=True, blank=True)


class MaterialApplicationCompatibility(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    suitability_score = models.FloatField(db_index=True)
    reasons = models.TextField(blank=True, null=True)