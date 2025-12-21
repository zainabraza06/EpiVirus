# disease_models.py
import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import random
from datetime import datetime, timedelta
import json
import networkx as nx  # Added missing import

class DiseaseState(Enum):
    """All possible disease states for individuals"""
    S = "Susceptible"
    E = "Exposed"           # Infected but not yet infectious
    I = "Infectious"        # Generic infectious
    Ia = "Asymptomatic"     # Infectious with no symptoms
    Im = "Mild"             # Mild symptoms
    Is = "Severe"           # Severe symptoms
    Ih = "Hospitalized"     # Hospitalized
    Ic = "Critical"         # ICU/Critical care
    R = "Recovered"         # Recovered with immunity
    D = "Deceased"          # Died from disease
    V = "Vaccinated"        # Vaccinated with partial immunity

@dataclass
class DiseaseParameters:
    """Complete parameters for ANY disease model"""
    
    # Basic disease characteristics
    name: str = "COVID-19"
    R0: float = 2.5                         # Basic reproduction number
    generation_time: float = 5.2            # Mean time between infections
    
    # Incubation and infectious periods (days)
    incubation_period: Dict[str, float] = field(default_factory=lambda: {'mean': 5.2, 'std': 2.8})
    infectious_period: Dict[str, float] = field(default_factory=lambda: {'mean': 10.0, 'std': 3.0})
    
    # Severity probabilities
    p_asymptomatic: float = 0.4            # Probability of no symptoms
    p_mild: float = 0.4                    # Mild symptoms, no hospitalization
    p_severe: float = 0.15                 # Severe, may need hospitalization
    p_critical: float = 0.05               # Critical, ICU needed
    
    # Hospitalization and mortality
    hospitalization_rate: float = 0.15     # Overall hospitalization rate
    icu_rate: float = 0.05                 #% of hospitalized needing ICU
    mortality_rate: float = 0.02           # Overall case fatality rate
    
    # Age-stratified parameters
    age_stratification: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        '0-9':   {'severity': 0.01,  'hospitalization': 0.005, 'mortality': 0.01, 'susceptibility': 0.5},
        '10-19': {'severity': 0.02,  'hospitalization': 0.01,  'mortality': 0.02, 'susceptibility': 0.7},
        '20-29': {'severity': 0.05,  'hospitalization': 0.02,  'mortality': 0.1,  'susceptibility': 0.9},
        '30-39': {'severity': 0.1,   'hospitalization': 0.03,  'mortality': 0.3,  'susceptibility': 0.9},
        '40-49': {'severity': 0.15,  'hospitalization': 0.05,  'mortality': 0.1,   'susceptibility': 0.9},
        '50-59': {'severity': 0.25,  'hospitalization': 0.08,  'mortality': 0.3,   'susceptibility': 0.9},
        '60-69': {'severity': 0.4,   'hospitalization': 0.15,  'mortality': 0.8,   'susceptibility': 0.9},
        '70-79': {'severity': 0.6,   'hospitalization': 0.25,  'mortality': 0.7,   'susceptibility': 0.9},
        '80+':   {'severity': 0.8,   'hospitalization': 0.35,  'mortality': 0.25,   'susceptibility': 0.9}
    })
    
    # Intervention effects
    mask_efficacy: float = 0.3            # Source control + wearer protection
    distancing_effect: float = 0.2        # Reduction from social distancing
    isolation_effect: float = 0.5         # Reduction from case isolation
    
    # Vaccine parameters
    vaccine_efficacy: Dict[str, float] = field(default_factory=lambda: {
        'infection': 0.7,      # Protection against infection
        'severity': 0.8,      # Protection against severe disease
        'transmission': 0.6,   # Reduction in transmission if infected
        'waning_start': 120,   # Days until immunity starts waning
        'waning_rate': 0.003   # Daily waning rate after start
    })
    
    # Seasonality (for diseases like influenza)
    seasonality_amplitude: float = 0.0     # 0-1, 0 = no seasonality
    seasonality_peak: int = 0              # Day of year when transmission peaks
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        assert 0 <= self.R0 <= 20, "R0 must be between 0 and 20"
        assert 0 <= self.p_asymptomatic <= 1
        total_prob = self.p_asymptomatic + self.p_mild + self.p_severe + self.p_critical
        assert abs(total_prob - 1.0) < 0.01, \
               f"Severity probabilities must sum to 1 (got {total_prob:.3f})"

