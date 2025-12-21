# simulator_engine.py
import numpy as np
import networkx as nx
from collections import defaultdict, deque
import random
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import json
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class UltimateSimulator:
    """
    Complete epidemic simulator with network, disease, and interventions
    Time Complexity: O(N + E) per day with optimizations
    Space Complexity: O(N + E) for network + O(N) for tracking
    """
    
    def __init__(self, G, disease_params, interventions=None):
        """
        Initialize simulator with network and disease
        
        Args:
            G: NetworkX graph (from network_generator)
            disease_params: DiseaseParameters object
            interventions: Dict of initial interventions
        """
        self.G = G.copy()  # Work on a copy
        self.disease = disease_params
        self.interventions = interventions or {}
        
        # Simulation state
        self.time = 0  # Current day
        self.running = False
        
        # Efficient data structures for tracking
        self._initialize_tracking()
        
        # Statistics and history
        self.history = defaultdict(list)
        self.event_queue = deque()  # For scheduled events
        self.stats = {
            'total_infected': 0,
            'total_recovered': 0,
            'total_deaths': 0,
            'total_vaccinated': 0,
            'peak_infections': 0,
            'peak_day': 0,
            'total_hospitalized': 0,
            'hospital_bed_usage': [],  # Time series
            'r_effective': []  # Time-varying R
        }
        
        # Performance optimization
        self._cache_neighbors = {}
        self._last_R0_calculation = 0
        
        # Visualization data
        self.visualization_data = {
            'node_positions': None,
            'node_colors': [],
            'infection_paths': []
        }
    
    def _initialize_tracking(self):
        """Initialize efficient data structures for state tracking"""
        # Fast state lookups using sets
        self.state_sets = {
            'S': set(self.G.nodes()),  # All start susceptible
            'E': set(),
            'I': set(),
            'R': set(),
            'D': set(),
            'V': set()
        }
        
        # Infectious subsets for different severity
        self.infectious_subsets = {
            'Ia': set(),  # Asymptomatic
            'Im': set(),  # Mild
            'Is': set(),  # Severe
            'Ih': set(),  # Hospitalized
            'Ic': set()   # Critical
        }
        
        # Time-based event tracking
        self.transition_times = defaultdict(list)
        self.recovery_schedule = defaultdict(list)
        
        # Infection tree (for contact tracing)
        self.infection_tree = {}
        
        # Cache for frequently accessed data
        self._degree_cache = {node: self.G.degree(node) for node in self.G.nodes()}
        
        print(f"✅ Simulator initialized with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges")
    
    # ==================== INFECTION METHODS ====================
    
    def seed_infections(self, n_infections=10, method='random', **kwargs):
        """
        Seed initial infections in the population
        
        Methods:
        - 'random': Random nodes
        - 'hubs': Most connected nodes
        - 'mobile': Highest mobility nodes
        - 'geographic': Cluster in one area
        - 'age_targeted': Target specific age groups
        """
        infected_nodes = []
        
        if method == 'random':
            infected_nodes = random.sample(list(self.G.nodes()), min(n_infections, len(self.G)))
            
        elif method == 'hubs':
            # Sort by degree (most connected first)
            nodes_by_degree = sorted(self.G.nodes(), 
                                   key=lambda n: self._degree_cache[n], 
                                   reverse=True)
            infected_nodes = nodes_by_degree[:n_infections]
            
        elif method == 'mobile':
            # Sort by mobility
            nodes_by_mobility = sorted(self.G.nodes(),
                                     key=lambda n: self.G.nodes[n].get('mobility', 0.5),
                                     reverse=True)
            infected_nodes = nodes_by_mobility[:n_infections]
            
        elif method == 'geographic':
            # If we have positions, cluster infections
            if 'positions' in kwargs:
                positions = kwargs['positions']
                center_node = random.choice(list(self.G.nodes()))
                center_pos = positions[center_node]
                
                # Find nodes close to center
                distances = []
                for node in self.G.nodes():
                    if node in positions:
                        dist = np.linalg.norm(np.array(positions[node]) - np.array(center_pos))
                        distances.append((node, dist))
                
                distances.sort(key=lambda x: x[1])
                infected_nodes = [node for node, _ in distances[:n_infections]]
            else:
                infected_nodes = random.sample(list(self.G.nodes()), n_infections)
                
        elif method == 'age_targeted':
            target_age = kwargs.get('target_age', (20, 40))
            age_nodes = [n for n in self.G.nodes() 
                        if target_age[0] <= self.G.nodes[n]['age'] <= target_age[1]]
            infected_nodes = random.sample(age_nodes, min(n_infections, len(age_nodes)))
        
        else:
            infected_nodes = random.sample(list(self.G.nodes()), n_infections)
        
        # Infect the selected nodes
        for node in infected_nodes:
            self._infect_node(node, source='seed')
            
        print(f"🌱 Seeded {len(infected_nodes)} initial infections using '{method}' method")
        return infected_nodes
    
    def _infect_node(self, node, source='unknown'):
        """
        Infect a node and determine disease progression
        Time Complexity: O(1) for infection + O(k) for contact tracing
        """
        # Update node state
        self.G.nodes[node]['state'] = 'E'  # Exposed
        self.G.nodes[node]['infected_by'] = source
        self.G.nodes[node]['infection_time'] = self.time
        self.G.nodes[node]['days_in_state'] = 0
        
        # Remove from susceptible, add to exposed
        self.state_sets['S'].discard(node)
        self.state_sets['E'].add(node)
        
        # Determine disease progression
        age = self.G.nodes[node]['age']
        vaccinated = self.G.nodes[node].get('vaccinated', False)
        
        # Get disease course
        from disease_models import DiseaseProgression
        progression = DiseaseProgression.determine_initial_course(
            age, self.disease, vaccinated
        )
        
        # DEBUG: Print progression data to see what's happening
        print(f"DEBUG: Node {node} (age {age}) progression:")
        print(f"  Symptoms: {progression['symptoms']}")
        print(f"  Will die: {progression['will_die']}")
        print(f"  Recovery day: {progression['recovery_day']}")
        print(f"  Death day: {progression['death_day']}")
        
        # Store progression data
        self.G.nodes[node]['symptoms'] = progression['symptoms']
        self.G.nodes[node]['incubation_days'] = progression['incubation_days']
        self.G.nodes[node]['infectious_days'] = progression['infectious_days']
        self.G.nodes[node]['will_hospitalize'] = progression['will_hospitalize']
        self.G.nodes[node]['will_die'] = progression['will_die']
        
        # Schedule state transitions
        # 1. Become infectious after incubation
        incubation_days = progression['incubation_days']
        if incubation_days and incubation_days > 0:
            self._schedule_event(node, 'become_infectious', incubation_days)
        else:
            # Default if incubation_days is invalid
            self._schedule_event(node, 'become_infectious', 5)
            print(f"⚠️  Warning: Invalid incubation days for node {node}, using default 5")
        
        # 2. Hospitalization if needed
        if progression.get('will_hospitalize', False) and progression.get('hospital_day'):
            hospital_day = progression['hospital_day']
            if hospital_day and hospital_day > 0:
                self._schedule_event(node, 'hospitalize', hospital_day)
        
        # 3. Death if fatal - FIXED: Only schedule if death_day exists and is valid
        if progression.get('will_die', False) and progression.get('death_day'):
            death_day = progression['death_day']
            if death_day and death_day > 0:
                self._schedule_event(node, 'die', death_day)
                print(f"💀 Scheduled death for node {node} on day {self.time + death_day}")
            else:
                print(f"⚠️  Warning: Invalid death_day ({death_day}) for node {node}")
        
        # 4. Recovery - only schedule if not fatal and recovery_day exists
        if not progression.get('will_die', False) and progression.get('recovery_day'):
            recovery_day = progression['recovery_day']
            if recovery_day and recovery_day > 0:
                self._schedule_event(node, 'recover', recovery_day)
            else:
                print(f"⚠️  Warning: Invalid recovery_day ({recovery_day}) for node {node}")
        elif progression.get('will_die', False):
            print(f"ℹ️  Node {node} will die, skipping recovery scheduling")
        else:
            print(f"⚠️  Warning: No recovery day for node {node}")
        
        # Update infection tree for contact tracing
        if source != 'seed':
            if source not in self.infection_tree:
                self.infection_tree[source] = []
            self.infection_tree[source].append(node)
        
        # Update statistics
        self.stats['total_infected'] += 1
        
        # For visualization
        self.visualization_data['infection_paths'].append({
            'from': source if source != 'seed' else None,
            'to': node,
            'time': self.time
        })
    # ==================== TRANSMISSION STEP ====================
    
    def _transmission_step(self):
        """
        Execute disease transmission for one day
        Time Complexity: O(I × k) where I = infectious nodes, k = avg degree
        Optimized using neighbor caching and early termination
        """
        new_infections = 0
        
        # Get all infectious nodes (all types)
        all_infectious = set()
        for subset in self.infectious_subsets.values():
            all_infectious.update(subset)
        
        # If no infectious nodes, return early
        if not all_infectious:
            return 0
        
        # Pre-calculate intervention factors for this day
        intervention_cache = self._cache_intervention_factors()
        
        # Process each infectious node
        for infector in list(all_infectious):
            # Skip if isolated or hospitalized (reduced transmission)
            if self.G.nodes[infector].get('isolated', False):
                continue
            
            # Get neighbors (cached for performance)
            if infector not in self._cache_neighbors:
                self._cache_neighbors[infector] = list(self.G.neighbors(infector))
            neighbors = self._cache_neighbors[infector]
            
            # Apply mobility-based contact reduction
            mobility = self.G.nodes[infector].get('mobility', 1.0)
            if mobility < 1.0:
                n_contacts = int(len(neighbors) * mobility)
                if n_contacts < len(neighbors):
                    neighbors = random.sample(neighbors, n_contacts)
            
            # Try to infect each susceptible neighbor
            for contact in neighbors:
                # Fast check: is contact susceptible?
                if self.G.nodes[contact]['state'] != 'S':
                    continue
                
                # Check if edge is active (for travel restrictions)
                edge_data = self.G.get_edge_data(infector, contact, {})
                if not edge_data.get('active', True):
                    continue
                
                # Calculate transmission probability
                from disease_models import TransmissionCalculator
                transmission_prob = TransmissionCalculator.calculate_transmission_probability(
                    infector=infector,
                    susceptible=contact,
                    G=self.G,
                    disease=self.disease,
                    interventions=intervention_cache,
                    current_day=self.time
                )
                
                # Apply transmission
                if random.random() < transmission_prob:
                    self._infect_node(contact, source=infector)
                    new_infections += 1
                    
                    # Early termination if we've infected too many this step
                    if new_infections > len(self.state_sets['S']) * 0.1:  # 10% of susceptibles
                        print(f"⚠️  High transmission rate: {new_infections} new infections")
                        break
        
        return new_infections
    
    def _cache_intervention_factors(self):
        """Cache intervention factors for performance"""
        cache = self.interventions.copy()
        
        # Add compliance-based factors
        if 'mask_mandate' in cache:
            cache['mask_compliance'] = cache.get('mask_compliance', 0.7)
        
        if 'social_distancing' in cache:
            cache['distancing_compliance'] = cache.get('distancing_compliance', 0.6)
        
        return cache
    
    # ==================== INTERVENTION METHODS ====================
    
    def apply_intervention(self, intervention_type, **params):
        """
        Apply any intervention type with parameters
        """
        if intervention_type == 'lockdown':
            self._apply_lockdown(**params)
        elif intervention_type == 'social_distancing':
            self._apply_social_distancing(**params)
        elif intervention_type == 'mask_mandate':
            self._apply_mask_mandate(**params)
        elif intervention_type == 'vaccination':
            self._apply_vaccination(**params)
        elif intervention_type == 'testing':
            self._apply_testing(**params)
        elif intervention_type == 'isolation':
            self._apply_isolation(**params)
        elif intervention_type == 'travel_restrictions':
            self._apply_travel_restrictions(**params)
        elif intervention_type == 'hygiene':
            self._apply_hygiene(**params)
        elif intervention_type == 'ventilation':
            self._apply_ventilation(**params)
        elif intervention_type == 'reopen':
            self._apply_reopen(**params)
        else:
            print(f"⚠️  Unknown intervention: {intervention_type}")
    
    def _apply_lockdown(self, strictness=0.7, compliance=0.8, duration=None):
        """Apply lockdown - reduces mobility and contacts"""
        self.interventions['lockdown'] = True
        self.interventions['lockdown_strictness'] = strictness
        self.interventions['lockdown_compliance'] = compliance
        
        print(f"🔒 Lockdown initiated: strictness={strictness}, compliance={compliance}")
        
        # Apply to individuals based on compliance
        for node in self.G.nodes():
            if random.random() < compliance:
                # Reduce mobility
                current_mobility = self.G.nodes[node].get('mobility', 0.5)
                self.G.nodes[node]['mobility'] = current_mobility * (1 - strictness)
                
                # Mark as isolated if strict lockdown
                if strictness > 0.6:
                    self.G.nodes[node]['isolated'] = True
        
        # Schedule lockdown end if duration specified
        if duration:
            self._schedule_intervention_end('lockdown', duration)
    
    def _apply_social_distancing(self, reduction=0.3, compliance=0.7):
        """Apply social distancing"""
        self.interventions['social_distancing'] = True
        self.interventions['distancing_factor'] = reduction
        self.interventions['distancing_compliance'] = compliance
        
        print(f"↔️  Social distancing: reduction={reduction}, compliance={compliance}")
    
    def _apply_mask_mandate(self, efficacy=0.5, compliance=0.7):
        """Apply mask mandate"""
        self.interventions['mask_mandate'] = True
        self.interventions['mask_efficacy'] = efficacy
        self.interventions['mask_compliance'] = compliance
        
        # Assign masks to compliant individuals
        for node in self.G.nodes():
            if random.random() < compliance:
                self.G.nodes[node]['wears_mask'] = True
        
        print(f"😷 Mask mandate: efficacy={efficacy}, compliance={compliance}")
    
    def _apply_vaccination(self, rate=0.01, efficacy=0.9, priority='age', daily_capacity=None):
        """Vaccinate population"""
        self.interventions['vaccination'] = True
        self.interventions['vaccination_rate'] = rate
        self.interventions['vaccine_efficacy'] = efficacy
        self.interventions['vaccine_priority'] = priority
        
        # Determine vaccination order
        if priority == 'age':
            # Prioritize elderly (highest risk)
            candidates = sorted(self.state_sets['S'], 
                              key=lambda n: self.G.nodes[n]['age'], 
                              reverse=True)
        elif priority == 'frontline':
            # Prioritize high-mobility (essential workers)
            candidates = sorted(self.state_sets['S'],
                              key=lambda n: self.G.nodes[n].get('mobility', 0.5),
                              reverse=True)
        elif priority == 'random':
            candidates = list(self.state_sets['S'])
            random.shuffle(candidates)
        elif priority == 'vulnerable':
            # Prioritize by health risk
            candidates = sorted(self.state_sets['S'],
                              key=lambda n: self.G.nodes[n].get('health_risk', 0.5),
                              reverse=True)
        else:
            candidates = list(self.state_sets['S'])
        
        # Apply capacity limit if specified
        if daily_capacity:
            rate = min(rate, daily_capacity / len(self.state_sets['S']))
        
        # Number to vaccinate today
        n_to_vaccinate = int(rate * len(candidates))
        
        for i, node in enumerate(candidates[:n_to_vaccinate]):
            # Vaccine efficacy check
            if random.random() < efficacy:
                self.G.nodes[node]['state'] = 'V'
                self.G.nodes[node]['vaccinated'] = True
                self.G.nodes[node]['vaccination_day'] = self.time
                self.G.nodes[node]['immunity'] = 0.95  # Initial high immunity
                
                # Update state sets
                self.state_sets['S'].discard(node)
                self.state_sets['V'].add(node)
                
                self.stats['total_vaccinated'] += 1
        
        print(f"💉 Vaccinated {n_to_vaccinate} individuals with priority='{priority}'")
    
    def _apply_testing(self, rate=0.05, accuracy=0.95, delay=2, isolation_compliance=0.8):
        """Implement testing regime"""
        self.interventions['testing'] = True
        self.interventions['testing_rate'] = rate
        self.interventions['testing_accuracy'] = accuracy
        self.interventions['testing_delay'] = delay
        
        # Test infectious individuals
        infectious = list(self.infectious_subsets['Ia'] | self.infectious_subsets['Im'] | 
                         self.infectious_subsets['Is'] | self.infectious_subsets['Ih'])
        
        n_to_test = int(rate * len(infectious))
        tested = random.sample(infectious, min(n_to_test, len(infectious)))
        
        for node in tested:
            if random.random() < accuracy:
                # Test positive - schedule isolation
                self._schedule_event(node, 'isolate', delay)
        
        print(f"🧪 Testing: rate={rate}, accuracy={accuracy}, tested {len(tested)} individuals")
    
    def _apply_isolation(self, compliance=0.8):
        """Isolate infected individuals"""
        self.interventions['isolation'] = True
        self.interventions['isolation_compliance'] = compliance
        
        # Find symptomatic infectious individuals
        symptomatic = [n for n in (self.infectious_subsets['Im'] | 
                                  self.infectious_subsets['Is'] | 
                                  self.infectious_subsets['Ih'])
                      if random.random() < compliance]
        
        for node in symptomatic:
            self.G.nodes[node]['isolated'] = True
        
        print(f"🏠 Isolation: compliance={compliance}, isolated {len(symptomatic)} individuals")
    
    def _apply_travel_restrictions(self, reduction=0.5):
        """Restrict long-distance travel"""
        self.interventions['travel_restrictions'] = True
        self.interventions['travel_reduction'] = reduction
        
        # Deactivate long-distance connections
        for u, v, data in self.G.edges(data=True):
            if data.get('type') == 'random':  # Long-distance
                if random.random() < reduction:
                    self.G[u][v]['active'] = False
        
        print(f"✈️  Travel restrictions: reduction={reduction}")
    
    def _apply_hygiene(self, improvement=0.3):
        """Improve hygiene practices"""
        self.interventions['hygiene'] = True
        self.interventions['hygiene_improvement'] = improvement
        print(f"🧼 Hygiene improvement: {improvement}")
    
    def _apply_ventilation(self, improvement=0.4):
        """Improve ventilation"""
        self.interventions['ventilation'] = True
        self.interventions['ventilation_improvement'] = improvement
        print(f"💨 Ventilation improvement: {improvement}")
    
    def _apply_reopen(self, gradual=True):
        """Reopen society after restrictions"""
        if 'lockdown' in self.interventions:
            del self.interventions['lockdown']
        
        # Gradually restore mobility
        for node in self.G.nodes():
            if self.G.nodes[node].get('isolated', False):
                self.G.nodes[node]['isolated'] = False
                
            if gradual:
                # Gradually increase mobility over 14 days
                current = self.G.nodes[node].get('mobility', 0.3)
                target = min(0.9, current * 1.5)
                self.G.nodes[node]['mobility'] = target
        
        print("🏙️  Society reopening" + (" (gradual)" if gradual else ""))
    
    def _schedule_intervention_end(self, intervention_type, duration):
        """Schedule end of an intervention"""
        end_day = self.time + duration
        self._schedule_event(None, f'end_{intervention_type}', duration)
    
    # ==================== EVENT PROCESSING ====================
    
    def _schedule_event(self, node, action, days_from_now):
        """Schedule an event for future execution"""
        event_time = self.time + days_from_now
        event = {
            'node': node,
            'action': action,
            'scheduled_time': event_time
        }
        
        # Insert in sorted order
        if not self.event_queue or event_time >= self.event_queue[-1][0]:
            self.event_queue.append((event_time, event))
        else:
            # Find insertion point (maintain sorted order)
            for i, (t, _) in enumerate(self.event_queue):
                if event_time < t:
                    self.event_queue.insert(i, (event_time, event))
                    break
    
    def _process_events(self):
        """Process all events scheduled for current day"""
        processed = 0
        
        while self.event_queue and self.event_queue[0][0] == self.time:
            _, event = self.event_queue.popleft()
            self._execute_event(event)
            processed += 1
        
        return processed
    
    def _execute_event(self, event):
        """Execute a scheduled event"""
        node = event['node']
        action = event['action']
        
        if action == 'become_infectious':
            # Move from Exposed to Infectious
            self.G.nodes[node]['state'] = 'I'
            self.G.nodes[node]['days_in_state'] = 0
            
            # Update state sets
            self.state_sets['E'].discard(node)
            self.state_sets['I'].add(node)
            
            # Add to appropriate infectious subset
            symptoms = self.G.nodes[node].get('symptoms', 'mild')
            if symptoms == 'asymptomatic':
                self.infectious_subsets['Ia'].add(node)
            elif symptoms == 'mild':
                self.infectious_subsets['Im'].add(node)
            elif symptoms == 'severe':
                self.infectious_subsets['Is'].add(node)
            elif symptoms == 'critical':
                self.infectious_subsets['Ic'].add(node)
        
        elif action == 'hospitalize':
            self.G.nodes[node]['state'] = 'Ih'
            self.G.nodes[node]['hospitalized'] = True
            self.G.nodes[node]['days_in_state'] = 0
            
            # Remove from previous infectious subset
            for key in ['Ia', 'Im', 'Is', 'Ic']:
                self.infectious_subsets[key].discard(node)
            
            self.infectious_subsets['Ih'].add(node)
            self.stats['total_hospitalized'] += 1
        
        elif action == 'recover':
            self.G.nodes[node]['state'] = 'R'
            self.G.nodes[node]['days_in_state'] = 0
            self.G.nodes[node]['immunity'] = 0.8  # Natural immunity
            
            # Remove from all infectious subsets
            for key in self.infectious_subsets:
                self.infectious_subsets[key].discard(node)
            
            # Update state sets
            self.state_sets['I'].discard(node)
            self.state_sets['R'].add(node)
            
            self.stats['total_recovered'] += 1
        
        elif action == 'die':
            self.G.nodes[node]['state'] = 'D'
            
            # Remove from all sets
            for state_set in self.state_sets.values():
                state_set.discard(node)
            for inf_set in self.infectious_subsets.values():
                inf_set.discard(node)
            
            self.stats['total_deaths'] += 1
        
        elif action == 'isolate':
            self.G.nodes[node]['isolated'] = True
        
        elif action.startswith('end_'):
            # End an intervention
            intervention_type = action[4:]  # Remove 'end_'
            if intervention_type in self.interventions:
                del self.interventions[intervention_type]
                print(f"⏹️  Ended intervention: {intervention_type}")
    
    # ==================== SIMULATION LOOP ====================
    
    def step(self, days=1):
        """
        Execute simulation for specified number of days
        Returns: new_infections for each day
        """
        new_infections_list = []
        
        for _ in range(days):
            # 1. Process scheduled events
            self._process_events()
            
            # 2. Apply scheduled interventions
            self._apply_scheduled_interventions()
            
            # 3. Disease transmission
            new_infections = self._transmission_step()
            new_infections_list.append(new_infections)
            
            # 4. Update state durations
            for node in self.G.nodes():
                self.G.nodes[node]['days_in_state'] += 1
            
            # 5. Update immunity (waning)
            from disease_models import DiseaseProgression
            for node in self.G.nodes():
                DiseaseProgression.update_immunity(node, self.G, self.disease, self.time)
            
            # 6. Record history and statistics
            self._record_history()
            self._update_statistics()
            
            # 7. Increment time
            self.time += 1
        
        return new_infections_list
    
    def run(self, days=100, show_progress=True):
        """
        Run complete simulation for specified days
        Returns: history dictionary
        """
        print(f"🚀 Starting simulation for {days} days...")
        
        self.running = True
        progress_range = tqdm(range(days)) if show_progress else range(days)
        
        for day in progress_range:
            self.step(1)
            
            # Update progress bar
            if show_progress:
                infectious = len(self.state_sets['I'])
                progress_range.set_description(
                    f"Day {day+1}: {infectious} infectious, {self.stats['total_deaths']} deaths"
                )
        
        self.running = False
        print(f"✅ Simulation complete after {days} days")
        print(f"   Final: {len(self.state_sets['S'])} susceptible, "
              f"{len(self.state_sets['I'])} infectious, "
              f"{len(self.state_sets['R'])} recovered, "
              f"{len(self.state_sets['D'])} deaths")
        
        return self.history
    
    def _apply_scheduled_interventions(self):
        """Apply interventions scheduled for specific days"""
        # Example: Start vaccination on day 60
        if self.time == 60 and not self.interventions.get('vaccination', False):
            self.apply_intervention('vaccination', rate=0.02, efficacy=0.9, priority='age')
        
        # Example: Start lockdown on day 30 if cases > threshold
        if (self.time == 30 and 
            not self.interventions.get('lockdown', False) and
            len(self.state_sets['I']) > 50):
            self.apply_intervention('lockdown', strictness=0.7, compliance=0.8)
        
        # Example: Lift lockdown on day 90
        if self.time == 90 and self.interventions.get('lockdown', False):
            self.apply_intervention('reopen', gradual=True)
    
    def _record_history(self):
        """Record current state for analysis"""
        self.history['time'].append(self.time)
        
        # Record all state counts
        for state in ['S', 'E', 'I', 'R', 'D', 'V']:
            self.history[state].append(len(self.state_sets[state]))
        
        # Record infectious subtypes
        for inf_state in ['Ia', 'Im', 'Is', 'Ih', 'Ic']:
            self.history[inf_state].append(len(self.infectious_subsets[inf_state]))
        
        # Record interventions
        self.history['interventions'].append(self.interventions.copy())
        
        # Record new infections
        if self.time == 0:
            self.history['new_infections'].append(0)
        else:
            current_E = len(self.state_sets['E'])
            prev_E = self.history['E'][-2] if len(self.history['E']) > 1 else 0
            new_infections = current_E - prev_E
            self.history['new_infections'].append(new_infections)
    
    def _update_statistics(self):
        """Update simulation statistics"""
        current_infectious = len(self.state_sets['I'])
        
        # Update peak infections
        if current_infectious > self.stats['peak_infections']:
            self.stats['peak_infections'] = current_infectious
            self.stats['peak_day'] = self.time
        
        # Calculate effective R
        if self.time >= 7:  # Need some history
            recent_infections = self.history['new_infections'][-7:]  # Last 7 days
            if sum(recent_infections) > 0:
                # Simple R estimation
                if len(self.history['new_infections']) >= 14:
                    current_avg = np.mean(recent_infections)
                    prev_avg = np.mean(self.history['new_infections'][-14:-7])
                    if prev_avg > 0:
                        r_eff = current_avg / prev_avg
                        self.stats['r_effective'].append(r_eff)
        
        # Hospital bed usage
        hospitalized = len(self.infectious_subsets['Ih']) + len(self.infectious_subsets['Ic'])
        self.stats['hospital_bed_usage'].append(hospitalized)
    
    # ==================== ANALYSIS METHODS ====================
    
    def run_with_animation(self, days=100, save_checkpoints=True, checkpoint_interval=5):
        """
        Run simulation while saving states for animation
        
        Args:
            days: Number of days to simulate
            save_checkpoints: Save state at intervals
            checkpoint_interval: Days between saved states
            
        Returns:
            history and checkpoints for animation
        """
        print(f"🎬 Running simulation with animation checkpoints...")
        
        # Initialize checkpoints
        self.checkpoints = {}
        
        # Save initial state
        if save_checkpoints:
            self._save_checkpoint(0)
        
        # Run simulation with periodic saving
        for day in range(days):
            self.step(1)
            
            # Save checkpoint at intervals
            if save_checkpoints and (day % checkpoint_interval == 0 or day == days - 1):
                self._save_checkpoint(self.time)
            
            # Progress indicator
            if day % 10 == 0:
                infectious = len(self.state_sets['I'])
                print(f"  Day {day}: {infectious} infectious individuals")
        
        print(f"✅ Simulation complete with {len(self.checkpoints)} animation checkpoints")
        return self.history, self.checkpoints
    
    def _save_checkpoint(self, day):
        """Save simulation state for animation"""
        # Save node states
        node_states = {}
        for node in self.G.nodes():
            node_states[node] = self.G.nodes[node].get('state', 'S')
        
        # Save current statistics
        stats = {
            'S': len(self.state_sets['S']),
            'E': len(self.state_sets['E']),
            'I': len(self.state_sets['I']),
            'R': len(self.state_sets['R']),
            'D': len(self.state_sets['D']),
            'V': len(self.state_sets.get('V', set()))
        }
        
        self.checkpoints[day] = {
            'node_states': node_states,
            'statistics': stats,
            'time': day
        }
    
    def restore_from_checkpoint(self, day):
        """Restore simulation state from checkpoint"""
        if day not in self.checkpoints:
            print(f"⚠️ No checkpoint for day {day}")
            return
        
        checkpoint = self.checkpoints[day]
        
        # Restore node states
        for node, state in checkpoint['node_states'].items():
            self.G.nodes[node]['state'] = state
        
        # Restore state sets
        self._rebuild_state_sets()
        
        # Restore time
        self.time = day
        
        print(f"✅ Restored simulation to day {day}")
    
    def _rebuild_state_sets(self):
        """Rebuild state sets from node states"""
        # Clear existing sets
        for state_set in self.state_sets.values():
            state_set.clear()
        
        # Rebuild from node states
        for node in self.G.nodes():
            state = self.G.nodes[node].get('state', 'S')
            if state in self.state_sets:
                self.state_sets[state].add(node)
    
    def get_summary_stats(self):
        """Get comprehensive statistics"""
        return {
            'total_days': self.time,
            'initial_population': len(self.G),
            'final_susceptible': len(self.state_sets['S']),
            'total_infected': self.stats['total_infected'],
            'total_recovered': self.stats['total_recovered'],
            'total_deaths': self.stats['total_deaths'],
            'total_vaccinated': self.stats['total_vaccinated'],
            'peak_infections': self.stats['peak_infections'],
            'peak_day': self.stats['peak_day'],
            'attack_rate': self.stats['total_infected'] / len(self.G),
            'case_fatality_rate': (self.stats['total_deaths'] / 
                                  max(1, self.stats['total_infected'])),
            'final_r_effective': (self.stats['r_effective'][-1] 
                                 if self.stats['r_effective'] else 0)
        }
    
    def get_infection_tree(self, max_depth=3):
        """Get infection transmission tree up to specified depth"""
        tree = {}
        
        def build_tree(node, depth=0):
            if depth >= max_depth:
                return None
            
            if node in self.infection_tree:
                children = []
                for child in self.infection_tree[node]:
                    child_data = {
                        'id': child,
                        'age': self.G.nodes[child]['age'],
                        'infection_time': self.G.nodes[child].get('infection_time', 0),
                        'symptoms': self.G.nodes[child].get('symptoms', 'unknown'),
                        'children': build_tree(child, depth + 1)
                    }
                    children.append(child_data)
                return children
            return []
        
        # Start from seed infections
        seed_infections = [n for n in self.G.nodes() 
                          if self.G.nodes[n].get('infected_by') == 'seed']
        
        for seed in seed_infections[:5]:  # Limit to 5 seeds for readability
            tree[seed] = build_tree(seed)
        
        return tree
    
    def get_network_metrics(self):
        """Calculate network metrics relevant to disease spread"""
        metrics = {
            'avg_degree': np.mean([d for _, d in self.G.degree()]),
            'degree_assortativity': nx.degree_assortativity_coefficient(self.G),
            'avg_clustering': nx.average_clustering(self.G),
            'diameter': nx.diameter(self.G) if nx.is_connected(self.G) else float('inf'),
            'avg_path_length': nx.average_shortest_path_length(self.G) 
                              if nx.is_connected(self.G) else float('inf'),
        }
        
        # Super-spreader identification (top 5% by degree)
        degrees = [(n, d) for n, d in self.G.degree()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        n_superspreaders = max(1, int(0.05 * len(self.G)))
        superspreaders = degrees[:n_superspreaders]
        
        metrics['superspreader_count'] = n_superspreaders
        metrics['superspreader_avg_degree'] = np.mean([d for _, d in superspreaders])
        
        return metrics
    
    # ==================== VISUALIZATION METHODS ====================
    
    def compute_force_directed_layout(self, iterations=50):
        """Compute force-directed layout for visualization"""
        print("🎨 Computing force-directed layout...")
        
        # Use NetworkX spring layout (force-directed)
        pos = nx.spring_layout(self.G, iterations=iterations, seed=42)
        self.visualization_data['node_positions'] = pos
        
        # Update node colors based on current state
        self._update_node_colors()
        
        return pos
    
    def _update_node_colors(self):
        """Update node colors for visualization"""
        color_map = {
            'S': 'green',      # Susceptible
            'E': 'orange',     # Exposed
            'I': 'red',        # Infectious
            'Ia': 'pink',      # Asymptomatic
            'Im': 'red',       # Mild
            'Is': 'darkred',   # Severe
            'Ih': 'purple',    # Hospitalized
            'Ic': 'black',     # Critical
            'R': 'blue',       # Recovered
            'D': 'gray',       # Deceased
            'V': 'cyan'        # Vaccinated
        }
        
        self.visualization_data['node_colors'] = []
        for node in self.G.nodes():
            state = self.G.nodes[node]['state']
            self.visualization_data['node_colors'].append(color_map.get(state, 'gray'))
    
    def save_simulation(self, filename):
        """Save simulation state to file"""
        data = {
            'G': self.G,
            'disease': self.disease,
            'time': self.time,
            'history': self.history,
            'stats': self.stats,
            'state_sets': self.state_sets,
            'infectious_subsets': self.infectious_subsets,
            'interventions': self.interventions
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Simulation saved to {filename}")
    
    @classmethod
    def load_simulation(cls, filename):
        """Load simulation from file"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        # Create new simulator
        simulator = cls(data['G'], data['disease'], data.get('interventions', {}))
        
        # Restore state
        simulator.time = data['time']
        simulator.history = data['history']
        simulator.stats = data['stats']
        simulator.state_sets = data['state_sets']
        simulator.infectious_subsets = data['infectious_subsets']
        
        print(f"📂 Simulation loaded from {filename}")
        return simulator
    
    # ==================== MAIN SIMULATION FUNCTION ====================

def run_complete_simulation(
    population=1000,
    network_type='hybrid',
    disease_variant='omicron',
    intervention_scenario='delayed_response',
    days=120,
    seed_method='random',
    n_seed_infections=10,
    output_file=None
):
    """
    Run a complete simulation with all components
    
    Returns: (simulator, history, stats)
    """
    print("=" * 60)
    print("🚀 ULTIMATE PANDEMIC SIMULATION")
    print("=" * 60)
    
    # 1. Generate network
    print("\n1️⃣  Generating network...")
    from network_generator import UltimateNetworkGenerator
    generator = UltimateNetworkGenerator(population=population)
    
    if network_type == 'erdos_renyi':
        G = generator.erdos_renyi(p=0.01)
    elif network_type == 'watts_strogatz':
        G = generator.watts_strogatz(k=8, p=0.3)
    elif network_type == 'barabasi_albert':
        G = generator.barabasi_albert(m=3)
    elif network_type == 'stochastic_block':
        G = generator.stochastic_block()
    else:  # hybrid (default)
        G = generator.hybrid_multilayer()
    
    print(f"   Network: {network_type}, Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    # 2. Select disease
    print("\n2️⃣  Selecting disease...")
    from disease_models import DiseaseLibrary
    disease = DiseaseLibrary.covid19_variant(disease_variant)
    print(f"   Disease: {disease.name}, R0={disease.R0}")
    
    # 3. Create simulator
    print("\n3️⃣  Initializing simulator...")
    simulator = UltimateSimulator(G, disease)
    
    # 4. Seed infections
    print("\n4️⃣  Seeding initial infections...")
    simulator.seed_infections(n_seed_infections, method=seed_method)
    
    # 5. Set up interventions
    print("\n5️⃣  Setting up interventions...")
    from disease_models import InterventionSchedule
    interv_schedule = InterventionSchedule()
    interv_schedule.create_preset_scenario(intervention_scenario)
    
    # Apply initial interventions
    for interv in interv_schedule.get_interventions_for_day(0):
        simulator.apply_intervention(interv['type'], **interv['params'])
    
    # 6. Run simulation
    print(f"\n6️⃣  Running simulation for {days} days...")
    print("-" * 40)
    
    history = simulator.run(days=days, show_progress=True)
    
    # 7. Get results
    print("\n7️⃣  Simulation complete! Generating results...")
    stats = simulator.get_summary_stats()
    
    print("\n" + "=" * 60)
    print("📊 SIMULATION RESULTS")
    print("=" * 60)
    
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key:25}: {value:.4f}")
        else:
            print(f"{key:25}: {value}")
    
    # 8. Save if requested
    if output_file:
        simulator.save_simulation(output_file)
        print(f"\n💾 Results saved to {output_file}")
    
    print("\n✅ Simulation pipeline complete!")
    return simulator, history, stats

# ==================== QUICK TEST ====================

if __name__ == "__main__":
    # Run a quick test simulation
    print("🧪 Running test simulation...")
    
    simulator, history, stats = run_complete_simulation(
        population=500,  # Smaller for quick test
        network_type='hybrid',
        disease_variant='omicron',
        intervention_scenario='delayed_response',
        days=60,
        seed_method='random',
        n_seed_infections=5,
        output_file=None
    )
    
    # Enhanced visualization of results
    import matplotlib.pyplot as plt
    import numpy as np

    # Create figure with 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # ========== PLOT 1: Disease Dynamics ==========
    axes[0, 0].fill_between(history['time'], history['S'], color='lightgreen', alpha=0.4, label='Susceptible')
    axes[0, 0].fill_between(history['time'], history['I'], color='lightcoral', alpha=0.4, label='Infectious')
    axes[0, 0].fill_between(history['time'], history['R'], color='lightblue', alpha=0.4, label='Recovered')

    # Add line plots on top for clarity
    axes[0, 0].plot(history['time'], history['S'], 'g-', linewidth=1.5, alpha=0.8)
    axes[0, 0].plot(history['time'], history['I'], 'r-', linewidth=1.5, alpha=0.8)
    axes[0, 0].plot(history['time'], history['R'], 'b-', linewidth=1.5, alpha=0.8)

    if 'D' in history and any(history['D']):
        axes[0, 0].plot(history['time'], history['D'], 'k--', linewidth=1.5, label='Deceased', alpha=0.8)

    axes[0, 0].set_xlabel('Days', fontsize=11)
    axes[0, 0].set_ylabel('Individuals', fontsize=11)
    axes[0, 0].set_title('Disease Dynamics Over Time', fontsize=13, fontweight='bold')
    axes[0, 0].legend(loc='upper right', fontsize=9)
    axes[0, 0].grid(True, alpha=0.2)
    axes[0, 0].set_ylim(bottom=0)

    # ========== PLOT 2: Epidemic Curve ==========
    # Calculate 7-day moving average for smoother curve
    window_size = 7
    if len(history['new_infections']) >= window_size:
        moving_avg = np.convolve(history['new_infections'], np.ones(window_size)/window_size, mode='valid')
        time_avg = history['time'][window_size-1:]
        axes[0, 1].plot(time_avg, moving_avg, 'darkred', linewidth=2.5, label=f'{window_size}-day avg', zorder=3)

    # Bar plot of daily cases
    bars = axes[0, 1].bar(history['time'], history['new_infections'], 
                          color='orangered', alpha=0.6, edgecolor='red', linewidth=0.5, label='Daily cases')

    # Highlight peak infection day
    peak_day = stats.get('peak_day', 0)
    if peak_day < len(history['new_infections']):
        axes[0, 1].axvline(x=peak_day, color='red', linestyle='--', alpha=0.5, label=f'Peak (Day {peak_day})')

    axes[0, 1].set_xlabel('Days', fontsize=11)
    axes[0, 1].set_ylabel('New Infections', fontsize=11)
    axes[0, 1].set_title('Epidemic Curve', fontsize=13, fontweight='bold')
    axes[0, 1].legend(loc='upper right', fontsize=9)
    axes[0, 1].grid(True, alpha=0.2)
    axes[0, 1].set_ylim(bottom=0)

    # ========== PLOT 3: Healthcare Burden ==========
    # Stacked area plot for healthcare burden
    if 'Ia' in history and 'Im' in history and 'Is' in history:
        axes[1, 0].stackplot(history['time'], 
                            history['Ia'], history['Im'], history['Is'], history.get('Ih', [0]*len(history['time'])),
                            colors=['lightpink', 'lightyellow', 'lightsalmon', 'mediumorchid'],
                            alpha=0.7,
                            labels=['Asymptomatic', 'Mild', 'Severe', 'Hospitalized'])
    else:
        # Fallback to line plots
        axes[1, 0].plot(history['time'], history.get('Ih', [0]*len(history['time'])), 
                        color='purple', linestyle='-', linewidth=2, label='Hospitalized')
        axes[1, 0].plot(history['time'], history.get('Ic', [0]*len(history['time'])), 
                        color='black', linestyle='-', linewidth=2, label='Critical')

    # Add ICU capacity line (example: 10% of population)
    icu_capacity = int(stats.get('initial_population', 500) * 0.1)
    axes[1, 0].axhline(y=icu_capacity, color='red', linestyle='--', alpha=0.5, label=f'ICU Capacity ({icu_capacity})')

    axes[1, 0].set_xlabel('Days', fontsize=11)
    axes[1, 0].set_ylabel('Patients', fontsize=11)
    axes[1, 0].set_title('Healthcare System Burden', fontsize=13, fontweight='bold')
    axes[1, 0].legend(loc='upper right', fontsize=9)
    axes[1, 0].grid(True, alpha=0.2)
    axes[1, 0].set_ylim(bottom=0)

    # ========== PLOT 4: Key Metrics ==========
    axes[1, 1].axis('off')  # Turn off axis for text display

    # Create summary statistics box
    summary_text = (
        f"🧬 {stats.get('initial_population', 'N/A')} Population | {stats.get('total_days', 'N/A')} Days\n"
        f"📊 Attack Rate: {stats.get('attack_rate', 0)*100:.1f}%\n"
        f"📈 Peak Infections: {stats.get('peak_infections', 0)} (Day {stats.get('peak_day', 0)})\n"
        f"⚰️  Total Deaths: {stats.get('total_deaths', 0)}\n"
        f"📉 Case Fatality Rate: {stats.get('case_fatality_rate', 0)*100:.2f}%\n"
        f"💉 Total Vaccinated: {stats.get('total_vaccinated', 0)}\n"
        f"🔄 Final R-effective: {stats.get('final_r_effective', 0):.2f}\n"
        f"🏥 Total Hospitalized: {stats.get('total_hospitalized', 0)}\n"
        f"✅ Final Susceptible: {stats.get('final_susceptible', 0)}\n"
        f"🩺 Total Recovered: {stats.get('total_recovered', 0)}"
    )

    # Add text box with metrics
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8, edgecolor='navy')
    axes[1, 1].text(0.05, 0.95, '📋 SIMULATION SUMMARY', 
                    transform=axes[1, 1].transAxes, fontsize=14, 
                    fontweight='bold', verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='navy', alpha=0.9, edgecolor='white'))

    axes[1, 1].text(0.05, 0.75, summary_text, transform=axes[1, 1].transAxes,
                    fontsize=11, verticalalignment='top',
                    bbox=props, linespacing=1.5)

    # Add small plot for R-effective if available
    if 'r_effective' in stats and stats['r_effective']:
        inset_ax = axes[1, 1].inset_axes([0.6, 0.1, 0.35, 0.3])
        inset_ax.plot(range(len(stats['r_effective'])), stats['r_effective'], 'b-', linewidth=1.5)
        inset_ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        inset_ax.set_xlabel('Days', fontsize=8)
        inset_ax.set_ylabel('R-eff', fontsize=8)
        inset_ax.set_title('Reproduction Number', fontsize=9)
        inset_ax.grid(True, alpha=0.2)
        inset_ax.tick_params(labelsize=7)

    # Add overall title
    plt.suptitle('Pandemic Simulation Results', fontsize=16, fontweight='bold', y=0.98)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    plt.savefig('simulation_results.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.savefig('simulation_results.pdf', dpi=300, bbox_inches='tight', facecolor='white')

    print("\n" + "="*60)
    print("📊 VISUALIZATION COMPLETE")
    print("="*60)
    print(f"✅ Plot saved as 'simulation_results.png' (high-quality)")
    print(f"✅ Plot saved as 'simulation_results.pdf' (vector format)")
    print(f"✅ Key metrics displayed in summary box")
    print(f"✅ Healthcare burden visualization with capacity limits")
    print("="*60)

    plt.show()