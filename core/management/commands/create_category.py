from django.core.management.base import BaseCommand
from core.models import Category, Tag

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

        tags_data = ['bug', 'feature', 'question', 'discussion', 'help-wanted', 
                     'polymers', 'ceramics', 'metals', 'composites', 'nanomaterials',
                     'characterization', 'processing', 'simulation', 'testing']
        
        tags_data += [
            'alloys', 'graphene', 'semiconductors', 'superconductors', 'polymer-composites',
            'nanotubes', 'material-synthesis', 'surface-engineering', 'metallurgy', 'nanostructures',
            'thermal-conductivity', 'mechanical-properties', 'electrical-properties', 'optical-properties',
            'magnetic-materials', 'thin-films', 'advanced-materials', 'additive-manufacturing', '3d-printing',
            'molecular-dynamics', 'crystallography', 'electrochemistry', 'ceramic-materials', 'corrosion',
            'biomaterials', 'photonic-materials', 'smart-materials', 'lightweight-materials', 'high-performance-materials',
            'environmental-materials', 'recyclable-materials', 'sustainable-materials', 'materials-characterization',
            'fracture-mechanics', 'dynamic-mechanics', 'hydrogels', 'polymer-blends', 'nanoparticles',
            'nanocomposites', 'piezoelectric-materials', 'superalloys', 'energy-storage', 'battery-materials',
            'fuel-cell-materials', 'solar-cells', 'semiconductor-fabrication', 'structural-materials',
            'failure-analysis', 'chemical-engineering', 'materials-design', 'material-properties', 'thermal-expansion',
            'conductive-polymers', 'high-strength-materials', 'composite-fabrication', 'nanoengineering',
            'electroplating', 'hydraulic-materials', 'phase-transitions', 'metals-processing', 'laser-materials-interactions',
            'fracture-toughness', 'plastics', 'bioengineering', 'organic-materials', 'high-temperature-materials',
            'bulk-materials', 'structural-composites', 'graphene-oxide', 'material-testing', '3D-structural-analysis',
            'conductive-materials', 'biodegradable-materials', 'carbon-nanotubes', 'thin-film-deposition', 'thermal-management',
            'materials-in-aviation', 'intelligent-materials', 'high-pressure-materials', 'chemomechanical-properties',
            'hydrodynamics', 'coatings', 'nanorods', 'electromagnetic-materials', 'microscale-materials', 'macroscale-materials',
            'nanoelectronics', 'graphene-based-materials', 'multifunctional-materials', 'alloy-design', 'organic-inorganic-hybrids',
            'surface-modification', 'laser-processing', 'sintering', 'bonding-techniques', 'advanced-composites',
            'light-emitting-materials', 'catalytic-materials', 'energy-harvesting', 'superplasticity', 'ceramic-matrix-composites',
            'metal-matrix-composites', 'polymer-matrix-composites', 'self-healing-materials', 'hydraulic-cements',
            'additive-fabrication', 'thermoplastics', 'thermosets', 'superconducting-materials', 'smart-coatings',
            'thermal-barrier-coatings', 'surface-science', 'metals-alloys', 'refractories', 'lightweight-alloys',
            'molecular-engineering', 'magnetic-alloys', 'nano-microscopy', 'molecular-scale-materials', 'chemical-vapor-deposition',
            'dental-materials', 'heat-treatment', 'oxidation-resistance', 'polymeric-materials', 'resilient-materials',
            'biocompatible-materials', 'nano-structured-coatings', 'nanocrystalline-materials', 'composite-matrices',
            'crystal-growth', 'materials-scaling', 'material-sustainability', 'synthetic-materials', 'antibacterial-materials',
            'thermal-stress', 'magnetic-polymers', 'superelastic-materials', 'reinforced-materials', 'high-entropy-alloys',
            'nano-coatings', 'industrial-materials', 'materials-recycling', 'composite-design', 'high-strength-steels',
            'semiconductor-materials', 'nano-structuring', 'phase-change-materials', 'dielectrics', 'shape-memory-materials',
            'nano-laminates', 'powder-metallurgy', 'thermal-insulation', 'hydrophobic-materials', 'transparent-conductors',
            'composite-particles', 'resistant-materials', 'toughness-enhancement', 'friction-materials', 'deformation-behavior',
            'material-interfaces', 'polymer-synthesis', 'nanocomposite-synthesis', 'environmentally-friendly-materials',
            'smart-textiles', 'atomic-scale-materials', 'magnetic-nanoparticles', 'heat-resistance', 'antioxidant-materials',
            'titanium-alloys', 'nanostructured-polymers', 'strengthening-mechanisms', 'elasticity-theory', 'composite-reinforcement',
            'conductive-polymers', 'nanoengineering-techniques', 'reliable-materials', 'organic-electronics',
            'aerogels', 'crystal-structure', 'metallurgical-engineering', 'mechanical-behavior', 'material-degradation',
            'bioinspired-materials', 'nano-composite-fabrication', 'ceramic-refractories', 'materials-chemistry', 'material-fabrication',
            'high-performance-composites', 'thermoplastic-composites', 'multiphase-materials', 'damage-tolerant-materials',
            'materials-science-modeling', 'toughened-materials', 'lightweight-structures', 'composite-fiber-reinforced',
            'atomistic-simulations', 'inorganic-materials', 'self-assembled-materials', 'carbon-based-materials',
            'composite-tubes', 'nano-adhesion', 'engineering-plastics', 'carbon-fiber', 'quantum-materials',
            'nanostructured-coatings', 'elasticity-mechanics', 'ceramic-coatings', 'material-fatigue', 'oxidation-resistant-alloys',
            'adhesive-bonding', 'advanced-ceramics', 'strength-of-materials', 'nanocomposites-in-engineering', 'biodegradable-polymers',
            'polymers-for-electronics', 'materials-mechanics', 'adhesive-materials', 'degradation-behavior', 'polymer-degradation',
            'fracture-surface-analysis', 'thermal-diffusivity', 'advanced-manufacturing', 'nano-alloying', 'stainless-steels',
            'smart-coating-applications', 'functionally-graded-materials', 'electronic-packaging', 'laser-sintering',
            'shape-memory-alloys', 'nanostructured-composites', 'high-performance-fibers', 'microfabrication', 'crack-propagation',
            'geopolymer-materials', 'environmentally-friendly-composites', 'bimetallic-alloys', 'nanocatalysis', 'tribology',
            'bulk-metal-glasses', 'pyrolysis-materials', 'nano-sponges', 'organic-inorganic-composites', 'graphene-based-composites',
            'piezoelectric-sensors', 'nanosensors', 'biomechanics', 'thermal-analysis', 'nano-magnetic-materials', 'processing-parameters',
            'green-materials', 'friction-wear', 'coating-application-techniques', 'self-repairing-materials', 'ceramic-fibers',
            'battery-storage-materials', 'thermochemical-materials', 'membrane-materials', 'friction-coefficients',
            'high-thermal-conductivity-materials', 'materials-fatigue', 'crack-healing', 'shape-memory-polymers', 'polymer-interfaces',
            'thermomechanical-properties', 'nanoscale-fabrication', 'high-performance-films', 'nano-fibers', 'smart-glass',
            'non-linear-materials', 'bulk-material-properties', 'semiconductor-devices', 'nanoelectronics-applications',
            'nano-lithography', 'fracture-dynamics', 'nanomechanics', 'microscale-testing', 'nanostructure-fabrication',
            'advanced-composites-manufacturing', 'brittle-materials', 'hybrid-materials', 'biocompatible-alloys',
            'adhesion-mechanisms', 'metals-matrix-composites', 'surface-properties', 'nanofabrication', 'materials-for-nuclear',
            'polymeric-nanocomposites', 'bio-nanomaterials', 'additive-materials', 'interfacial-materials', 'flexible-materials',
            'sensors-materials', 'membrane-filtration', 'dielectric-materials', 'smart-material-designs', 'magnetic-particles',
            'carbon-nano-onions', 'microstructure-engineering', 'hydrogen-storage-materials', 'hybrid-composites', 'ultra-lightweight-materials',
            'material-integrity', 'corrosion-resistant-coatings', 'thermal-stability', 'nano-structural-properties',
            'microwave-materials', 'functional-ceramics', 'bulk-materials-testing', 'molecular-modeling', 'structural-integrity',
            'metallic-coatings', 'automotive-materials', 'bioactive-materials', 'light-emitting-diodes', 'wear-resistant-materials',
            'toughness-characterization', 'multiphase-composites', 'nanostructured-alloys', 'polymer-nanofibers', 'advanced-alloys',
            'nano-patterning', 'energy-efficient-materials', 'self-assembled-nanomaterials', 'high-strength-composites'
        ]

        tags_data += [
            'biodegradable-composites', 'thermal-insulation', 'bioinorganic-materials', 'metal-organic-frameworks',
            'conductive-polymers', 'rechargeable-batteries', 'rechargeable-supercapacitors', 'nanosensors',
            'magnetoelectric-materials', 'wear-resistant-coatings', 'thermal-stress', 'refractory-materials',
            'magnetic-alloys', 'nanostructured-metals', 'mesoporous-silica', 'smart-glass', 'metallic-nanostructures',
            'surface-functionalization', 'biosensing', 'transparent-conducting-oxides', 'liquid-crystal-materials',
            'nanomaterial-synthesis', 'phase-change-materials', 'organic-inorganic-hybrids', 'composite-coatings',
            'graphene-based-materials', 'photoactive-materials', 'battery-materials', 'ionic-conductive-polymers',
            'oxidative-stability', 'nano-thin-films', 'alloy-design', 'submicron-particles', 'polymeric-nano-coatings',
            'carbon-fiber-reinforced-polymers', 'high-temperature-superconductors', 'nanorods', 'laser-material-interaction',
            'phase-transition-materials', 'thermoplastic-materials', 'polymer-blends', 'organic-light-emitting-materials',
            'nano-composite-films', 'polyelectrolytes', 'topology-optimized-materials', 'superplasticity', 'advanced-ceramics',
            'automotive-materials', 'thermal-barrier-coatings', 'sustainable-composites', 'water-repellent-materials',
            'high-energy-density-materials', 'multi-functional-nanomaterials', 'nano-scale-morphology', 'atomic-layer-deposition',
            'acoustic-materials', 'biopolymer-materials', 'layered-materials', 'surface-enhanced-raman-scattering',
            'thermal-shock-resistance', 'high-speed-rail-materials', 'catalytic-materials', 'nano-grains', 'nano-crystalline-materials',
            'photonic-crystals', 'oxide-semiconductors', 'hydrogen-bonded-materials', 'covalent-bonding-materials', 'tuning-material-properties',
            'piezoresistive-materials', 'graphene-oxide-composites', 'nanostructured-catalysts', 'electron-beam-evaporation',
            'self-assembling-polymers', 'superconducting-films', 'hydrophobic-coatings', 'memristors', 'quantum-dots-in-materials',
            'electromagnetic-interference-shielding', 'high-strength-composites', 'crystalline-materials-processing', 'liquid-metal-processing',
            'high-speed-materials-testing', 'nanoimprint-lithography', 'metal-organic-framework-synthesis', 'thin-film-solar-technologies',
            'catalytic-reaction-materials', 'hydrogen-absorbing-materials', 'electrolyte-materials', 'carbon-based-electrodes',
            'material-innovation', 'sensors-for-materials-characterization', 'nanoparticle-dispersion', 'ultra-light-materials', 
            'nano-composite-materials', 'high-performance-thin-films', 'light-emitting-nanomaterials', 'magnetic-field-modulated-materials',
            'bio-nanomaterials', 'high-temperature-materials', 'biocompatible-materials', 'scanning-electron-microscopy-materials',
            'plastic-deformation', 'sustainable-engineering-materials', 'nanotube-synthesis-techniques', 'advanced-electronic-materials',
            'multi-layered-coatings', 'high-resolution-imaging-materials', 'strong-light-absorbing-materials', 'materials-for-advanced-batteries',
            'conductive-carbon-materials', 'nano-carriers', 'mechanical-characterization-techniques', 'material-nano-engineering',
            'surface-improvement', 'polymer-coating-materials', 'multi-phase-materials', 'high-performance-metal-alloys',
            'nanostructured-ceramics', 'nano-alloy-synthesis', 'electron-conductive-materials', 'modulated-light-properties', 'energy-efficient-alloys',
            'high-durability-materials', 'surface-energy-modification', 'magnetocaloric-materials', 'photonic-properties-materials', 'electronic-devices-materials',
            'materials-for-energy-harvesting', 'nanoscale-imaging-techniques', 'non-volatile-memory-materials', 'nanostructured-particles',
            'electrochemical-sensors', 'li-ion-battery-materials', 'environmentally-safe-materials', 'bio-plastics', 'nano-powders',
            'material-degradation', 'thin-film-electronics', 'high-performance-ceramics', 'conformal-coatings', 'abrasion-resistant-materials',
            'recyclable-materials', 'organic-chemistry-in-materials', 'wear-resistant-coatings', 'hydrogels-in-materials', 'mechanism-of-deformation',
            'thermo-mechanical-properties', 'single-crystal-materials', 'nanoparticle-surface-functionalization', 'nano-hybrid-materials',
            'bimetallic-materials', 'nanomechanics-in-materials', 'biodegradable-composite-materials', 'ex-situ-materials-analysis',
            'nano-carriers-for-drug-delivery', 'polymer-composite-fabrication', 'functionalized-nanotubes', 'nano-synthesis-techniques',
            'thermal-decomposition-materials', 'polymeric-materials-characterization', 'surface-modified-nanoparticles', 'amorphous-metallic-materials',
            'thermally-conductive-polymers', 'nanofluid-materials', 'polymer-nanotube-composites', 'nanocrystals-for-materials',
            'optical-waveguides', 'toughening-mechanisms', 'conductive-ceramics', 'bio-inspired-materials-design', 'soft-materials',
            'ultrathin-films', 'hydrophobic-nanoparticles', 'multilayered-nanostructures', 'photo-catalytic-materials', 'materials-for-nanoelectronics',
            'multifunctional-systems', 'inorganic-nanostructures', 'ceramic-composite-fabrication', 'light-harvesting-materials', 'aerospace-nanomaterials',
            'transparent-conductive-materials', 'nanoencapsulation', 'photonic-molecular-materials', 'metal-nanoparticles-synthesis', 'transparent-nanocomposites'
        ]

        tags_data += [
            'high-energy-density-materials', 'nano-metallic-glasses', 'functional-nanocomposites', 'metallic-glass-alloys',
            'high-performance-batteries', 'polymer-nanocomposites-synthesis', 'nanostructured-thin-films', 'material-for-space-exploration',
            'thermo-mechanical-processing', 'thermal-imaging', 'materials-for-3d-printing', 'nanoparticle-dispersion-stability',
            'nanostructured-materials-fabrication', 'low-dimensional-materials', 'nanostructures-in-photonics', 'self-healing-composites',
            'bio-derived-materials', 'spintronic-materials', 'nano-coatings-for-electronics', 'high-temperature-superconducting-materials',
            'material-degradation-resistance', 'biomaterial-reinforcement', 'nano-composite-structures', 'flexible-electronics-materials',
            'superhydrophilic-materials', 'molecular-sieve-materials', 'photoactive-nanomaterials', 'piezoelectric-composites',
            'coating-materials-for-electronics', 'high-damping-materials', 'piezoelectric-nanofibers', 'nanotube-polymer-composites',
            'nanocellulose-based-materials', 'nanostructured-optical-materials', 'nano-textured-surfaces', 'thermo-optical-materials',
            'elastic-nanomaterials', 'inorganic-photonic-materials', 'nano-porous-glasses', 'laser-induced-material-modification',
            'advanced-polymer-blends', 'piezoelectric-films', 'bioinspired-materials', 'nanostructured-metal-composites', 'advanced-carbon-materials',
            'magnetic-silicon', 'nanotube-based-materials', 'high-temperature-electronics', 'nano-scale-synthesis-methods',
            'high-k-dielectric-materials', 'nanocomposites-for-catalysis', 'material-for-solar-cells', 'nanostructured-optical-devices',
            'high-strength-polymer-composites', 'alloying-in-metals', 'tungsten-carbide-materials', 'biocompatible-polymers-synthesis',
            'light-weight-composites', 'organic-photovoltaic-materials', 'nano-structured-conductive-materials', 'graphene-based-supercapacitors',
            'advanced-material-synthesis', 'high-stress-materials', 'energy-efficient-nanomaterials', 'surface-modified-composites',
            'refractory-nanocomposites', 'advanced-adhesives', 'graphene-coatings', 'thin-film-materials-fabrication', 'new-materials-for-hydrogen-storage',
            'green-ceramics', 'polymer-electrolyte-fuel-cells', 'self-assembled-materials', 'organic-inorganic-materials',
            'nano-materials-for-photodetectors', 'nano-materials-for-light-harvesting', 'thermoelectric-nanocomposites', 'materials-for-heat-exchangers',
            'metallic-nanoparticles-for-bio-applications', 'nano-photonics-materials', 'laser-machining-materials', 'graphene-based-materials-synthesis',
            'quantum-materials-synthesis', 'nanostructured-energy-storage-materials', 'high-efficiency-solar-cell-materials', 'advanced-composites-fabrication',
            'light-harvesting-nanomaterials', 'laser-textured-materials', 'nanocrystal-based-materials', 'porous-carbon-materials',
            'multi-functional-coatings', 'high-strength-glass', 'surface-roughness-effects-on-material-properties', 'optical-nanostructures',
            'deformation-in-nanomaterials', 'polymeric-thin-film-structures', 'self-assembled-nano-structures', 'graphene-based-superconductors',
            'materials-for-light-emitting-diodes', 'nanoparticle-surface-chemistry', 'solid-state-materials', 'nanoscale-morphology-tuning',
            'fuel-cell-materials-development', 'nanomaterial-synthesis-techniques', 'eco-friendly-materials-synthesis', 'advanced-metallic-nanoparticles',
            'solar-energy-materials', 'piezoresistive-materials-synthesis', 'materials-for-optical-fiber', 'self-repairing-materials',
            'alloy-engineering', 'nanostructured-thin-film-cathodes', 'ion-exchange-materials', 'composite-materials-processing',
            'thermal-management-materials', 'graphene-sensors', 'superplastic-nanomaterials', 'high-modulus-materials', 'material-synthesis-for-electronics',
            'nanoscale-fabrication-methods', 'materials-for-photonics', 'nano-structured-metals-and-alloys', 'polymer-synthesis-techniques',
            'thermal-oxidation-materials', 'polymer-inorganic-composites', 'bio-inspired-ceramics', 'biofunctional-materials', 'organic-nanocomposites',
            'composite-solar-cells', 'graphene-based-sensors', 'nanoscale-electrochemical-materials', 'polymer-nanoparticle-composite-materials',
            'lightweight-alloy-materials', 'low-cost-materials-for-solar-cells', 'nanotube-reinforced-materials', 'nano-structural-characterization',
            'metal-alloy-thin-films', 'advanced-graphene-composites', 'light-absorbing-nanomaterials', 'nano-composite-electrodes', 'reliable-materials-testing',
            'nano-alloy-synthesis-techniques', 'high-temperature-coatings', 'materials-for-wear-resistant-applications', 'multi-functional-nano-coatings',
            'conductive-materials-for-flexible-electronics', 'conductive-polymers-for-energy-storage', 'nanostructured-materials-for-sensors',
            'composite-for-lightweight-structures', 'advanced-materials-for-manufacturing', 'nanocrystal-processing', 'organic-materials-for-light-emitting-devices',
            'polymer-nano-fibers', 'nano-photonic-devices', 'self-healing-materials-in-sensors', 'multifunctional-thin-films', 'silicon-carbide-nanoparticles',
            'high-temperature-nano-coatings', 'nanostructured-catalytic-materials', 'nanoparticle-based-solar-cells', 'nano-sensors-for-environmental-monitoring',
            'nanostructured-materials-in-energy-storage', 'biomaterial-synthesis-for-medical-devices', 'additive-manufacturing-materials-characterization',
            'thermally-conductive-materials-in-electronics', 'biodegradable-thin-films', 'nano-engineering-for-photonics', 'energy-dense-materials',
            'superconducting-materials-for-quantum-computing', 'nanocomposites-for-lighting-applications', 'bio-compatible-nanomaterials',
            'nanomaterials-for-advanced-electronics', 'nano-coatings-for-cosmetics', 'laser-sintered-materials', 'surface-modification-for-biocompatibility',
            'materials-for-hybrid-batteries', 'nanofabrication-techniques', 'advanced-light-emitting-materials', 'carbon-based-supercapacitors', 
            'bio-inspired-nanostructures', 'silicon-nitride-ceramics', 'bio-ceramic-implants', 'nano-imprint-lithography-for-materials',
            'polymetallic-nanocomposites', 'nanoparticle-dispersion-techniques', 'thin-film-fabrication-methods', 'biomaterials-for-wound-care',
            'nano-patterned-surfaces', 'magnetic-nanomaterials', 'multi-functional-coatings-for-electronics', 'nano-reinforced-polymers'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        self.stdout.write(f'  Created/found {len(tags)} tags')

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Categories: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'Tags: {len(tags)}'))