# disease_models.py
import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

import numpy as np

logger = logging.getLogger(__name__)

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

    # Per-contact transmission scaling. R0 sets how infectious the disease is
    # in the abstract; this converts it into a per-contact probability for the
    # network at hand, and is what the "transmission rate (beta)" control sets.
    transmission_scale: float = 0.08
    
    # Incubation and infectious periods (days)
    incubation_period: Dict[str, float] = field(default_factory=lambda: {'mean': 5.2, 'std': 2.8})
    infectious_period: Dict[str, float] = field(default_factory=lambda: {'mean': 10.0, 'std': 3.0})
    
    # Severity probabilities
    p_asymptomatic: float = 0.4            # Probability of no symptoms
    p_mild: float = 0.4                    # Mild symptoms, no hospitalization
    p_severe: float = 0.15                 # Severe, may need hospitalization
    p_critical: float = 0.05               # Critical, ICU needed
    
    # Hospitalization and mortality
    hospitalization_rate: float = 0.25     # Overall hospitalization rate (25%)
    icu_rate: float = 0.08                 # % of hospitalized needing ICU (8%)
    mortality_rate: float = 0.03           # Overall case fatality rate (3%)
    
    # Age-stratified parameters - REALISTIC COVID-19 DATA
    age_stratification: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        '0-9':   {'severity': 0.02,  'hospitalization': 0.08, 'mortality': 0.001, 'susceptibility': 0.5},
        '10-19': {'severity': 0.03,  'hospitalization': 0.12, 'mortality': 0.002, 'susceptibility': 0.7},
        '20-29': {'severity': 0.05,  'hospitalization': 0.20, 'mortality': 0.005, 'susceptibility': 0.9},
        '30-39': {'severity': 0.08,  'hospitalization': 0.35, 'mortality': 0.010, 'susceptibility': 0.9},
        '40-49': {'severity': 0.12,  'hospitalization': 0.50, 'mortality': 0.020, 'susceptibility': 0.9},
        '50-59': {'severity': 0.18,  'hospitalization': 0.65, 'mortality': 0.050, 'susceptibility': 0.9},
        '60-69': {'severity': 0.28,  'hospitalization': 0.80, 'mortality': 0.120, 'susceptibility': 0.95},
        '70-79': {'severity': 0.42,  'hospitalization': 0.90, 'mortality': 0.280, 'susceptibility': 0.95},
        '80+':   {'severity': 0.58,  'hospitalization': 0.95, 'mortality': 0.450, 'susceptibility': 0.95}
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
        """Clamp and normalise parameters.

        User-supplied custom diseases go through here, so out-of-range values
        are corrected rather than raising - a slider combination should never
        take down the simulation with a 500.
        """
        self.R0 = float(np.clip(self.R0, 0.0, 20.0))
        self.transmission_scale = float(np.clip(self.transmission_scale, 0.0, 1.0))
        self.mortality_rate = float(np.clip(self.mortality_rate, 0.0, 1.0))
        self.hospitalization_rate = float(np.clip(self.hospitalization_rate, 0.0, 1.0))

        for period in (self.incubation_period, self.infectious_period):
            period['mean'] = max(1.0, float(period.get('mean', 5.0)))
            period['std'] = max(0.1, float(period.get('std', 1.0)))

        severities = [
            max(0.0, float(self.p_asymptomatic)),
            max(0.0, float(self.p_mild)),
            max(0.0, float(self.p_severe)),
            max(0.0, float(self.p_critical)),
        ]
        total = sum(severities)
        if total <= 0:
            severities = [0.4, 0.4, 0.15, 0.05]
            total = 1.0

        (self.p_asymptomatic, self.p_mild,
         self.p_severe, self.p_critical) = [s / total for s in severities]

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

        return disease.R0 * degree_factor * disease.transmission_scale
    
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

        # Social distancing. The key must match what the simulator writes in
        # `_apply_social_distancing`, otherwise the slider silently does
        # nothing and the default is used for every scenario.
        if interventions.get('social_distancing', False):
            compliance = interventions.get('distancing_compliance', 0.7)
            reduction = interventions.get('distancing_reduction', 0.3)

            inf_complies = random.random() < G.nodes[infector].get('compliance', 0.5)
            sus_complies = random.random() < G.nodes[susceptible].get('compliance', 0.5)

            if inf_complies or sus_complies:
                # Distancing works if either party keeps their distance; it
                # works better when both do.
                effective = reduction * compliance
                if not (inf_complies and sus_complies):
                    effective *= 0.5
                factor *= (1 - effective)

        # Case isolation (detected cases and hospital patients). Isolated
        # infectors are skipped outright in the transmission loop; this covers
        # an isolated susceptible.
        if G.nodes[susceptible].get('isolated', False):
            factor *= 0.1  # 90% reduction

        # Travel restrictions on long-distance contacts
        if interventions.get('travel_restrictions', False):
            edge_data = G.get_edge_data(infector, susceptible) or {}
            if 'random' in str(edge_data.get('type', '')):
                factor *= (1 - interventions.get('travel_reduction', 0.5))

        return factor

    @staticmethod
    def _mask_factor(infector, susceptible, G, interventions):
        """Mask effectiveness factor"""
        if not interventions.get('mask_mandate', False):
            return 1.0

        mask_efficacy = interventions.get('mask_efficacy', 0.5)

        inf_mask = G.nodes[infector].get('wears_mask', False)
        sus_mask = G.nodes[susceptible].get('wears_mask', False)

        if inf_mask and sus_mask:
            # Source control plus wearer protection
            return (1 - mask_efficacy) * (1 - mask_efficacy * 0.7)
        if inf_mask or sus_mask:
            return 1 - (mask_efficacy * 0.3)
        return 1.0

    @staticmethod
    def _immunity_factor(susceptible, G, disease):
        """Factor from vaccination / natural immunity."""
        attrs = G.nodes[susceptible]
        immunity = attrs.get('immunity', 0.0)

        if attrs.get('vaccinated', False):
            vaccine_eff = disease.vaccine_efficacy['infection']
            # `vaccination_day` is the attribute the simulator actually sets;
            # reading a non-existent `days_vaccinated` made vaccine waning a
            # no-op.
            days_since_vax = max(0, attrs.get('days_in_state', 0))
            waning_start = disease.vaccine_efficacy.get('waning_start', 120)

            if days_since_vax > waning_start:
                waned_days = days_since_vax - waning_start
                waning_rate = disease.vaccine_efficacy.get('waning_rate', 0.003)
                vaccine_eff *= max(0.0, 1 - waning_rate * waned_days)

            immunity = max(immunity, vaccine_eff)

        return max(0.0, 1 - immunity)
    
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
    """Handles individual disease progression through states."""

    # The age-stratified tables above are calibrated against a wildtype-like
    # disease. Variant-level (or user-supplied) rates are applied as a ratio
    # against these baselines, which is what makes the custom mortality and
    # hospitalisation inputs actually change the outcome.
    BASELINE_MORTALITY = 0.02
    BASELINE_HOSPITALIZATION = 0.15

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
        
        # Scale the age-stratified baselines by this disease's own rates so
        # variant selection and the custom-disease sliders take effect.
        hosp_scale = disease.hospitalization_rate / DiseaseProgression.BASELINE_HOSPITALIZATION
        mortality_scale = disease.mortality_rate / DiseaseProgression.BASELINE_MORTALITY

        # Set parameters based on symptoms
        if symptoms == 'asymptomatic':
            inc_mean = disease.incubation_period['mean'] * 0.8
            inf_mean = disease.infectious_period['mean'] * 0.7
            hospitalization_prob = 0.0
        elif symptoms == 'mild':
            inc_mean = disease.incubation_period['mean']
            inf_mean = disease.infectious_period['mean'] * 0.9
            hospitalization_prob = 0.02 * age_params['hospitalization'] * hosp_scale
        elif symptoms == 'severe':
            inc_mean = disease.incubation_period['mean'] * 0.9
            inf_mean = disease.infectious_period['mean'] * 1.2
            hospitalization_prob = 0.80 * age_params['hospitalization'] * hosp_scale
        else:  # critical
            inc_mean = disease.incubation_period['mean'] * 0.8
            inf_mean = disease.infectious_period['mean'] * 1.5
            hospitalization_prob = 0.95 * age_params['hospitalization'] * hosp_scale

        hospitalization_prob = min(1.0, hospitalization_prob)

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
        
        # Base mortality from age, scaled by this disease's own fatality rate
        base_mortality = age_params['mortality'] * mortality_scale

        # Adjust mortality based on symptoms
        if symptoms == 'asymptomatic':
            mortality_prob = base_mortality * 0.05  # Very low
        elif symptoms == 'mild':
            mortality_prob = base_mortality * 0.5   # Low-moderate
        elif symptoms == 'severe':
            mortality_prob = base_mortality * 2.5   # Moderate-high
        else:  # critical
            mortality_prob = base_mortality * 8.0   # Very high

        # Apply vaccine protection
        if vaccination_status:
            ve_severity = disease.vaccine_efficacy['severity']
            mortality_prob *= (1 - ve_severity * 0.8)  # Vaccines protect against death
        
        # Ensure probability is reasonable but can be high for critical cases
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
        
        # Exactly one terminal outcome is scheduled per case.
        if will_die:
            recovery_day = None
            if not death_day or death_day <= 0:
                death_day = incubation_days + infectious_days
        else:
            death_day = None
            recovery_day = incubation_days + infectious_days

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
    # Natural immunity half-life is roughly a year once waning starts
    NATURAL_WANING_START = 90
    NATURAL_WANING_RATE = 0.0019  # per day, ~50% loss per year

    @staticmethod
    def update_immunity(node, G, disease, current_day):
        """Apply one day of immunity waning to a recovered or vaccinated node."""
        attrs = G.nodes[node]
        state = attrs.get('state')

        if state not in ('R', 'V'):
            return

        immunity = attrs.get('immunity', 0.0)
        if immunity <= 0.0:
            return

        if state == 'R':
            days = attrs.get('days_in_state', 0)
            start = DiseaseProgression.NATURAL_WANING_START
            rate = DiseaseProgression.NATURAL_WANING_RATE
        else:
            vaccination_day = attrs.get('vaccination_day', current_day)
            days = max(0, current_day - vaccination_day)
            start = disease.vaccine_efficacy.get('waning_start', 120)
            rate = disease.vaccine_efficacy.get('waning_rate', 0.003)

        if days <= start:
            return

        # Exponential decay applied once per day after the waning start
        attrs['immunity'] = max(0.0, min(1.0, immunity * (1 - rate)))
