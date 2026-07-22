# simulator_engine.py - SEIRD network epidemic simulator
import heapq
import itertools
import logging
import pickle
import random
from collections import defaultdict

import networkx as nx
import numpy as np

from disease_models import DiseaseProgression, TransmissionCalculator

logger = logging.getLogger(__name__)

# States that a node's `state` attribute may hold. Severity (asymptomatic ..
# critical) is tracked separately in `infectious_subsets` so that the node
# state always stays within this set - the frontend colour maps depend on it.
NODE_STATES = ('S', 'E', 'I', 'R', 'D', 'V')


class UltimateSimulator:
    """
    Network epidemic simulator: SEIRD compartments with age stratification,
    five infectious severity levels and reversible interventions.

    Time complexity: O(I x k) per day, where I is the number of infectious
    nodes and k the average degree.
    """

    def __init__(self, G, disease_params, interventions=None):
        """
        Args:
            G: NetworkX graph (from network_generator)
            disease_params: DiseaseParameters object
            interventions: dict of initially active interventions
        """
        self.G = G.copy()  # Work on a copy
        self.disease = disease_params
        self.interventions = dict(interventions or {})
        self.scheduled_interventions = []

        self.time = 0  # Current day
        self.running = False

        self._initialize_tracking()

        self.history = defaultdict(list)

        # Event queue is a min-heap of (scheduled_day, sequence, event). The
        # sequence counter keeps ordering stable and stops heapq from ever
        # comparing two event dicts.
        self.event_queue = []
        self._event_counter = itertools.count()

        self.stats = {
            'total_infected': 0,
            'total_recovered': 0,
            'total_deaths': 0,
            'total_vaccinated': 0,
            'peak_infections': 0,
            'peak_day': 0,
            'total_hospitalized': 0,
            'hospital_bed_usage': [],  # One entry per simulated day
            'r_effective': []          # One entry per simulated day
        }

        # Counters reset at the start of every simulated day
        self.new_infections_today = 0
        self.new_hospitalizations_today = 0
        self.previous_total_deaths = 0

        self._cache_neighbors = {}

        # Node state snapshots for the 3D network view, as (day, states) pairs
        # where states is one character per node in graph order. Recording only
        # every `frame_interval` days, and as a string rather than a list of
        # per-node strings, keeps a long run over a large population from
        # holding tens of megabytes of frames it will never ship.
        self.state_frames = []
        self.frame_interval = 1

        self.visualization_data = {
            'node_positions': None,
            'node_colors': [],
            'infection_paths': []
        }

    def _initialize_tracking(self):
        """Initialise the data structures used for fast state lookups."""
        self.state_sets = {state: set() for state in NODE_STATES}
        self.state_sets['S'] = set(self.G.nodes())

        # Infectious severity subsets (a node in exactly one of these is also
        # a member of state_sets['I'])
        self.infectious_subsets = {
            'Ia': set(),  # Asymptomatic
            'Im': set(),  # Mild
            'Is': set(),  # Severe
            'Ih': set(),  # Hospitalized
            'Ic': set()   # Critical
        }

        self.infection_tree = {}
        self._degree_cache = {node: self.G.degree(node) for node in self.G.nodes()}

        logger.info(
            "Simulator initialised with %d nodes and %d edges",
            self.G.number_of_nodes(), self.G.number_of_edges()
        )

    def _set_state(self, node, state):
        """Move a node into `state`, removing it from every other state set.

        Going through this helper is what keeps the compartments a partition of
        the population - a node can never be counted in two compartments.
        """
        for state_set in self.state_sets.values():
            state_set.discard(node)
        self.state_sets[state].add(node)
        self.G.nodes[node]['state'] = state
        self.G.nodes[node]['days_in_state'] = 0

    def _clear_severity(self, node):
        for subset in self.infectious_subsets.values():
            subset.discard(node)

    # ==================== INFECTION METHODS ====================

    def seed_infections(self, n_infections=10, method='random', **kwargs):
        """
        Seed initial infections.

        Methods: 'random', 'hubs', 'mobile', 'geographic', 'age_targeted'.
        """
        candidates = list(self.state_sets['S'])
        if not candidates:
            return []
        n_infections = max(0, min(int(n_infections), len(candidates)))

        if method == 'hubs':
            candidates.sort(key=lambda n: self._degree_cache[n], reverse=True)
            infected_nodes = candidates[:n_infections]

        elif method == 'mobile':
            candidates.sort(key=lambda n: self.G.nodes[n].get('mobility', 0.5), reverse=True)
            infected_nodes = candidates[:n_infections]

        elif method == 'geographic':
            # Cluster the seeds around one randomly chosen node, using the
            # layout coordinates the network generator attaches to each node.
            center = random.choice(candidates)
            cx = self.G.nodes[center].get('x', 0.0)
            cy = self.G.nodes[center].get('y', 0.0)
            candidates.sort(
                key=lambda n: (self.G.nodes[n].get('x', 0.0) - cx) ** 2
                + (self.G.nodes[n].get('y', 0.0) - cy) ** 2
            )
            infected_nodes = candidates[:n_infections]

        elif method == 'age_targeted':
            lo, hi = kwargs.get('target_age', (20, 40))
            age_nodes = [n for n in candidates if lo <= self.G.nodes[n]['age'] <= hi]
            pool = age_nodes or candidates
            infected_nodes = random.sample(pool, min(n_infections, len(pool)))

        else:  # 'random' and any unknown method
            infected_nodes = random.sample(candidates, n_infections)

        for node in infected_nodes:
            self._infect_node(node, source='seed')

        logger.info("Seeded %d initial infections using '%s'", len(infected_nodes), method)
        return infected_nodes

    def _infect_node(self, node, source='unknown'):
        """Move a susceptible node into E and schedule its whole disease course."""
        self.G.nodes[node]['infected_by'] = source
        self.G.nodes[node]['infection_time'] = self.time
        self._set_state(node, 'E')

        age = self.G.nodes[node]['age']
        vaccinated = self.G.nodes[node].get('vaccinated', False)

        progression = DiseaseProgression.determine_initial_course(age, self.disease, vaccinated)

        self.G.nodes[node]['symptoms'] = progression['symptoms']
        self.G.nodes[node]['incubation_days'] = progression['incubation_days']
        self.G.nodes[node]['infectious_days'] = progression['infectious_days']
        self.G.nodes[node]['will_hospitalize'] = progression['will_hospitalize']
        self.G.nodes[node]['will_die'] = progression['will_die']

        # 1. Become infectious after incubation
        self._schedule_event(node, 'become_infectious', progression['incubation_days'])

        # 2. Hospitalisation, if this course leads there
        if progression['will_hospitalize'] and progression['hospital_day']:
            self._schedule_event(node, 'hospitalize', progression['hospital_day'])

        # 3. Exactly one terminal event: death or recovery, never both.
        if progression['will_die']:
            self._schedule_event(node, 'die', progression['death_day'])
        else:
            self._schedule_event(node, 'recover', progression['recovery_day'])

        if source != 'seed':
            self.infection_tree.setdefault(source, []).append(node)

        self.stats['total_infected'] += 1
        self.new_infections_today += 1

        self.visualization_data['infection_paths'].append({
            'from': None if source == 'seed' else source,
            'to': node,
            'time': self.time
        })

    # ==================== TRANSMISSION STEP ====================

    def _transmission_step(self):
        """Run one day of transmission and return the number of new infections."""
        all_infectious = set()
        for subset in self.infectious_subsets.values():
            all_infectious.update(subset)

        if not all_infectious:
            return 0

        new_infections = 0
        intervention_cache = self._cache_intervention_factors()

        for infector in all_infectious:
            # Hospitalised patients are isolated by definition; nodes flagged
            # `isolated` were detected by testing or are self-isolating.
            if self.G.nodes[infector].get('isolated', False):
                continue

            if infector not in self._cache_neighbors:
                self._cache_neighbors[infector] = list(self.G.neighbors(infector))

            for contact in self._cache_neighbors[infector]:
                if self.G.nodes[contact]['state'] != 'S':
                    continue

                edge_data = self.G.edges[infector, contact]
                if not edge_data.get('active', True):
                    continue

                transmission_prob = TransmissionCalculator.calculate_transmission_probability(
                    infector=infector,
                    susceptible=contact,
                    G=self.G,
                    disease=self.disease,
                    interventions=intervention_cache,
                    current_day=self.time
                )

                if random.random() < transmission_prob:
                    self._infect_node(contact, source=infector)
                    new_infections += 1

        return new_infections

    def _cache_intervention_factors(self):
        """Snapshot the intervention state used for this day's transmission."""
        return dict(self.interventions)

    # ==================== INTERVENTION METHODS ====================

    def apply_intervention(self, intervention_type, **params):
        """Dispatch to the handler for `intervention_type`."""
        handlers = {
            'lockdown': self._apply_lockdown,
            'social_distancing': self._apply_social_distancing,
            'mask_mandate': self._apply_mask_mandate,
            'vaccination': self._apply_vaccination,
            'testing': self._apply_testing,
            'isolation': self._apply_isolation,
            'travel_restrictions': self._apply_travel_restrictions,
            'school_closure': self._apply_school_closure,
            'border_control': self._apply_travel_restrictions,
            'hygiene': self._apply_hygiene,
            'ventilation': self._apply_ventilation,
            'reopen': self._apply_reopen,
        }
        handler = handlers.get(intervention_type)
        if handler is None:
            logger.warning("Unknown intervention: %s", intervention_type)
            return
        try:
            handler(**params)
        except TypeError as exc:
            logger.warning("Bad parameters for intervention '%s': %s", intervention_type, exc)

    def _apply_lockdown(self, strictness=0.7, compliance=0.8, duration=None):
        """Reduce mobility for complying individuals.

        The pre-lockdown mobility of every affected node is stored so that
        `_apply_reopen` and the scheduled end-of-lockdown event can restore it
        exactly. Lockdown deliberately does not set `isolated` - that flag is
        reserved for detected cases, and setting it here used to silence
        transmission for the whole population.
        """
        strictness = float(np.clip(strictness, 0.0, 1.0))
        compliance = float(np.clip(compliance, 0.0, 1.0))

        self.interventions['lockdown'] = True
        self.interventions['lockdown_strictness'] = strictness
        self.interventions['lockdown_compliance'] = compliance

        for node in self.G.nodes():
            if random.random() < compliance:
                attrs = self.G.nodes[node]
                if 'mobility_prelockdown' not in attrs:
                    attrs['mobility_prelockdown'] = attrs.get('mobility', 0.5)
                attrs['mobility'] = attrs['mobility_prelockdown'] * (1 - strictness)

        logger.info("Lockdown: strictness=%s compliance=%s duration=%s",
                    strictness, compliance, duration)

        if duration:
            self._schedule_event(None, 'end_lockdown', duration)

    def _restore_mobility(self):
        """Undo the mobility reduction applied by a lockdown."""
        for node in self.G.nodes():
            attrs = self.G.nodes[node]
            if 'mobility_prelockdown' in attrs:
                attrs['mobility'] = attrs.pop('mobility_prelockdown')

    def _apply_social_distancing(self, reduction=0.3, compliance=0.7):
        self.interventions['social_distancing'] = True
        self.interventions['distancing_reduction'] = float(np.clip(reduction, 0.0, 1.0))
        self.interventions['distancing_compliance'] = float(np.clip(compliance, 0.0, 1.0))
        logger.info("Social distancing: reduction=%s compliance=%s", reduction, compliance)

    def _apply_school_closure(self, reduction=0.8, compliance=0.9):
        """Deactivate a fraction of school edges."""
        reduction = float(np.clip(reduction, 0.0, 1.0)) * float(np.clip(compliance, 0.0, 1.0))
        self.interventions['school_closure'] = True

        closed = 0
        for u, v, data in self.G.edges(data=True):
            if 'school' in str(data.get('type', '')) and random.random() < reduction:
                data['active'] = False
                closed += 1
        logger.info("School closure: deactivated %d school contacts", closed)

    def _apply_mask_mandate(self, efficacy=0.5, compliance=0.7):
        efficacy = float(np.clip(efficacy, 0.0, 1.0))
        compliance = float(np.clip(compliance, 0.0, 1.0))

        self.interventions['mask_mandate'] = True
        self.interventions['mask_efficacy'] = efficacy
        self.interventions['mask_compliance'] = compliance

        for node in self.G.nodes():
            self.G.nodes[node]['wears_mask'] = random.random() < compliance

        logger.info("Mask mandate: efficacy=%s compliance=%s", efficacy, compliance)

    def _apply_vaccination(self, rate=0.01, efficacy=0.9, priority='age', daily_capacity=None):
        """Start (or update) a rolling vaccination campaign.

        Only the campaign parameters are recorded here; doses are administered
        once per simulated day by `_vaccinate_daily`, so `rate` behaves as the
        documented "daily fraction of susceptibles" rather than a single
        one-off batch.
        """
        self.interventions['vaccination'] = True
        self.interventions['vaccination_rate'] = float(np.clip(rate, 0.0, 1.0))
        self.interventions['vaccine_efficacy'] = float(np.clip(efficacy, 0.0, 1.0))
        self.interventions['vaccine_priority'] = priority
        self.interventions['vaccine_daily_capacity'] = daily_capacity

        logger.info("Vaccination campaign: rate=%s/day efficacy=%s priority=%s",
                    rate, efficacy, priority)

    def _vaccinate_daily(self):
        """Administer one day's worth of vaccine doses."""
        if not self.interventions.get('vaccination'):
            return

        rate = self.interventions.get('vaccination_rate', 0.0)
        efficacy = self.interventions.get('vaccine_efficacy', 0.9)
        priority = self.interventions.get('vaccine_priority', 'age')
        daily_capacity = self.interventions.get('vaccine_daily_capacity')

        susceptible = self.state_sets['S']
        if not susceptible or rate <= 0:
            return

        n_doses = int(round(rate * len(susceptible)))
        if daily_capacity:
            n_doses = min(n_doses, int(daily_capacity))
        if n_doses <= 0:
            return

        if priority in ('age', 'elderly'):
            candidates = sorted(susceptible, key=lambda n: self.G.nodes[n]['age'], reverse=True)
        elif priority == 'young':
            candidates = sorted(susceptible, key=lambda n: self.G.nodes[n]['age'])
        elif priority == 'frontline':
            candidates = sorted(susceptible,
                                key=lambda n: self.G.nodes[n].get('mobility', 0.5), reverse=True)
        elif priority == 'vulnerable':
            candidates = sorted(susceptible,
                                key=lambda n: self.G.nodes[n].get('health_risk', 0.5), reverse=True)
        else:  # 'random'
            candidates = random.sample(list(susceptible), len(susceptible))

        for node in candidates[:n_doses]:
            self.G.nodes[node]['vaccinated'] = True
            self.G.nodes[node]['vaccination_day'] = self.time
            # A dose always moves the node to V; `efficacy` determines how much
            # protection it confers, not whether it is administered.
            self.G.nodes[node]['immunity'] = efficacy
            self._set_state(node, 'V')
            self.stats['total_vaccinated'] += 1

    def _apply_testing(self, rate=0.05, accuracy=0.95, delay=2, isolation_compliance=0.8):
        """Start a testing regime; cases are detected daily by `_test_daily`."""
        self.interventions['testing'] = True
        self.interventions['testing_rate'] = float(np.clip(rate, 0.0, 1.0))
        self.interventions['testing_accuracy'] = float(np.clip(accuracy, 0.0, 1.0))
        self.interventions['testing_delay'] = max(0, int(delay))
        self.interventions['testing_isolation_compliance'] = float(np.clip(isolation_compliance, 0.0, 1.0))
        logger.info("Testing: rate=%s accuracy=%s delay=%sd", rate, accuracy, delay)

    def _test_daily(self):
        """Test a fraction of symptomatic cases and schedule isolation for positives."""
        if not self.interventions.get('testing'):
            return

        rate = self.interventions.get('testing_rate', 0.0)
        accuracy = self.interventions.get('testing_accuracy', 0.95)
        delay = self.interventions.get('testing_delay', 2)
        isolation_compliance = self.interventions.get('testing_isolation_compliance', 0.8)

        # Only symptomatic, not-yet-isolated cases present for testing
        testable = [
            n for n in (self.infectious_subsets['Im'] | self.infectious_subsets['Is']
                        | self.infectious_subsets['Ic'])
            if not self.G.nodes[n].get('isolated', False)
        ]
        if not testable or rate <= 0:
            return

        n_to_test = min(len(testable), int(round(rate * len(testable))))
        for node in random.sample(testable, n_to_test):
            if random.random() < accuracy and random.random() < isolation_compliance:
                self._schedule_event(node, 'isolate', delay)

    def _apply_isolation(self, compliance=0.8):
        """Isolate currently symptomatic individuals."""
        compliance = float(np.clip(compliance, 0.0, 1.0))
        self.interventions['isolation'] = True
        self.interventions['isolation_compliance'] = compliance

        symptomatic = (self.infectious_subsets['Im'] | self.infectious_subsets['Is']
                       | self.infectious_subsets['Ic'])
        isolated = 0
        for node in symptomatic:
            if random.random() < compliance:
                self.G.nodes[node]['isolated'] = True
                isolated += 1

        logger.info("Isolation: compliance=%s, isolated %d individuals", compliance, isolated)

    def _apply_travel_restrictions(self, reduction=0.5, compliance=1.0):
        """Deactivate a fraction of long-distance ('random') contacts."""
        reduction = float(np.clip(reduction, 0.0, 1.0)) * float(np.clip(compliance, 0.0, 1.0))
        self.interventions['travel_restrictions'] = True
        self.interventions['travel_reduction'] = reduction

        for u, v, data in self.G.edges(data=True):
            if 'random' in str(data.get('type', '')) and random.random() < reduction:
                data['active'] = False

        logger.info("Travel restrictions: reduction=%s", reduction)

    def _apply_hygiene(self, improvement=0.3):
        self.interventions['hygiene'] = True
        self.interventions['hygiene_improvement'] = float(np.clip(improvement, 0.0, 1.0))

    def _apply_ventilation(self, improvement=0.4):
        self.interventions['improved_ventilation'] = True
        self.interventions['ventilation_improvement'] = float(np.clip(improvement, 0.0, 1.0))

    def _apply_reopen(self, gradual=True):
        """Lift lockdown, travel restrictions and school closures."""
        for key in ('lockdown', 'lockdown_strictness', 'lockdown_compliance',
                    'travel_restrictions', 'travel_reduction', 'school_closure',
                    'social_distancing', 'distancing_reduction', 'distancing_compliance'):
            self.interventions.pop(key, None)

        self._restore_mobility()

        if gradual:
            # Ease back rather than snapping to full pre-pandemic mixing
            for node in self.G.nodes():
                attrs = self.G.nodes[node]
                attrs['mobility'] = min(0.95, attrs.get('mobility', 0.5) * 1.2)

        # Reopened contacts become active again
        for _, _, data in self.G.edges(data=True):
            data['active'] = True

        logger.info("Reopening society (gradual=%s)", gradual)

    # ==================== EVENT PROCESSING ====================

    def _schedule_event(self, node, action, days_from_now):
        """Schedule `action` for `node` to fire `days_from_now` days from today."""
        if days_from_now is None:
            return
        days_from_now = max(0, int(days_from_now))
        event_time = self.time + days_from_now
        heapq.heappush(
            self.event_queue,
            (event_time, next(self._event_counter), {'node': node, 'action': action})
        )

    def _process_events(self):
        """Fire every event due today or earlier.

        The `<=` comparison matters: an event scheduled for a day that has
        already passed (which can happen for zero-delay follow-ups) would
        otherwise sit at the head of the queue forever and block every event
        behind it.
        """
        processed = 0
        while self.event_queue and self.event_queue[0][0] <= self.time:
            _, _, event = heapq.heappop(self.event_queue)
            self._execute_event(event)
            processed += 1
        return processed

    def _execute_event(self, event):
        node = event['node']
        action = event['action']

        if action == 'end_lockdown':
            self.interventions.pop('lockdown', None)
            self.interventions.pop('lockdown_strictness', None)
            self.interventions.pop('lockdown_compliance', None)
            self._restore_mobility()
            logger.info("Lockdown ended on day %d", self.time)
            return

        if node is None:
            return

        state = self.G.nodes[node].get('state')

        # Dead nodes are terminal - a stale event must never resurrect them.
        if state == 'D':
            return

        if action == 'become_infectious':
            if state != 'E':
                return
            self._set_state(node, 'I')
            symptoms = self.G.nodes[node].get('symptoms', 'mild')
            subset = {'asymptomatic': 'Ia', 'mild': 'Im',
                      'severe': 'Is', 'critical': 'Ic'}.get(symptoms, 'Im')
            self._clear_severity(node)
            self.infectious_subsets[subset].add(node)

        elif action == 'hospitalize':
            if state not in ('E', 'I'):
                return
            # A patient may be hospitalised straight out of incubation
            self._set_state(node, 'I')
            self.G.nodes[node]['hospitalized'] = True
            # Hospitalised patients no longer mix with their contacts
            self.G.nodes[node]['isolated'] = True
            self._clear_severity(node)
            self.infectious_subsets['Ih'].add(node)
            self.stats['total_hospitalized'] += 1
            self.new_hospitalizations_today += 1

        elif action == 'recover':
            if state in ('R', 'V'):
                return
            self._clear_severity(node)
            self._set_state(node, 'R')
            self.G.nodes[node]['immunity'] = 0.85  # Natural immunity
            self.G.nodes[node]['isolated'] = False
            self.G.nodes[node]['hospitalized'] = False
            self.stats['total_recovered'] += 1

        elif action == 'die':
            self._clear_severity(node)
            self._set_state(node, 'D')
            self.G.nodes[node]['isolated'] = True
            self.stats['total_deaths'] += 1

        elif action == 'isolate':
            if state in ('E', 'I'):
                self.G.nodes[node]['isolated'] = True

    # ==================== SIMULATION LOOP ====================

    def step(self, days=1):
        """Advance the simulation by `days` days; returns new infections per day."""
        new_infections_list = []

        for _ in range(days):
            # The counters are cleared at the *end* of each day rather than
            # here, so infections seeded before the first step are attributed
            # to day 0 instead of being lost.

            # 1. Fire scheduled state transitions
            self._process_events()

            # 2. Start any interventions scheduled for today
            self._apply_scheduled_interventions()

            # 3. Daily intervention activity
            self._vaccinate_daily()
            self._test_daily()

            # 4. Transmission
            new_infections = self._transmission_step()
            new_infections_list.append(new_infections)

            # 5. Age every node's time-in-state and update waning immunity
            for node in self.G.nodes():
                self.G.nodes[node]['days_in_state'] = self.G.nodes[node].get('days_in_state', 0) + 1
                DiseaseProgression.update_immunity(node, self.G, self.disease, self.time)

            # 6. Record
            self._record_history()
            self._update_statistics()
            self._record_state_frame()

            self.new_infections_today = 0
            self.new_hospitalizations_today = 0
            self.time += 1

        return new_infections_list

    def run(self, days=100, show_progress=False):
        """Run the simulation for `days` days and return the history dict."""
        logger.info("Starting simulation for %d days", days)
        self.running = True

        for day in range(days):
            self.step(1)
            if show_progress and day % 10 == 0:
                logger.info("Day %d: %d infectious, %d deaths",
                            day, len(self.state_sets['I']), self.stats['total_deaths'])

        self.running = False
        logger.info(
            "Simulation complete: %d susceptible, %d infectious, %d recovered, %d deaths",
            len(self.state_sets['S']), len(self.state_sets['I']),
            len(self.state_sets['R']), len(self.state_sets['D'])
        )
        return self.history

    def _apply_scheduled_interventions(self):
        """Start every intervention whose scheduled day is today."""
        for entry in self.scheduled_interventions:
            if entry.get('day') == self.time:
                self.apply_intervention(entry['type'], **entry.get('params', {}))

    def _record_history(self):
        self.history['time'].append(self.time)

        for state in NODE_STATES:
            self.history[state].append(len(self.state_sets[state]))

        for inf_state in ('Ia', 'Im', 'Is', 'Ih', 'Ic'):
            self.history[inf_state].append(len(self.infectious_subsets[inf_state]))

        # Actual transmission events today, not a difference of compartment
        # sizes (which goes negative as people leave E).
        self.history['new_infections'].append(self.new_infections_today)

        daily_deaths = self.stats['total_deaths'] - self.previous_total_deaths
        self.history['daily_deaths'].append(daily_deaths)
        self.previous_total_deaths = self.stats['total_deaths']

        self.history['new_hospitalizations'].append(self.new_hospitalizations_today)
        self.history['daily_hospitalizations'].append(
            len(self.infectious_subsets['Ih']) + len(self.infectious_subsets['Ic'])
        )

    def _record_state_frame(self):
        """Store the per-node state for this day (used by the 3D network view)."""
        if self.time % self.frame_interval:
            return
        self.state_frames.append(
            (self.time, ''.join(self.G.nodes[n]['state'] for n in self.G.nodes()))
        )

    def _update_statistics(self):
        current_infectious = len(self.state_sets['I'])

        if current_infectious > self.stats['peak_infections']:
            self.stats['peak_infections'] = current_infectious
            self.stats['peak_day'] = self.time

        self.stats['r_effective'].append(self._estimate_r_effective())

        self.stats['hospital_bed_usage'].append(
            len(self.infectious_subsets['Ih']) + len(self.infectious_subsets['Ic'])
        )

    def _estimate_r_effective(self):
        """Estimate R_eff from the ratio of new cases one generation apart.

        Exactly one value is appended per simulated day so the series lines up
        with `history['time']` on the charts. Days without enough history yield
        0.0 rather than being skipped.
        """
        cases = self.history['new_infections']
        gen = max(1, int(round(self.disease.generation_time)))

        if len(cases) < 2 * gen:
            return 0.0

        recent = float(np.mean(cases[-gen:]))
        previous = float(np.mean(cases[-2 * gen:-gen]))
        if previous <= 0:
            return 0.0

        # Growth over one generation interval is R_eff by definition
        return round(recent / previous, 4)

    # ==================== ANALYSIS ====================

    def get_summary_stats(self):
        population = max(1, len(self.G))

        # The value on the final day, not the last non-zero one: filtering
        # zeros out reported a long-dead epidemic's old growth rate, so a
        # finished outbreak claimed it was still expanding.
        r_series = self.stats['r_effective']
        final_r = r_series[-1] if r_series else 0.0
        peak_r = max(r_series) if r_series else 0.0

        return {
            'total_days': self.time,
            'initial_population': len(self.G),
            'final_susceptible': len(self.state_sets['S']),
            'total_infected': self.stats['total_infected'],
            'total_recovered': self.stats['total_recovered'],
            'total_deaths': self.stats['total_deaths'],
            'total_vaccinated': self.stats['total_vaccinated'],
            'total_hospitalized': self.stats['total_hospitalized'],
            'peak_infections': self.stats['peak_infections'],
            'peak_day': self.stats['peak_day'],
            'attack_rate': self.stats['total_infected'] / population,
            'case_fatality_rate': self.stats['total_deaths'] / max(1, self.stats['total_infected']),
            'final_r_effective': final_r,
            'peak_r_effective': peak_r,
        }

    def get_infection_tree(self, max_depth=3):
        """Transmission tree rooted at the seed infections."""
        def build_tree(node, depth=0):
            if depth >= max_depth or node not in self.infection_tree:
                return []
            return [
                {
                    'id': child,
                    'age': self.G.nodes[child]['age'],
                    'infection_time': self.G.nodes[child].get('infection_time', 0),
                    'symptoms': self.G.nodes[child].get('symptoms', 'unknown'),
                    'children': build_tree(child, depth + 1)
                }
                for child in self.infection_tree[node]
            ]

        seeds = [n for n in self.G.nodes() if self.G.nodes[n].get('infected_by') == 'seed']
        return {seed: build_tree(seed) for seed in seeds[:5]}

    def get_network_metrics(self):
        """Network metrics relevant to disease spread."""
        degrees = [d for _, d in self.G.degree()]
        connected = nx.is_connected(self.G) if len(self.G) else False

        metrics = {
            'avg_degree': float(np.mean(degrees)) if degrees else 0.0,
            'avg_clustering': nx.average_clustering(self.G),
            'diameter': nx.diameter(self.G) if connected else None,
            'avg_path_length': nx.average_shortest_path_length(self.G) if connected else None,
        }

        try:
            metrics['degree_assortativity'] = nx.degree_assortativity_coefficient(self.G)
        except (ZeroDivisionError, ValueError):
            metrics['degree_assortativity'] = None

        n_superspreaders = max(1, int(0.05 * len(self.G)))
        top = sorted(degrees, reverse=True)[:n_superspreaders]
        metrics['superspreader_count'] = n_superspreaders
        metrics['superspreader_avg_degree'] = float(np.mean(top)) if top else 0.0

        return metrics

    # ==================== VISUALIZATION ====================

    def compute_force_directed_layout(self, iterations=50, dim=2):
        """Compute a force-directed layout for visualisation."""
        pos = nx.spring_layout(self.G, iterations=iterations, dim=dim, seed=42)
        self.visualization_data['node_positions'] = pos
        return pos

    def save_simulation(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump({
                'G': self.G,
                'disease': self.disease,
                'time': self.time,
                'history': dict(self.history),
                'stats': self.stats,
                'state_sets': self.state_sets,
                'infectious_subsets': self.infectious_subsets,
                'interventions': self.interventions
            }, f)
        logger.info("Simulation saved to %s", filename)

    @classmethod
    def load_simulation(cls, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)

        simulator = cls(data['G'], data['disease'], data.get('interventions', {}))
        simulator.time = data['time']
        simulator.history = defaultdict(list, data['history'])
        simulator.stats = data['stats']
        simulator.state_sets = data['state_sets']
        simulator.infectious_subsets = data['infectious_subsets']
        return simulator
