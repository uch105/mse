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