class DiseaseLibrary:
    """Pre-configured diseases with realistic parameters from literature"""
    
    @staticmethod
    def covid19_variant(variant: str = "wildtype") -> DiseaseParameters:
        """COVID-19 with different variant parameters"""
        variants = {
            "wildtype": DiseaseParameters(
                name="COVID-19 (Wildtype)",
                R0=2.5,
                p_asymptomatic=0.4,
                p_mild=0.4,
                p_severe=0.15,
                p_critical=0.05,
                mortality_rate=0.02,
                hospitalization_rate=0.15
            ),
            "alpha": DiseaseParameters(
                name="COVID-19 (Alpha)",
                R0=4.0,
                p_asymptomatic=0.3,
                p_mild=0.45,
                p_severe=0.18,
                p_critical=0.07,
                mortality_rate=0.025,
                hospitalization_rate=0.18
            ),
            "delta": DiseaseParameters(
                name="COVID-19 (Delta)",
                R0=5.0,
                p_asymptomatic=0.25,
                p_mild=0.45,
                p_severe=0.22,
                p_critical=0.08,
                mortality_rate=0.03,
                hospitalization_rate=0.22
            ),
            "omicron": DiseaseParameters(
                name="COVID-19 (Omicron)",
                R0=9.5,
                p_asymptomatic=0.35,
                p_mild=0.5,
                p_severe=0.12,
                p_critical=0.03,
                mortality_rate=0.01,
                hospitalization_rate=0.08
            )
        }
        return variants.get(variant, variants["wildtype"])
    
    @staticmethod
    def influenza() -> DiseaseParameters:
        """Seasonal influenza parameters"""
        return DiseaseParameters(
            name="Influenza (Seasonal)",
            R0=1.3,
            generation_time=3.0,
            incubation_period={'mean': 2.0, 'std': 0.5},
            infectious_period={'mean': 5.0, 'std': 1.0},
            p_asymptomatic=0.2,
            p_mild=0.6,
            p_severe=0.15,
            p_critical=0.05,
            hospitalization_rate=0.02,
            mortality_rate=0.001,
            seasonality_amplitude=0.3,
            seasonality_peak=45  # Mid-February peak
        )
    
    @staticmethod
    def measles() -> DiseaseParameters:
        """Measles - highly contagious"""
        return DiseaseParameters(
            name="Measles",
            R0=15.0,
            generation_time=12.0,
            incubation_period={'mean': 10.0, 'std': 2.0},
            infectious_period={'mean': 8.0, 'std': 1.0},
            p_asymptomatic=0.05,
            p_mild=0.1,
            p_severe=0.5,
            p_critical=0.35,
            hospitalization_rate=0.3,
            mortality_rate=0.002,
            mask_efficacy=0.2  # Masks less effective for airborne
        )
    
    @staticmethod
    def ebola() -> DiseaseParameters:
        """Ebola virus disease"""
        return DiseaseParameters(
            name="Ebola",
            R0=1.8,
            generation_time=15.0,
            incubation_period={'mean': 10.0, 'std': 4.0},
            infectious_period={'mean': 15.0, 'std': 5.0},
            p_asymptomatic=0.01,
            p_mild=0.1,
            p_severe=0.4,
            p_critical=0.49,
            hospitalization_rate=0.7,
            mortality_rate=0.5,  # Very high mortality
            mask_efficacy=0.8    # PPE very effective
        )
    
    @staticmethod
    def sars() -> DiseaseParameters:
        """SARS-CoV-1"""
        return DiseaseParameters(
            name="SARS",
            R0=3.0,
            p_asymptomatic=0.01,
            p_mild=0.09,
            p_severe=0.4,
            p_critical=0.5,
            mortality_rate=0.095,  # ~9.5% mortality
            hospitalization_rate=0.9  # Most cases hospitalized
        )

