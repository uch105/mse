# Copyright 2025 Tanvir Saklan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import FileExtensionValidator

# ===========================================
# Forum Models
# ===========================================

import uuid

User = get_user_model()

# ===========================================
# Profile Details
# ===========================================

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    linkedin = models.TextField(blank=True)
    institution = models.CharField(max_length=200, blank=True,default="No institution provided")
    degree = models.CharField(max_length=100, blank=True, default="No degree provided")
    specialization = models.CharField(max_length=150, blank=True,default="No specialization provided")
    bio = models.TextField(blank=True,default="No bio provided")
    country = models.CharField(max_length=100, blank=True,default="No country provided")

    # --- Interests & Skills ---
    research_interests = models.TextField(blank=True,help_text="Comma-separated interests e.g. Nanomaterials, Thermodynamics, Polymers")
    skills = models.TextField(max_length=255, blank=True, help_text="Comma-separated skills e.g. Python, MATLAB, SEM, XRD")

    # --- Contribution Metrics ---
    materials_added = models.PositiveIntegerField(default=0)
    datasets_uploaded = models.PositiveIntegerField(default=0)
    forum_posts = models.PositiveIntegerField(default=0)
    forum_comments = models.PositiveIntegerField(default=0)
    blogs_published = models.PositiveIntegerField(default=0)
    books_contributed = models.PositiveIntegerField(default=0)
    ai_queries = models.PositiveIntegerField(default=0)
    api_contributions = models.PositiveIntegerField(default=0)

    # --- Scoring System ---
    score = models.FloatField(default=0)
    level = models.CharField(max_length=50, default="Beginner")

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def interest_list(self):
        return [i.strip() for i in self.research_interests.split(",") if i.strip()]
    
    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def calculate_score(self):
        """Weighted scoring system for contributions"""
        self.score = (
            self.materials_added * 5 +
            self.datasets_uploaded * 10 +
            self.forum_posts * 2 +
            self.forum_comments * 1 +
            self.blogs_published * 8 +
            self.books_contributed * 6 +
            self.api_contributions * 12 +
            self.ai_queries * 0.5
        )
        self._update_level()
        self.save()

    def _update_level(self):
        """Define level thresholds"""
        if self.score < 50:
            self.level = "Beginner"
        elif self.score < 200:
            self.level = "Explorer"
        elif self.score < 500:
            self.level = "Contributor"
        elif self.score < 1000:
            self.level = "Expert"
        else:
            self.level = "Research Master"

    def __str__(self):
        return f"Profile of {self.full_name} - ({self.user.email})"