class InterventionSchedule:
    """Manages timing and application of interventions"""
    
    def __init__(self):
        self.scheduled_interventions = []
    
    def add_intervention(self, day, intervention_type, **params):
        """Schedule an intervention to start on specific day"""
        self.scheduled_interventions.append({
            'day': int(day),
            'type': intervention_type,
            'params': params
        })
        # Sort by day
        self.scheduled_interventions.sort(key=lambda x: x['day'])
        logger.info("Scheduled %s for day %s with params %s", intervention_type, day, params)
    
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
                {'day': 45, 'type': 'social_distancing', 'params': {'reduction': 0.3, 'compliance': 0.6}},
                {'day': 60, 'type': 'vaccination', 'params': {'rate': 0.02, 'efficacy': 0.9, 'priority': 'age'}},
                {'day': 75, 'type': 'lockdown', 'params': {'strictness': 0.7, 'compliance': 0.8}},
                {'day': 120, 'type': 'reopen', 'params': {'gradual': True}}
            ],
            'rapid_response': [
                {'day': 7, 'type': 'mask_mandate', 'params': {'efficacy': 0.6, 'compliance': 0.8}},
                {'day': 14, 'type': 'testing', 'params': {'rate': 0.1, 'accuracy': 0.95, 'delay': 1}},
                {'day': 21, 'type': 'social_distancing', 'params': {'reduction': 0.5, 'compliance': 0.7}},
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
        
        if scenario_name not in scenarios:
            # An unrecognised scenario falls back to no interventions rather
            # than failing the whole simulation run.
            logger.warning("Unknown scenario '%s'; running with no interventions", scenario_name)
            scenario_name = 'no_intervention'

        self.scheduled_interventions = [dict(item) for item in scenarios[scenario_name]]
        logger.info("Created '%s' scenario with %d interventions",
                    scenario_name, len(self.scheduled_interventions))
        return self.scheduled_interventions