class TransmissionCalculator:
    """Advanced transmission probability calculation with all factors"""
    
    @staticmethod
    def calculate_transmission_probability(
        infector: int,
        susceptible: int,
        G,
        disease: DiseaseParameters,
        interventions: Dict[str, Any],
        current_day: int = 0
    ) -> float:
        """
        Calculate probability of transmission considering ALL factors
        
        Formula: P = R0 × C × S × A × I × M × V × T × E
        
        Where:
        - R0: Basic reproduction number
        - C: Contact factor (network structure)
        - S: Susceptibility (age, immunity)
        - A: Activity/mobility factor
        - I: Intervention effects
        - M: Mask usage
        - V: Vaccination status
        - T: Time/seasonality
        - E: Environmental factors
        """
        
        # 1. BASE TRANSMISSION (R0 adjusted for network structure)
        base_prob = TransmissionCalculator._base_transmission(
            infector, susceptible, G, disease
        )
        
        # 2. AGE-RELATED SUSCEPTIBILITY
        age_factor = TransmissionCalculator._age_susceptibility(
            G.nodes[susceptible]['age'], disease
        )
        
        # 3. MOBILITY AND ACTIVITY
        mobility_factor = TransmissionCalculator._mobility_factor(
            G.nodes[infector]['mobility'],
            G.nodes[susceptible]['mobility']
        )
        
        # 4. CONTACT TYPE AND DURATION
        contact_factor = TransmissionCalculator._contact_factor(
            infector, susceptible, G
        )
        
        # 5. INTERVENTION EFFECTS
        intervention_factor = TransmissionCalculator._intervention_factor(
            infector, susceptible, G, interventions
        )
        
        # 6. MASK USAGE
        mask_factor = TransmissionCalculator._mask_factor(
            infector, susceptible, G, interventions
        )
        
        # 7. VACCINATION/IMMUNITY
        immunity_factor = TransmissionCalculator._immunity_factor(
            susceptible, G, disease
        )
        
        # 8. SEASONALITY/TIME
        season_factor = TransmissionCalculator._seasonality_factor(
            current_day, disease
        )
        
        # 9. ENVIRONMENTAL FACTORS (ventilation, outdoors)
        env_factor = TransmissionCalculator._environmental_factor(
            infector, susceptible, G, interventions
        )
        
        # 10. ASYMPTOMATIC TRANSMISSION REDUCTION
        symptoms_factor = 1.0
        if G.nodes[infector].get('symptoms') == 'asymptomatic':
            symptoms_factor = 0.3  # Asymptomatic transmit less
        
        # Combine all factors
        final_prob = (base_prob * age_factor * mobility_factor * 
                     contact_factor * intervention_factor * mask_factor *
                     immunity_factor * season_factor * env_factor * symptoms_factor)
        
        # Ensure probability is between 0 and 0.99
        return max(0.0, min(0.99, final_prob))
    
    @staticmethod
    def _base_transmission(infector, susceptible, G, disease):
        """Base transmission adjusted for network degree"""
        # More connected individuals have lower per-contact probability
        infector_degree = G.degree(infector)
        susceptible_degree = G.degree(susceptible)
        
        # Average degree adjustment
        avg_degree = (infector_degree + susceptible_degree) / 2
        degree_factor = 2.0 / (avg_degree + 2)  # Normalize
        
        return disease.R0 * degree_factor * 0.08  # Scaling factor
    
    @staticmethod
    def _age_susceptibility(age, disease):
        """Age-based susceptibility multiplier"""
        age_group = TransmissionCalculator._get_age_group(age)
        return disease.age_stratification[age_group]['susceptibility']
    
    @staticmethod
    def _mobility_factor(infector_mobility, susceptible_mobility):
        """Mobility increases contact opportunities"""
        return (infector_mobility + susceptible_mobility) / 2
    
    @staticmethod
    def _contact_factor(infector, susceptible, G):
        """Factor based on type and duration of contact"""
        edge_data = G.get_edge_data(infector, susceptible, {})
        
        contact_type = edge_data.get('type', 'random')
        weight = edge_data.get('weight', 1.0)
        
        # Different transmission rates for different contact types
        type_factors = {
            'household': 2.0,    # Close, prolonged contact
            'school': 1.5,       # Moderate contact
            'workplace': 1.2,    # Moderate contact
            'hub': 1.8,          # Super-spreader
            'random': 0.8        # Casual contact
        }
        
        type_factor = type_factors.get(contact_type, 1.0)
        return type_factor * weight
    
    @staticmethod
    def _intervention_factor(infector, susceptible, G, interventions):
        """Factor for all active interventions"""
        factor = 1.0
        
        # Social distancing
        if interventions.get('social_distancing', False):
            compliance = interventions.get('distancing_compliance', 0.7)
            effectiveness = interventions.get('distancing_effectiveness', 0.3)
            
            # Check if individuals comply
            inf_complies = random.random() < G.nodes[infector].get('compliance', 0.5)
            sus_complies = random.random() < G.nodes[susceptible].get('compliance', 0.5)
            
            if inf_complies and sus_complies:
                factor *= (1 - effectiveness * compliance)
        
        # Lockdown/isolation
        if G.nodes[infector].get('isolated', False) or G.nodes[susceptible].get('isolated', False):
            factor *= 0.1  # 90% reduction
        
        # Travel restrictions
        if interventions.get('travel_restrictions', False):
            edge_data = G.get_edge_data(infector, susceptible, {})
            if edge_data.get('type') == 'random':  # Long-distance
                factor *= (1 - interventions.get('travel_reduction', 0.5))
        
        return factor
    
    @staticmethod
    def _mask_factor(infector, susceptible, G, interventions):
        """Mask effectiveness factor"""
        if not interventions.get('mask_mandate', False):
            return 1.0
        
        mask_efficacy = interventions.get('mask_efficacy', 0.5)
        
        # Check if individuals wear masks
        inf_mask = G.nodes[infector].get('wears_mask', 
                                        random.random() < interventions.get('mask_compliance', 0.7))
        sus_mask = G.nodes[susceptible].get('wears_mask', 
                                           random.random() < interventions.get('mask_compliance', 0.7))
        
        if inf_mask and sus_mask:
            # Both wearing masks - bidirectional protection
            return (1 - mask_efficacy) * (1 - mask_efficacy * 0.7)
        elif inf_mask or sus_mask:
            # One wearing mask - partial protection
            return 1 - (mask_efficacy * 0.3)
        else:
            # No masks
            return 1.0
    
    @staticmethod
    def _immunity_factor(susceptible, G, disease):
        """Factor from vaccination/natural immunity"""
        immunity = G.nodes[susceptible]['immunity']
        
        # Check if vaccinated
        if G.nodes[susceptible].get('vaccinated', False):
            vaccine_eff = disease.vaccine_efficacy['infection']
            days_since_vax = G.nodes[susceptible].get('days_vaccinated', 0)
            
            # Account for waning immunity
            if days_since_vax > disease.vaccine_efficacy['waning_start']:
                waned_days = days_since_vax - disease.vaccine_efficacy['waning_start']
                waning = 1 - (1 - disease.vaccine_efficacy['waning_rate']) ** waned_days
                vaccine_eff *= (1 - waning)
            
            immunity = max(immunity, vaccine_eff)
        
        return 1 - immunity
    
    @staticmethod
    def _seasonality_factor(day, disease):
        """Seasonal variation in transmission"""
        if disease.seasonality_amplitude == 0:
            return 1.0
        
        # Sinusoidal seasonal pattern
        day_of_year = day % 365
        radians = 2 * np.pi * (day_of_year - disease.seasonality_peak) / 365
        return 1 + disease.seasonality_amplitude * np.cos(radians)
    
    @staticmethod
    def _environmental_factor(infector, susceptible, G, interventions):
        """Environmental factors like ventilation"""
        factor = 1.0
        
        # Improved ventilation
        if interventions.get('improved_ventilation', False):
            factor *= 0.7
        
        # Outdoor vs indoor (simplified - assume some edges are outdoor)
        edge_data = G.get_edge_data(infector, susceptible, {})
        if edge_data.get('location') == 'outdoor':
            factor *= 0.2  # 80% reduction outdoors
        
        return factor
    
    @staticmethod
    def _get_age_group(age):
        """Map age to stratification group"""
        if age < 10: return '0-9'
        elif age < 20: return '10-19'
        elif age < 30: return '20-29'
        elif age < 40: return '30-39'
        elif age < 50: return '40-49'
        elif age < 60: return '50-59'
        elif age < 70: return '60-69'
        elif age < 80: return '70-79'
        else: return '80+'