# ===========================================
# Material's Database Models
# ===========================================
"""
class Material(models.Model):
    name = models.CharField(max_length=200, unique=True)
    other_names = models.TextField(blank=True, help_text="Industrial nicknames, trade names, or abbreviations")
    description = models.TextField(blank=True, help_text="General description of the material")

    def __str__(self):
        return self.name


# --------------------
# Mechanical Properties
# --------------------
class MechanicalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="mechanical_properties")
    youngs_modulus = models.FloatField(null=True, blank=True, help_text="GPa")
    tensile_strength = models.FloatField(null=True, blank=True, help_text="MPa")
    yield_strength = models.FloatField(null=True, blank=True, help_text="MPa")
    hardness = models.FloatField(null=True, blank=True, help_text="Vickers / Mohs / Brinell")
    fracture_toughness = models.FloatField(null=True, blank=True, help_text="MPa·m^0.5")
    fatigue_strength = models.FloatField(null=True, blank=True, help_text="MPa")
    poisson_ratio = models.FloatField(null=True, blank=True)
    elongation = models.FloatField(null=True, blank=True, help_text="%")
    creep_resistance = models.TextField(blank=True, help_text="Qualitative or quantitative creep resistance data")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Mechanical Properties of {self.material.name}"


# --------------------
# Optical Properties
# --------------------
class OpticalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="optical_properties")
    refractive_index = models.FloatField(null=True, blank=True)
    absorption_coefficient = models.FloatField(null=True, blank=True, help_text="cm^-1")
    transmission = models.FloatField(null=True, blank=True, help_text="%")
    reflectivity = models.FloatField(null=True, blank=True, help_text="%")
    bandgap = models.FloatField(null=True, blank=True, help_text="eV")
    color = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Optical Properties of {self.material.name}"


# --------------------
# Electrical Properties
# --------------------
class ElectricalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="electrical_properties")
    conductivity = models.FloatField(null=True, blank=True, help_text="S/m")
    resistivity = models.FloatField(null=True, blank=True, help_text="Ω·m")
    dielectric_constant = models.FloatField(null=True, blank=True)
    breakdown_voltage = models.FloatField(null=True, blank=True, help_text="kV/mm")
    electron_mobility = models.FloatField(null=True, blank=True, help_text="cm^2/V·s")
    superconducting_temp = models.FloatField(null=True, blank=True, help_text="K")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Electrical Properties of {self.material.name}"


# --------------------
# Magnetic Properties
# --------------------
class MagneticProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="magnetic_properties")
    magnetic_susceptibility = models.FloatField(null=True, blank=True)
    saturation_magnetization = models.FloatField(null=True, blank=True, help_text="emu/g")
    coercivity = models.FloatField(null=True, blank=True, help_text="Oe")
    remanence = models.FloatField(null=True, blank=True, help_text="T")
    curie_temperature = models.FloatField(null=True, blank=True, help_text="K")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Magnetic Properties of {self.material.name}"


# --------------------
# Chemical Properties
# --------------------
class ChemicalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="chemical_properties")
    composition = models.TextField(blank=True, help_text="Atomic % or wt% composition")
    corrosion_resistance = models.TextField(blank=True)
    oxidation_resistance = models.TextField(blank=True)
    reactivity = models.TextField(blank=True)
    chemical_stability = models.TextField(blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Chemical Properties of {self.material.name}"


# --------------------
# Thermal Properties
# --------------------
class ThermalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="thermal_properties")
    thermal_conductivity = models.FloatField(null=True, blank=True, help_text="W/m·K")
    thermal_expansion = models.FloatField(null=True, blank=True, help_text="ppm/K")
    specific_heat = models.FloatField(null=True, blank=True, help_text="J/kg·K")
    melting_point = models.FloatField(null=True, blank=True, help_text="°C")
    boiling_point = models.FloatField(null=True, blank=True, help_text="°C")
    glass_transition_temp = models.FloatField(null=True, blank=True, help_text="°C (for polymers)")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Thermal Properties of {self.material.name}"


# --------------------
# Physical Properties
# --------------------
class PhysicalProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="physical_properties")
    density = models.FloatField(null=True, blank=True, help_text="g/cm³")
    crystal_structure = models.CharField(max_length=100, blank=True)
    grain_size = models.FloatField(null=True, blank=True, help_text="μm")
    porosity = models.FloatField(null=True, blank=True, help_text="%")
    phase = models.CharField(max_length=100, blank=True, help_text="solid/liquid/gas/amorphous")
    color = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Physical Properties of {self.material.name}"


# --------------------
# Acoustic Properties
# --------------------
class AcousticProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="acoustic_properties")
    sound_velocity = models.FloatField(null=True, blank=True, help_text="m/s")
    acoustic_impedance = models.FloatField(null=True, blank=True, help_text="Rayl")
    damping_coefficient = models.FloatField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Acoustic Properties of {self.material.name}"


# --------------------
# Atomic Properties
# --------------------
class AtomicProperties(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="atomic_properties")
    atomic_number = models.IntegerField(null=True, blank=True)
    atomic_weight = models.FloatField(null=True, blank=True)
    electronic_configuration = models.CharField(max_length=200, blank=True)
    valence_electrons = models.IntegerField(null=True, blank=True)
    bonding_type = models.CharField(max_length=100, blank=True)
    lattice_parameter = models.FloatField(null=True, blank=True, help_text="Å")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Atomic Properties of {self.material.name}"

# ===========================================
# Environment Database Models
# ===========================================

class UsageEnvironment(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="Canonical name of environment (e.g., Aircraft)")
    other_names = models.TextField(blank=True, help_text="Comma-separated synonyms/aliases (e.g., Aerospace, Aero craft, Airplane)")
    properties = models.TextField(blank=True, help_text="Comma-separated list of important properties (e.g., strength, corrosion resistance, thermal expansion)")
    description = models.TextField(blank=True, help_text="Optional description of this environment or usage")
    note = models.TextField(blank=True, help_text="Special notes or exceptions")

    def __str__(self):
        return self.name

    def get_other_names(self):
        return [n.strip() for n in self.other_names.split(",") if n.strip()]

    def get_properties(self):
        return [p.strip() for p in self.properties.split(",") if p.strip()]


# ===========================================
# Resources, Books & Software
# ===========================================

class Resource(models.Model):
    RESOURCE_TYPE = [
        ("book", "Book"),
        ("software", "Software"),
        ("dataset", "Dataset"),
        ("other", "Other"),
    ]
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=64, choices=RESOURCE_TYPE)
    description = models.TextField(blank=True, help_text="Brief description of the resource")
    link = models.URLField(blank=True)
    file = models.FileField(upload_to="resources/", null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    uploader = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_resources")
    tags = models.TextField(blank=True, help_text="Comma-separated list of resource category (e.g., Software, Book, Dataset etc)")

    def __str__(self):
        return self.title

"""
# ===========================================
# Press Releases
# ===========================================

