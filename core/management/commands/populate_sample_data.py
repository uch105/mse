from django.core.management.base import BaseCommand
from matscichat.models import (
    Material, MaterialProperty, Environment,
    MaterialEnvironmentCompatibility
)


class Command(BaseCommand):
    help = 'Populate sample materials data for testing MatSciChat'

    def handle(self, *args, **options):
        self.stdout.write('Populating materials database...')
        
        # Create Steel
        steel, created = Material.objects.get_or_create(
            name="Steel",
            defaults={
                'category': 'Metal',
                'density': 7.85,
                'tensile_strength': 400,
                'melting_point': 1370,
                'thermal_conductivity': 50,
                'corrosion_resistance_score': 4,
                'description': 'Iron-carbon alloy widely used in construction and manufacturing'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {steel.name}'))
            
            # Add properties
            MaterialProperty.objects.create(
                material=steel,
                key='strength_to_weight_ratio',
                float_value=51.0
            )
            MaterialProperty.objects.create(
                material=steel,
                key='fatigue_resistance',
                float_value=7.5
            )
            MaterialProperty.objects.create(
                material=steel,
                key='galvanic_corrosion_potential',
                float_value=-0.6
            )
            MaterialProperty.objects.create(
                material=steel,
                key='cost_per_kg',
                float_value=0.80
            )
            MaterialProperty.objects.create(
                material=steel,
                key='electrochemical_corrosion_rate',
                float_value=0.15  # mm/year
            )
            MaterialProperty.objects.create(
                material=steel,
                key='passivation_tendency',
                float_value=3.0
            )
            MaterialProperty.objects.create(
                material=steel,
                key='microstructure_stability',
                float_value=6.0
            )
            MaterialProperty.objects.create(
                material=steel,
                key='coating_adhesion',
                float_value=8.0
            )
        
        # Create Aluminum
        aluminum, created = Material.objects.get_or_create(
            name="Aluminum",
            defaults={
                'other_names': 'Aluminium',
                'category': 'Metal',
                'density': 2.70,
                'tensile_strength': 310,
                'melting_point': 660,
                'thermal_conductivity': 237,
                'corrosion_resistance_score': 7,
                'description': 'Lightweight silvery-white metal with excellent corrosion resistance'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {aluminum.name}'))
            
            # Add properties
            MaterialProperty.objects.create(
                material=aluminum,
                key='strength_to_weight_ratio',
                float_value=115.0
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='fatigue_resistance',
                float_value=6.0
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='galvanic_corrosion_potential',
                float_value=-1.66
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='cost_per_kg',
                float_value=2.50
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='electrochemical_corrosion_rate',
                float_value=0.03  # mm/year
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='passivation_tendency',
                float_value=8.5
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='microstructure_stability',
                float_value=7.5
            )
            MaterialProperty.objects.create(
                material=aluminum,
                key='coating_adhesion',
                float_value=7.0
            )
        
        # Create Seawater Environment
        seawater, created = Environment.objects.get_or_create(
            name="Seawater",
            defaults={
                'other_names': 'saltwater, ocean, marine',
                'description': 'Highly corrosive marine environment with 3.5% salinity',
                'properties': {
                    'salinity': '3.5%',
                    'pH': '8.1',
                    'temperature_range': '0-30°C',
                    'dissolved_oxygen': '5-8 mg/L'
                }
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {seawater.name} environment'))
        
        # Create Material-Environment Compatibility for Steel
        steel_seawater, created = MaterialEnvironmentCompatibility.objects.get_or_create(
            material=steel,
            environment=seawater,
            defaults={
                'compatibility_score': 4.0,
                'degradation_behavior': (
                    'Steel undergoes rapid electrochemical corrosion in seawater. '
                    'Forms iron oxide (rust) leading to material loss. '
                    'Galvanic corrosion accelerates when coupled with noble metals. '
                    'Requires protective coatings (paint, galvanization) and cathodic protection. '
                    'Expected corrosion rate: 0.1-0.2 mm/year without protection.'
                )
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Steel-Seawater compatibility'))
        
        # Create Material-Environment Compatibility for Aluminum
        aluminum_seawater, created = MaterialEnvironmentCompatibility.objects.get_or_create(
            material=aluminum,
            environment=seawater,
            defaults={
                'compatibility_score': 7.0,
                'degradation_behavior': (
                    'Aluminum forms a protective aluminum oxide layer (passivation) in seawater. '
                    'Good general corrosion resistance but susceptible to pitting corrosion in chloride environments. '
                    'Galvanic corrosion risk when coupled with more noble metals (steel, copper). '
                    'Marine-grade alloys (5xxx, 6xxx series) perform better. '
                    'Expected corrosion rate: 0.02-0.05 mm/year with proper alloy selection.'
                )
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Aluminum-Seawater compatibility'))
        
        # Add more materials
        titanium, created = Material.objects.get_or_create(
            name="Titanium",
            defaults={
                'category': 'Metal',
                'density': 4.51,
                'tensile_strength': 900,
                'melting_point': 1668,
                'thermal_conductivity': 21.9,
                'corrosion_resistance_score': 9,
                'description': 'High-strength, low-density metal with exceptional corrosion resistance'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {titanium.name}'))
        
        copper, created = Material.objects.get_or_create(
            name="Copper",
            defaults={
                'category': 'Metal',
                'density': 8.96,
                'tensile_strength': 220,
                'melting_point': 1085,
                'thermal_conductivity': 401,
                'corrosion_resistance_score': 6,
                'description': 'Excellent electrical and thermal conductor'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {copper.name}'))
        
        stainless_steel, created = Material.objects.get_or_create(
            name="Stainless Steel",
            defaults={
                'other_names': '316 stainless, 304 stainless',
                'category': 'Metal',
                'density': 8.00,
                'tensile_strength': 515,
                'melting_point': 1400,
                'thermal_conductivity': 16.2,
                'corrosion_resistance_score': 8,
                'description': 'Chromium-alloyed steel with superior corrosion resistance'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {stainless_steel.name}'))
            
            # Stainless Steel properties
            MaterialProperty.objects.create(
                material=stainless_steel,
                key='strength_to_weight_ratio',
                float_value=64.0
            )
            MaterialProperty.objects.create(
                material=stainless_steel,
                key='fatigue_resistance',
                float_value=8.0
            )
            MaterialProperty.objects.create(
                material=stainless_steel,
                key='electrochemical_corrosion_rate',
                float_value=0.01
            )
            MaterialProperty.objects.create(
                material=stainless_steel,
                key='passivation_tendency',
                float_value=9.0
            )
            MaterialProperty.objects.create(
                material=stainless_steel,
                key='cost_per_kg',
                float_value=3.50
            )
            
            # Stainless Steel - Seawater compatibility
            MaterialEnvironmentCompatibility.objects.get_or_create(
                material=stainless_steel,
                environment=seawater,
                defaults={
                    'compatibility_score': 8.5,
                    'degradation_behavior': (
                        '316 stainless steel performs excellently in seawater due to molybdenum content. '
                        'Forms stable chromium oxide passive layer. Resistant to pitting and crevice corrosion. '
                        'Expected corrosion rate: <0.01 mm/year. Excellent choice for marine applications.'
                    )
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Database population complete!'))
        self.stdout.write(self.style.SUCCESS('You can now test MatSciChat with queries like:'))
        self.stdout.write('  "Compare steel and aluminum for seawater usage. Which will corrode faster?"')