class DiseaseProgression:
    """Handles individual disease progression through states - FIXED VERSION"""
    
    @staticmethod
    @staticmethod
    def determine_initial_course(age, disease, vaccination_status=False):
        """
        Determine disease course when someone gets infected
        Returns: (symptoms_type, incubation_days, infectious_days, outcomes)
        """
        # Get age group
        age_group = TransmissionCalculator._get_age_group(age)
        age_params = disease.age_stratification[age_group]
        
        # Random outcome based on probabilities
        rand = random.random()
        
        # Adjust probabilities for vaccination
        if vaccination_status:
            ve_severity = disease.vaccine_efficacy['severity']
            
            # Vaccines primarily reduce severe outcomes
            p_critical_vax = max(0, disease.p_critical * (1 - ve_severity))
            p_severe_vax = max(0, disease.p_severe * (1 - ve_severity * 0.7))
            p_mild_vax = max(0, disease.p_mild * (1 - ve_severity * 0.3))
            p_asymptomatic_vax = 1 - (p_critical_vax + p_severe_vax + p_mild_vax)
            
            # Ensure probabilities are valid
            p_asymptomatic_vax = max(0, min(1, p_asymptomatic_vax))
            adjusted_p_asymptomatic = p_asymptomatic_vax
            adjusted_p_mild = p_mild_vax
            adjusted_p_severe = p_severe_vax
            adjusted_p_critical = p_critical_vax
        else:
            adjusted_p_asymptomatic = disease.p_asymptomatic
            adjusted_p_mild = disease.p_mild
            adjusted_p_severe = disease.p_severe
            adjusted_p_critical = disease.p_critical
        
        # Adjust for age-specific severity
        age_severity = age_params['severity']
        adjusted_p_critical = min(1, adjusted_p_critical * (1 + age_severity * 2))
        adjusted_p_severe = min(1, adjusted_p_severe * (1 + age_severity))
        adjusted_p_mild = max(0, adjusted_p_mild * (1 - age_severity * 0.3))
        adjusted_p_asymptomatic = 1 - (adjusted_p_critical + adjusted_p_severe + adjusted_p_mild)
        adjusted_p_asymptomatic = max(0, min(1, adjusted_p_asymptomatic))
        
        # Normalize to ensure sum = 1
        total = adjusted_p_asymptomatic + adjusted_p_mild + adjusted_p_severe + adjusted_p_critical
        if total > 0:
            adjusted_p_asymptomatic /= total
            adjusted_p_mild /= total
            adjusted_p_severe /= total
            adjusted_p_critical /= total
        
        # Determine symptoms type based on probabilities
        symptoms = 'asymptomatic'  # default
        if rand < adjusted_p_asymptomatic:
            symptoms = 'asymptomatic'
        elif rand < adjusted_p_asymptomatic + adjusted_p_mild:
            symptoms = 'mild'
        elif rand < adjusted_p_asymptomatic + adjusted_p_mild + adjusted_p_severe:
            symptoms = 'severe'
        else:
            symptoms = 'critical'
        
        # Set parameters based on symptoms
        if symptoms == 'asymptomatic':
            inc_mean = disease.incubation_period['mean'] * 0.8
            inf_mean = disease.infectious_period['mean'] * 0.7
            hospitalization_prob = 0.0
        elif symptoms == 'mild':
            inc_mean = disease.incubation_period['mean']
            inf_mean = disease.infectious_period['mean'] * 0.9
            hospitalization_prob = 0.01 * age_params['hospitalization']
        elif symptoms == 'severe':
            inc_mean = disease.incubation_period['mean'] * 0.9
            inf_mean = disease.infectious_period['mean'] * 1.2
            hospitalization_prob = 0.7 * age_params['hospitalization']
        else:  # critical
            inc_mean = disease.incubation_period['mean'] * 0.8
            inf_mean = disease.infectious_period['mean'] * 1.5
            hospitalization_prob = 0.9 * age_params['hospitalization']
        
        # Sample actual days from distributions - ensure minimum values
        incubation_days = max(1, int(np.random.normal(
            inc_mean, disease.incubation_period['std']
        )))
        
        infectious_days = max(3, int(np.random.normal(
            inf_mean, disease.infectious_period['std']
        )))
        
        # Determine if hospitalized
        will_hospitalize = False
        hospital_day = None
        if symptoms in ['severe', 'critical'] and random.random() < hospitalization_prob:
            will_hospitalize = True
            hospital_day = incubation_days + random.randint(1, 3)
        
        # Determine if dies
        will_die = False
        death_day = None
        
        # Base mortality from age
        base_mortality = age_params['mortality']
        
        # Adjust mortality based on symptoms
        if symptoms == 'asymptomatic':
            mortality_prob = base_mortality * 0.01  # Very low
        elif symptoms == 'mild':
            mortality_prob = base_mortality * 0.1   # Low
        elif symptoms == 'severe':
            mortality_prob = base_mortality * 3.0   # Moderate
        else:  # critical
            mortality_prob = base_mortality * 10.0  # High
        
        # Apply vaccine protection
        if vaccination_status:
            ve_severity = disease.vaccine_efficacy['severity']
            mortality_prob *= (1 - ve_severity * 0.8)  # Vaccines protect against death
        
        # Ensure probability is reasonable
        mortality_prob = min(0.95, max(0, mortality_prob))
        
        # Roll for death
        if random.random() < mortality_prob:
            will_die = True
            if will_hospitalize and hospital_day:
                death_day = hospital_day + random.randint(3, 14)
            else:
                death_day = incubation_days + random.randint(
                    infectious_days // 2, infectious_days
                )
        
        # Determine recovery day (if not fatal)
        if will_die:
            recovery_day = None
        else:
            recovery_day = incubation_days + infectious_days
        
        # DEBUG: Log for problematic cases
        if will_die and (death_day is None or death_day <= 0):
            print(f"⚠️  DEBUG: Node marked to die but death_day={death_day}, symptoms={symptoms}")
            death_day = incubation_days + infectious_days  # Default fallback
        
        if recovery_day is None and not will_die:
            print(f"⚠️  DEBUG: Node not marked to die but recovery_day=None, symptoms={symptoms}")
            recovery_day = incubation_days + infectious_days  # Default fallback
        
        return {
            'symptoms': symptoms,
            'incubation_days': incubation_days,
            'infectious_days': infectious_days,
            'will_hospitalize': will_hospitalize,
            'hospital_day': hospital_day,
            'will_die': will_die,
            'death_day': death_day,
            'recovery_day': recovery_day  # This will be None if will_die is True
        }
    @staticmethod
    def update_immunity(node, G, disease, current_day):
        """Update immunity levels (waning, boosting)"""
        if 'immunity' not in G.nodes[node]:
            G.nodes[node]['immunity'] = 0.0
            
        current_immunity = G.nodes[node]['immunity']
        
        # Natural immunity waning for recovered individuals
        if G.nodes[node].get('state') == 'R':
            days_recovered = G.nodes[node].get('days_in_state', 0)
            # Immunity wanes slowly over time
            waning_rate = 0.0005  # ~50% loss per year if no boosting
            new_immunity = current_immunity * (1 - waning_rate) ** (days_recovered / 365)
            G.nodes[node]['immunity'] = max(0.0, min(1.0, new_immunity))
        
        # Vaccine immunity waning
        elif G.nodes[node].get('vaccinated', False):
            vaccination_day = G.nodes[node].get('vaccination_day', current_day)
            days_vaccinated = max(0, current_day - vaccination_day)
            
            if days_vaccinated > disease.vaccine_efficacy.get('waning_start', 120):
                waned_days = days_vaccinated - disease.vaccine_efficacy['waning_start']
                waning = disease.vaccine_efficacy.get('waning_rate', 0.003) * waned_days
                G.nodes[node]['immunity'] = max(0.0, current_immunity - waning)