class PressRelease(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Partnership, Product Launch, Event")
    disclaimer = models.TextField(blank=True, help_text="Optional legal disclaimer or note")
    content = models.TextField(blank=True)
    meta_tags = models.TextField(blank=True, help_text="Comma-separated meta tags for SEO")
    published_at = models.DateTimeField(auto_now_add=True)

    @property
    def tag_list(self):
        return [t.strip() for t in self.meta_tags.split(',')]

    def __str__(self):
        return self.title

# ===========================================
# Careers
# ===========================================

class Career(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    key_responsibilities = models.TextField(blank=True, help_text="Comma-separated list of key responsibilities")
    qualifications = models.TextField(blank=True, help_text="Comma-separated list of required qualifications")
    compensation = models.TextField(blank=True, help_text="e.g., Salary range, benefits")
    location = models.CharField(max_length=255, blank=True)
    job_type = models.CharField(max_length=100, blank=True, help_text="e.g., Engineering, Research, Marketing")
    employment_type = models.CharField(max_length=50, blank=True, help_text="e.g., Remote, Urgent")
    posted_at = models.DateTimeField(auto_now_add=True)
    application_deadline = models.CharField(max_length=255, blank=True)
    job_tags = models.TextField(blank=True, help_text="Comma-separated list of job tags (e.g., Python, ML, Data Science)")
    accepting = models.BooleanField(default=True, help_text="Is this position currently accepting applications?")

    def __str__(self):
        return self.title
    
    @property
    def tag_list(self):
        return [t.strip() for t in self.job_tags.split(',')]

class CareerApplication(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="career_applications")
    phone = models.CharField(max_length=20, blank=True)
    resume = models.FileField(upload_to="careers/resumes/", null=True, blank=True)
    links = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.email} - {self.career.title}"
    
# ===========================================
# Team Members
# ===========================================

class TeamMember(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="team_member")
    role = models.CharField(max_length=100, blank=True, help_text="e.g., Founder, Advisor, Developer")
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.full_name} - {self.role}"



# ===========================================
# Blogs Section
# ===========================================


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='blogs')
    
    # Meta Information
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description (max 300 chars)")
    
    # Content
    content = models.TextField(help_text="Main blog content with HTML support")
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=250, blank=True)
    
    # Status & Analytics
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Featured & Trending
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-calculate read time based on content
        if self.content:
            word_count = len(self.content.split())
            self.read_time = max(1, word_count // 200)  # Average reading speed: 200 words/min
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def __str__(self):
        return self.title


class BlogSection(models.Model):
    SECTION_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('quote', 'Quote'),
        ('code', 'Code'),
    ]

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=10, choices=SECTION_TYPES, default='text')
    order = models.PositiveIntegerField(default=0)
    
    # Content fields
    title = models.CharField(max_length=250, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog_sections/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.blog.title} - Section {self.order}"


