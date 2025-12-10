from typing import Dict, Any, Generator, List
from django.db.models import Q
from matscichat.models import (
    Material, MaterialProperty, Environment, 
    MaterialEnvironmentCompatibility, Application,
    MaterialApplicationCompatibility
)


class MaterialQueryEngine:
    """Advanced materials query engine with streaming responses"""
    
    # Property mappings for different intents
    COMPARISON_PROPERTIES = {
        'seawater': [
            'strength_to_weight_ratio',
            'corrosion_resistance_score',
            'fatigue_resistance',
            'galvanic_corrosion_potential',
            'cost_per_kg'
        ],
        'aerospace': [
            'strength_to_weight_ratio',
            'fatigue_resistance',
            'high_temperature_strength',
            'thermal_expansion_coefficient'
        ],
        'construction': [
            'compressive_strength',
            'tensile_strength',
            'cost_per_kg',
            'durability',
            'thermal_conductivity'
        ],
        'default': [
            'density',
            'tensile_strength',
            'thermal_conductivity',
            'corrosion_resistance_score',
            'cost_per_kg'
        ]
    }
    
    DEGRADATION_PROPERTIES = {
        'seawater': [
            'electrochemical_corrosion_rate',
            'corrosion_resistance_score',
            'passivation_tendency',
            'microstructure_stability',
            'coating_adhesion'
        ],
        'acidic': [
            'acid_resistance',
            'passivation_tendency',
            'corrosion_resistance_score'
        ],
        'default': [
            'corrosion_resistance_score',
            'oxidation_resistance',
            'environmental_stability'
        ]
    }
    
    def __init__(self):
        pass
    
    def generate_answer(self, query: str, analysis: Dict) -> Generator[str, None, None]:
        """Main answer generation with streaming"""
        intents = analysis.get('intents', [])
        materials = analysis.get('materials', [])
        applications = analysis.get('applications', [])
        
        if not materials:
            yield "I couldn't identify specific materials in your query. Please mention materials like steel, aluminum, titanium, etc.\n\n"
            return
        
        # Fetch material objects
        material_objs = self._fetch_materials(materials)
        
        if not material_objs:
            yield f"I couldn't find information about {', '.join(materials)} in our database.\n\n"
            return
        
        # Process each intent
        for intent in intents:
            if intent == 'comparison':
                yield from self._handle_comparison(material_objs, applications, query)
            elif intent == 'degradation_forecast':
                yield from self._handle_degradation_forecast(material_objs, applications, query)
            elif intent == 'property_lookup':
                yield from self._handle_property_lookup(material_objs)
            elif intent == 'casual_chat':
                yield from self._handle_casual_chat(query)
            else:
                yield from self._handle_generic(intent, query)
    
    def _fetch_materials(self, material_names: List[str]) -> List[Material]:
        """Fetch material objects from database"""
        materials = []
        for name in material_names:
            mat = Material.objects.filter(
                Q(name__iexact=name) | 
                Q(other_names__icontains=name) |
                Q(name__icontains=name)
            ).first()
            if mat:
                materials.append(mat)
        return materials
    
    def _handle_comparison(self, materials: List[Material], applications: List[str], query: str) -> Generator[str, None, None]:
        """Handle comparison intent with detailed analysis"""
        if len(materials) < 2:
            yield "For comparison, I need at least two materials. Please specify another material.\n\n"
            return
        
        # Determine application context
        app_context = applications[0] if applications else 'default'
        
        # Announce intent
        material_names = [m.name for m in materials]
        yield f"**Your intention:** Comparison between **{' and '.join(material_names)}**"
        
        if applications:
            yield f" for **{applications[0]}** usage.\n\n"
        else:
            yield " (general purpose).\n\n"
        
        # Identify relevant properties
        properties = self.COMPARISON_PROPERTIES.get(app_context, self.COMPARISON_PROPERTIES['default'])
        
        yield f"**Analysis approach:** I will compare the following properties:\n"
        for prop in properties:
            readable_prop = prop.replace('_', ' ').title()
            yield f"- {readable_prop}\n"
        yield "\n"
        
        yield "---\n\n"
        yield "## Property Comparison\n\n"
        
        # Compare each property
        for prop in properties:
            yield from self._compare_property(materials, prop, app_context)
        
        # Generate recommendation
        yield "\n---\n\n"
        yield from self._generate_comparison_recommendation(materials, app_context, query)
    
    def _compare_property(self, materials: List[Material], prop: str, context: str) -> Generator[str, None, None]:
        """Compare a specific property across materials"""
        readable_prop = prop.replace('_', ' ').title()
        yield f"### {readable_prop}\n"
        
        values = []
        for mat in materials:
            value = self._get_property_value(mat, prop)
            if value is not None:
                values.append((mat.name, value))
                yield f"- **{mat.name}**: {value}\n"
            else:
                yield f"- **{mat.name}**: Data not available\n"
        
        # Determine best material for this property
        if values:
            # Higher is better for most properties except corrosion rate, cost
            lower_is_better = ['electrochemical_corrosion_rate', 'cost_per_kg', 'galvanic_corrosion_potential']
            
            if prop in lower_is_better:
                best = min(values, key=lambda x: x[1])
                yield f"\n  → **Best (Lowest):** {best[0]}\n"
            else:
                best = max(values, key=lambda x: x[1])
                yield f"\n  → **Best (Highest):** {best[0]}\n"
        
        yield "\n"
    
    def _generate_comparison_recommendation(self, materials: List[Material], context: str, query: str) -> Generator[str, None, None]:
        """Generate final comparison recommendation"""
        yield "## Comparison Result & Recommendation\n\n"
        
        material_names = [m.name for m in materials]
        
        if context == 'seawater':
            # Analyze seawater compatibility
            for mat in materials:
                env = Environment.objects.filter(
                    Q(name__icontains='seawater') | Q(name__icontains='marine')
                ).first()
                
                if env:
                    compat = MaterialEnvironmentCompatibility.objects.filter(
                        material=mat, environment=env
                    ).first()
                    
                    if compat:
                        score = compat.compatibility_score
                        if score >= 7:
                            yield f"✓ **{mat.name}** shows excellent compatibility with seawater (Score: {score}/10)\n"
                        elif score >= 5:
                            yield f"⚠ **{mat.name}** shows moderate compatibility with seawater (Score: {score}/10)\n"
                        else:
                            yield f"✗ **{mat.name}** shows poor compatibility with seawater (Score: {score}/10)\n"
            
            yield "\n**Specific Recommendations:**\n"
            
            # Generate context-specific recommendations
            if 'aluminum' in [m.name.lower() for m in materials]:
                yield "- **Aluminum** is suitable for smaller marine applications (boats, fishing vessels, marine rails)\n"
                yield "  - Advantages: Lightweight, good strength-to-weight ratio, resistant to general corrosion\n"
                yield "  - Cautions: Prone to galvanic corrosion when in contact with dissimilar metals\n\n"
            
            if 'steel' in [m.name.lower() for m in materials]:
                yield "- **Steel** is better for large structural applications (ship hulls, offshore platforms)\n"
                yield "  - Advantages: High strength, good for load-bearing structures, cost-effective\n"
                yield "  - Cautions: Requires protective coatings, regular maintenance needed\n\n"
        else:
            # General recommendation
            yield f"Based on the analysis:\n\n"
            yield f"- Each material has distinct advantages for different applications\n"
            yield f"- Consider your specific requirements: budget, weight constraints, performance needs\n"
            yield f"- Consult with a materials engineer for critical applications\n\n"
    
    def _handle_degradation_forecast(self, materials: List[Material], applications: List[str], query: str) -> Generator[str, None, None]:
        """Handle degradation forecast intent"""
        if not materials:
            yield "Please specify materials for degradation analysis.\n\n"
            return
        
        # Determine application context
        app_context = applications[0] if applications else 'default'
        
        # Announce intent
        material_names = [m.name for m in materials]
        yield f"\n**Your intention:** Degradation forecast for **{' and '.join(material_names)}**"
        
        if applications:
            yield f" in **{applications[0]}** environment.\n\n"
        else:
            yield ".\n\n"
        
        # Identify relevant properties
        properties = self.DEGRADATION_PROPERTIES.get(app_context, self.DEGRADATION_PROPERTIES['default'])
        
        yield f"**Analysis approach:** I will analyze:\n"
        for prop in properties:
            readable_prop = prop.replace('_', ' ').title()
            yield f"- {readable_prop}\n"
        yield "\n"
        
        yield "---\n\n"
        yield "## Degradation Analysis\n\n"
        
        # Analyze each material
        for mat in materials:
            yield f"### {mat.name}\n\n"
            
            # Get degradation properties
            for prop in properties:
                value = self._get_property_value(mat, prop)
                if value is not None:
                    readable_prop = prop.replace('_', ' ').title()
                    yield f"- **{readable_prop}**: {value}\n"
            
            # Get environment compatibility if available
            if applications:
                env = Environment.objects.filter(
                    Q(name__icontains=applications[0]) |
                    Q(other_names__icontains=applications[0])
                ).first()
                
                if env:
                    compat = MaterialEnvironmentCompatibility.objects.filter(
                        material=mat, environment=env
                    ).first()
                    
                    if compat and compat.degradation_behavior:
                        yield f"\n**Degradation Behavior:** {compat.degradation_behavior}\n"
            
            yield "\n"
        
        # Generate forecast
        yield "---\n\n"
        yield from self._generate_degradation_forecast(materials, app_context, query)
    
    def _generate_degradation_forecast(self, materials: List[Material], context: str, query: str) -> Generator[str, None, None]:
        """Generate degradation forecast and timeline"""
        yield "## Degradation Forecast\n\n"
        
        if context == 'seawater':
            for mat in materials:
                corr_score = mat.corrosion_resistance_score or 5
                
                yield f"**{mat.name}:**\n"
                
                if corr_score >= 8:
                    yield f"- **Degradation Rate:** Very slow\n"
                    yield f"- **Expected Lifespan:** 20-50+ years with minimal maintenance\n"
                    yield f"- **Maintenance:** Annual inspection recommended\n"
                elif corr_score >= 6:
                    yield f"- **Degradation Rate:** Moderate\n"
                    yield f"- **Expected Lifespan:** 10-25 years with proper maintenance\n"
                    yield f"- **Maintenance:** Coating inspection every 2-3 years\n"
                elif corr_score >= 4:
                    yield f"- **Degradation Rate:** Fast\n"
                    yield f"- **Expected Lifespan:** 5-15 years with protective coatings\n"
                    yield f"- **Maintenance:** Annual coating renewal required\n"
                else:
                    yield f"- **Degradation Rate:** Very fast\n"
                    yield f"- **Expected Lifespan:** 2-8 years even with protection\n"
                    yield f"- **Maintenance:** Frequent monitoring and coating\n"
                
                yield "\n"
            
            # Comparative forecast
            if len(materials) >= 2:
                yield "**Comparative Timeline:**\n"
                sorted_mats = sorted(materials, key=lambda m: m.corrosion_resistance_score or 0, reverse=True)
                
                yield f"- **Will corrode fastest:** {sorted_mats[-1].name}\n"
                yield f"- **Will last longest:** {sorted_mats[0].name}\n\n"
                
                yield f"**Recommendation:** For long-term seawater exposure, prefer {sorted_mats[0].name} "
                yield f"or apply high-quality protective coatings to {sorted_mats[-1].name}.\n\n"
        else:
            yield "Degradation rates depend on specific environmental conditions.\n"
            yield "Please provide more details about the operating environment for accurate forecasting.\n\n"
    
    def _handle_property_lookup(self, materials: List[Material]) -> Generator[str, None, None]:
        """Handle simple property lookup"""
        for mat in materials:
            yield f"## {mat.name}\n\n"
            
            if mat.description:
                yield f"{mat.description}\n\n"
            
            yield "**Key Properties:**\n"
            if mat.density:
                yield f"- Density: {mat.density} g/cm³\n"
            if mat.tensile_strength:
                yield f"- Tensile Strength: {mat.tensile_strength} MPa\n"
            if mat.melting_point:
                yield f"- Melting Point: {mat.melting_point} °C\n"
            if mat.thermal_conductivity:
                yield f"- Thermal Conductivity: {mat.thermal_conductivity} W/m·K\n"
            if mat.corrosion_resistance_score:
                yield f"- Corrosion Resistance: {mat.corrosion_resistance_score}/10\n"
            
            yield "\n"
    
    def _handle_casual_chat(self, query: str) -> Generator[str, None, None]:
        """Handle greetings and casual chat"""
        query_lower = query.lower()
        
        if any(g in query_lower for g in ['hello', 'hi', 'hey']):
            yield "Hello! I'm MatSciChat, your materials science assistant. 👋\n\n"
            yield "I can help you with:\n"
            yield "- Comparing materials for specific applications\n"
            yield "- Forecasting material degradation and corrosion\n"
            yield "- Looking up material properties\n\n"
            yield "What would you like to know?\n"
        elif any(g in query_lower for g in ['bye', 'goodbye']):
            yield "Goodbye! Feel free to return anytime. 👋\n"
        elif any(g in query_lower for g in ['thanks', 'thank you']):
            yield "You're welcome! Happy to help with materials science. 😊\n"
        else:
            yield "I'm here to help with materials questions!\n"
    
    def _handle_generic(self, intent: str, query: str) -> Generator[str, None, None]:
        """Handle other intents"""
        if intent == 'theory_explain':
            yield "For theoretical explanations, please consult materials science textbooks or specialized resources.\n\n"
            yield "I specialize in material comparisons, property lookups, and degradation forecasting.\n"
        elif intent == 'process_guidance':
            yield "For detailed manufacturing processes, please consult process handbooks.\n\n"
            yield "I can help you select appropriate materials for your process!\n"
        elif intent == 'news_request':
            yield "I don't have access to real-time news. For latest research:\n"
            yield "- Check journals: Nature Materials, Advanced Materials\n"
            yield "- Visit: Materials Today, ScienceDaily\n\n"
        else:
            yield "I'm not sure how to help with that. Try asking about material comparisons or properties!\n"
    
    def _get_property_value(self, material: Material, property_name: str):
        """Get property value from material or MaterialProperty table"""
        # Check main fields first
        if hasattr(material, property_name):
            val = getattr(material, property_name, None)
            if val is not None:
                return val
        
        # Check MaterialProperty table
        prop = MaterialProperty.objects.filter(
            material=material,
            key=property_name
        ).first()
        
        if prop:
            return prop.float_value or prop.text_value
        
        return None