class InterventionSchedule:
    """Manages timing and application of interventions"""
    
    def __init__(self):
        self.scheduled_interventions = []
    
    def add_intervention(self, day, intervention_type, **params):
        """Schedule an intervention to start on specific day"""
        self.scheduled_interventions.append({
            'day': day,
            'type': intervention_type,
            'params': params
        })
        # Sort by day
        self.scheduled_interventions.sort(key=lambda x: x['day'])
        print(f"📅 Scheduled {intervention_type} for day {day} with params: {params}")
    
    def get_interventions_for_day(self, day):
        """Get interventions scheduled for this day"""
        interventions = []
        for interv in self.scheduled_interventions:
            if interv['day'] == day:
                interventions.append(interv)
        return interventions
    
    def create_preset_scenario(self, scenario_name):
        """Create predefined intervention scenarios - FIXED VERSION"""
        scenarios = {
            'no_intervention': [],
            'delayed_response': [
                {'day': 30, 'type': 'mask_mandate', 'params': {'efficacy': 0.5, 'compliance': 0.7}},
                {'day': 45, 'type': 'social_distancing', 'params': {'effectiveness': 0.3, 'compliance': 0.6}},
                {'day': 60, 'type': 'vaccination', 'params': {'rate': 0.02, 'efficacy': 0.9, 'priority': 'age'}},
                {'day': 75, 'type': 'lockdown', 'params': {'strictness': 0.7, 'compliance': 0.8}},
                {'day': 120, 'type': 'reopen', 'params': {'gradual': True}}
            ],
            'rapid_response': [
                {'day': 7, 'type': 'mask_mandate', 'params': {'efficacy': 0.6, 'compliance': 0.8}},
                {'day': 14, 'type': 'testing', 'params': {'rate': 0.1, 'accuracy': 0.95, 'delay': 1}},
                {'day': 21, 'type': 'social_distancing', 'params': {'effectiveness': 0.5, 'compliance': 0.7}},
                {'day': 30, 'type': 'vaccination', 'params': {'rate': 0.03, 'efficacy': 0.9, 'priority': 'frontline'}},
                {'day': 45, 'type': 'travel_restrictions', 'params': {'reduction': 0.7}}
            ],
            'herd_immunity': [
                {'day': 0, 'type': 'vaccination', 'params': {'rate': 0.05, 'efficacy': 0.9, 'priority': 'random'}},
                {'day': 30, 'type': 'vaccination', 'params': {'rate': 0.03, 'efficacy': 0.9, 'priority': 'random'}},
                {'day': 60, 'type': 'vaccination', 'params': {'rate': 0.02, 'efficacy': 0.9, 'priority': 'random'}}
            ],
            'full_lockdown': [
                {'day': 14, 'type': 'lockdown', 'params': {'strictness': 0.9, 'compliance': 0.85, 'duration': 30}},
                {'day': 15, 'type': 'mask_mandate', 'params': {'efficacy': 0.7, 'compliance': 0.9}},
                {'day': 16, 'type': 'travel_restrictions', 'params': {'reduction': 0.9}},
                {'day': 45, 'type': 'reopen', 'params': {'gradual': True}},
                {'day': 50, 'type': 'vaccination', 'params': {'rate': 0.04, 'efficacy': 0.95, 'priority': 'vulnerable'}}
            ]
        }
        
        if scenario_name in scenarios:
            self.scheduled_interventions = []
            for schedule_item in scenarios[scenario_name]:
                if schedule_item:  # Check if not empty
                    # Directly add the dictionary
                    self.scheduled_interventions.append(schedule_item)
                    print(f"📅 Added {schedule_item['type']} for day {schedule_item['day']}")
            print(f"✅ Created '{scenario_name}' scenario with {len(self.scheduled_interventions)} interventions")
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")
# ==================== QUICK TEST FUNCTION ====================
def test_disease_models():
    """Test the disease models module"""
    print("🧪 Testing Disease Models Module...")
    
    # Test disease library
    covid = DiseaseLibrary.covid19_variant("omicron")
    flu = DiseaseLibrary.influenza()
    
    print(f"\n📊 Disease Parameters:")
    print(f"COVID-19 Omicron: R0={covid.R0}, Mortality={covid.mortality_rate}")
    print(f"Influenza: R0={flu.R0}, Seasonality={flu.seasonality_amplitude}")
    
    # Test that probabilities sum to 1
    print(f"\n✅ Probability Validation:")
    for variant in ["wildtype", "alpha", "delta", "omicron"]:
        disease = DiseaseLibrary.covid19_variant(variant)
        total = disease.p_asymptomatic + disease.p_mild + disease.p_severe + disease.p_critical
        print(f"{disease.name}: {total:.3f} (asymptomatic={disease.p_asymptomatic:.2f}, "
              f"mild={disease.p_mild:.2f}, severe={disease.p_severe:.2f}, critical={disease.p_critical:.2f})")
    
    # Test transmission calculator
    print(f"\n🎯 Transmission Calculator Test:")
    
    # Create a simple test network
    G = nx.erdos_renyi_graph(10, 0.3)
    for node in G.nodes():
        G.nodes[node]['age'] = np.random.randint(0, 80)
        G.nodes[node]['mobility'] = np.random.random()
        G.nodes[node]['immunity'] = 0.0
    
    # Calculate transmission probability
    prob = TransmissionCalculator.calculate_transmission_probability(
        infector=0,
        susceptible=1,
        G=G,
        disease=covid,
        interventions={'mask_mandate': True, 'mask_efficacy': 0.5},
        current_day=100
    )
    
    print(f"Transmission probability: {prob:.3f}")
    
    # Test disease progression
    print(f"\n🔄 Disease Progression Test:")
    progression = DiseaseProgression.determine_initial_course(
        age=45,
        disease=covid,
        vaccination_status=False
    )
    
    print(f"Symptoms: {progression['symptoms']}")
    print(f"Incubation: {progression['incubation_days']} days")
    print(f"Infectious: {progression['infectious_days']} days")
    print(f"Hospitalization: {progression['will_hospitalize']}")
    
    print("\n✅ Disease Models Module Test Complete!")

if __name__ == "__main__":
    test_disease_models()