class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

    def get_replies(self):
        return BlogComment.objects.filter(parent=self, is_approved=True)


class BlogShare(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    platform = models.CharField(max_length=50)  # facebook, twitter, linkedin, etc.
    shared_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-shared_at']

    def __str__(self):
        return f"{self.blog.title} shared on {self.platform}"
    




# ===========================================
# Forum Models
# ===========================================

class Category(models.Model):
    """Forum categories for organizing topics"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#667eea')  # Hex color
    icon = models.CharField(max_length=50, default='💬')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:category', kwargs={'slug': self.slug})
    
    def topic_count(self):
        return self.topics.count()
    
    def post_count(self):
        return sum(topic.replies.count() + 1 for topic in self.topics.all())


class Tag(models.Model):
    """Tags for topics"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:tag', kwargs={'slug': self.slug})


class Topic(models.Model):
    """Forum topics/threads"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    tags = models.ManyToManyField(Tag, blank=True, related_name='topics')
    
    # Status fields
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_solved = models.BooleanField(default=False)
    
    # Engagement fields
    views = models.PositiveIntegerField(default=0)
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvoted_topics')
    downvotes = models.ManyToManyField(User, blank=True, related_name='downvoted_topics')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['-last_activity']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_pinned', '-last_activity']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Topic.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'slug': self.slug})
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def reply_count(self):
        return self.replies.count()
    
    def get_excerpt(self, length=150):
        """Get a truncated excerpt of the content"""
        if len(self.content) > length:
            return self.content[:length] + '...'
        return self.content
    
    def has_media_attachments(self):
        """Check if topic has any media attachments"""
        return self.attachments.exists()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class Reply(models.Model):
    """Replies/comments to topics"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Engagement fields
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvoted_replies')
    downvotes = models.ManyToManyField(User, blank=True, related_name='downvoted_replies')
    
    # Status
    is_solution = models.BooleanField(default=False)  # Mark as solution to the topic
    is_edited = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Replies'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['topic', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author.username} on {self.topic.title}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Update topic's last activity when a reply is added
        if is_new:
            self.topic.update_activity()
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def get_nested_replies(self):
        """Get all nested replies (children)"""
        return self.children.all()
    
    def has_replies(self):
        """Check if this reply has any children"""
        return self.children.exists()


class Attachment(models.Model):
    """File attachments for topics"""
    ATTACHMENT_TYPES = (
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('other', 'Other'),
    )
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='forum/attachments/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='other')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.topic.title}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            
            # Determine file type based on extension
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            elif ext in ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx']:
                self.file_type = 'document'
            elif ext in ['mp4', 'avi', 'mov', 'webm']:
                self.file_type = 'video'
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Convert bytes to human readable format"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.2f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.2f} MB"


class UserProfile(models.Model):
    """Extended user profile for forum"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_profile')
    avatar = models.ImageField(upload_to='forum/avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    reputation = models.IntegerField(default=0)

    email_notifications = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-reputation']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        """Return forum avatar, or fallback to profile picture, or default"""
        if self.avatar:
            return self.avatar.url
        elif hasattr(self.user, "profile") and self.user.profile.profile_picture:
            return self.user.profile.profile_picture.url
        else:
            return ''
    
    def get_display_name(self):
        """Get user's display name"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    def topic_count(self):
        return self.user.forum_topics.count()
    
    def reply_count(self):
        return self.user.forum_replies.count()
    
    def total_posts(self):
        return self.topic_count() + self.reply_count()


class Bookmark(models.Model):
    """User bookmarks for topics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_bookmarks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.topic.title}"


class Report(models.Model):
    """Report system for inappropriate content"""
    REPORT_TYPES = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('off_topic', 'Off Topic'),
        ('other', 'Other'),
    )
    
    REPORT_STATUS = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_reports_made')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    
    # Moderation
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_reports_reviewed')
    moderator_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.topic:
            return f"Report on topic: {self.topic.title}"
        elif self.reply:
            return f"Report on reply by {self.reply.author.username}"
        return f"Report by {self.reporter.username}"