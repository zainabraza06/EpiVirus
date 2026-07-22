# network_generator.py
import logging
import random

import networkx as nx
import numpy as np
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class UltimateNetworkGenerator:
   
    
    def __init__(self, population=2000, dataset_csv: Optional[str] = None):
       
        self.population = population
        self.dataset_csv = dataset_csv
        self.real_data = None
        if self.dataset_csv:
            self.load_dataset(self.dataset_csv)
    
    # LOAD REAL DATA
    def load_dataset(self, csv_path: str):
        """Load Kaggle dataset for nodes and edges"""
        import pandas as pd  # optional dependency, only needed for CSV-backed networks
        self.real_data = pd.read_csv(csv_path)
        logger.info(f" Loaded dataset with {len(self.real_data)} rows")
    
    # BASE NETWORK MODELS
    def erdos_renyi(self, p=0.01):
        """Random connections model"""
        G = nx.erdos_renyi_graph(n=self.population, p=p)
        self._add_attributes(G)
        self._add_edge_attributes(G)
        return G
    
    def watts_strogatz(self, k=8, p=0.3):
        """Small-world network"""
        G = nx.watts_strogatz_graph(n=self.population, k=k, p=p)
        self._add_attributes(G)
        self._add_edge_attributes(G)
        return G
    
    def barabasi_albert(self, m=3):
        """Scale-free network (preferential attachment)"""
        G = nx.barabasi_albert_graph(n=self.population, m=m)
        self._add_attributes(G)
        self._add_edge_attributes(G)
        return G
    
    def stochastic_block(self, community_sizes=None, intra_prob=0.15, inter_prob=0.01,
                         n_blocks=4):
        """Community-structured network"""
        if community_sizes is None:
            n_blocks = max(2, min(int(n_blocks), max(2, self.population // 10)))
            community_sizes = [self.population // n_blocks] * n_blocks
            community_sizes[-1] = self.population - sum(community_sizes[:-1])

        # Create probability matrix
        n_communities = len(community_sizes)
        prob_matrix = [[intra_prob if i==j else inter_prob for j in range(n_communities)] 
                      for i in range(n_communities)]
        
        G = nx.stochastic_block_model(community_sizes, prob_matrix)
        self._add_attributes(G)
        self._add_edge_attributes(G)
        return G
    
    #  HYBRID NETWORK
    def hybrid_multilayer(self, school_p=0.8, workplace_p=0.6, community_p=0.4):
        """
        Combine multiple network layers for realistic social structure
        """
        logger.info(" Building hybrid multilayer network...")
        
        # 1. Start with small-world base network
        G = nx.watts_strogatz_graph(n=self.population, k=6, p=0.2)
        logger.info(f"   Base network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # 2. Add attributes FIRST 
        self._add_attributes(G)
        
        # 3. Create household layer
        self._add_households(G)
        
        # 4. Create workplace layer (based on age and occupation)
        self._add_workplaces(G, workplace_p)
        
        # 5. Create school layer (based on age)
        self._add_schools(G, school_p)
        
        # 6. Add hub nodes (super-spreaders)
        self._add_hubs(G)
        
        # 7. Add random connections (long-distance travel)
        self._add_random_connections(G, community_p)
        
        # 8. Add edge attributes
        self._add_edge_attributes(G)
        
        logger.info(f"   Final network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        logger.info("   Layers: Households, Workplaces, Schools, Hubs, Random")
        return G
    
    def _add_households(self, G):
        """Assign every person to exactly one household and connect its members.

        Adults and children are drawn from pre-partitioned pools, so households
        are disjoint and the whole pass is linear in the population. Building
        the candidate lists inside the loop instead made this O(N^2) and let the
        same person belong to arbitrarily many households.
        """
        logger.info("Adding households...")

        adults = [n for n in G.nodes() if 20 <= G.nodes[n]['age'] <= 65]
        children = [n for n in G.nodes() if G.nodes[n]['age'] < 20]
        others = [n for n in G.nodes() if G.nodes[n]['age'] > 65]

        random.shuffle(adults)
        random.shuffle(children)
        random.shuffle(others)

        household_id = 0
        while adults or children or others:
            size = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.25, 0.35, 0.2, 0.1])[0]
            members = []

            # Up to two adults per household, then children, then anyone left
            for _ in range(min(2, size)):
                if adults:
                    members.append(adults.pop())
            while len(members) < size and children:
                members.append(children.pop())
            while len(members) < size and others:
                members.append(others.pop())
            while len(members) < size and adults:
                members.append(adults.pop())

            if not members:
                break

            for node in members:
                G.nodes[node]['household'] = household_id

            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    u, v = members[i], members[j]
                    if G.has_edge(u, v):
                        G[u][v]['weight'] = max(3.0, G[u][v].get('weight', 1.0))
                        G[u][v]['type'] = 'household'
                    else:
                        G.add_edge(u, v, weight=3.0, type='household', active=True)

            household_id += 1

        logger.info("Created %d households", household_id)
    
    def _add_workplaces(self, G, connection_prob=0.6):
        """Add workplace connections"""
        logger.info("   Adding workplaces...")
        
        # Identify workers (age 20-65, not students)
        workers = []
        for node in G.nodes():
            age = G.nodes[node]['age']
            occupation = G.nodes[node]['occupation']
            if 20 <= age <= 65 and occupation in ['worker', 'essential']:
                workers.append(node)
        
        logger.info(f"   Found {len(workers)} workers")
        
        # Create workplaces
        n_workplaces = max(1, len(workers) // 30)  # Average 30 workers per workplace
        workplaces = []
        
        for i in range(n_workplaces):
            workplace_size = random.randint(10, 50)
            workplaces.append([])
        
        # Assign workers to workplaces
        for worker in workers:
            workplace_idx = random.randint(0, n_workplaces - 1)
            workplaces[workplace_idx].append(worker)
        
        # Add connections within workplaces
        for workplace in workplaces:
            for i in range(len(workplace)):
                for j in range(i + 1, len(workplace)):
                    if random.random() < connection_prob:
                        node_i, node_j = workplace[i], workplace[j]
                        if G.has_edge(node_i, node_j):
                            G[node_i][node_j]['weight'] = max(1.5, G[node_i][node_j].get('weight', 1.0))
                            if 'type' not in G[node_i][node_j]:
                                G[node_i][node_j]['type'] = 'workplace'
                            else:
                                # Edge can have multiple types
                                if G[node_i][node_j]['type'] != 'workplace':
                                    G[node_i][node_j]['type'] += ',workplace'
                        else:
                            G.add_edge(node_i, node_j, weight=1.5, type='workplace', active=True)
        
        logger.info(f"   Created {n_workplaces} workplaces")
    
    def _add_schools(self, G, connection_prob=0.8):
        """Add school connections"""
        logger.info("   Adding schools...")
        
        # Identify school-age children (5-18)
        students = []
        for node in G.nodes():
            if 5 <= G.nodes[node]['age'] <= 18:
                students.append(node)
        
        logger.info(f"   Found {len(students)} students")
        
        if not students:
            return
        
        # Create schools
        n_schools = max(1, len(students) // 30)  # Average 30 students per school
        schools = []
        
        for i in range(n_schools):
            school_size = random.randint(20, 40)
            schools.append([])
        
        # Assign students to schools
        for student in students:
            school_idx = random.randint(0, n_schools - 1)
            schools[school_idx].append(student)
        
        # Add connections within schools
        for school in schools:
            for i in range(len(school)):
                for j in range(i + 1, len(school)):
                    if random.random() < connection_prob:
                        node_i, node_j = school[i], school[j]
                        if G.has_edge(node_i, node_j):
                            G[node_i][node_j]['weight'] = max(2.5, G[node_i][node_j].get('weight', 1.0))
                            if 'type' not in G[node_i][node_j]:
                                G[node_i][node_j]['type'] = 'school'
                            else:
                                if G[node_i][node_j]['type'] != 'school':
                                    G[node_i][node_j]['type'] += ',school'
                        else:
                            G.add_edge(node_i, node_j, weight=2.5, type='school', active=True)
        
        logger.info(f"   Created {n_schools} schools")
    
    def _add_hubs(self, G, n_hubs=None):
        """Add hub nodes (super-spreaders)"""
        if n_hubs is None:
            n_hubs = max(5, self.population // 100)  # 1% of population
        
        logger.info(f"   Adding {n_hubs} hub nodes...")
        
        # Select hubs (prefer high-mobility, essential workers)
        potential_hubs = []
        for node in G.nodes():
            mobility = G.nodes[node]['mobility']
            if G.nodes[node].get('essential_worker', False):
                mobility += 0.3
            potential_hubs.append((node, mobility))
        
        potential_hubs.sort(key=lambda x: x[1], reverse=True)
        hubs = [node for node, _ in potential_hubs[:n_hubs]]

        # Materialise the node list once; rebuilding it per connection made
        # hub creation O(hubs x connections x N).
        all_nodes = list(G.nodes())

        for hub in hubs:
            G.nodes[hub]['hub'] = True

            # Scale hub degree with population so small networks are not
            # turned into one giant clique by a handful of super-spreaders.
            n_extra_connections = min(
                random.randint(20, 50),
                max(5, self.population // 20)
            )
            for _ in range(n_extra_connections):
                target = random.choice(all_nodes)
                if target == hub:
                    continue
                if G.has_edge(hub, target):
                    G[hub][target]['weight'] = max(2.0, G[hub][target].get('weight', 1.0))
                    if 'hub' not in G[hub][target].get('type', ''):
                        G[hub][target]['type'] = G[hub][target].get('type', '') + ',hub'
                else:
                    G.add_edge(hub, target, weight=2.0, type='hub', active=True)

        logger.info("Added %d hub nodes with extra connections", len(hubs))
    
    def _add_random_connections(self, G, connection_prob=0.4):
        """Add random long-distance connections"""
        logger.info("   Adding random connections...")
        
        n_random_edges = int(connection_prob * self.population)
        
        for _ in range(n_random_edges):
            u, v = random.sample(list(G.nodes()), 2)
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=0.8, type='random', active=True)
            elif 'random' not in G[u][v].get('type', ''):
                G[u][v]['type'] = G[u][v].get('type', '') + ',random'
                G[u][v]['weight'] = min(1.0, G[u][v].get('weight', 1.0) * 0.9)
    
    def _add_edge_attributes(self, G):
        """Add default attributes to all edges"""
        for u, v in G.edges():
            if 'weight' not in G[u][v]:
                G[u][v]['weight'] = 1.0
            if 'type' not in G[u][v]:
                G[u][v]['type'] = 'base'
            if 'active' not in G[u][v]:
                G[u][v]['active'] = True
    
    #  ATTRIBUTE GENERATION 
    def _add_attributes(self, G):
        """Add realistic demographic and disease-related attributes"""
        logger.info("   Adding node attributes...")
        
        # Generate synthetic demographic data
        ages = self._generate_age_distribution()
        occupations = self._generate_occupations(ages)
        
        for i, node in enumerate(G.nodes()):
            # Age
            age = ages[i] if i < len(ages) else random.randint(0, 90)
            G.nodes[node]['age'] = age
            
            # Occupation
            occ = occupations[i] if i < len(occupations) else 'worker'
            G.nodes[node]['occupation'] = occ
            
            # Mobility 
            G.nodes[node]['mobility'] = self._calculate_mobility(age, occ)
            
            # Essential worker flag
            G.nodes[node]['essential_worker'] = self._is_essential_worker(age, occ)
            
            # Health risk
            G.nodes[node]['health_risk'] = self._calculate_health_risk(age, occ)
            
            # Compliance with interventions
            G.nodes[node]['compliance'] = np.random.beta(3, 2)  # Most people compliant
            
            # Disease state
            G.nodes[node]['state'] = 'S'  # Susceptible
            G.nodes[node]['days_in_state'] = 0
            G.nodes[node]['immunity'] = 0.0
            G.nodes[node]['vaccinated'] = False
            G.nodes[node]['symptoms'] = None
            G.nodes[node]['isolated'] = False
            G.nodes[node]['wears_mask'] = False
            
            # Household (will be set later)
            G.nodes[node]['household'] = None
            
            # Position for visualization
            G.nodes[node]['x'] = random.random()
            G.nodes[node]['y'] = random.random()
        
        logger.info(f"   Attributes added to {G.number_of_nodes()} nodes")
    
    def _generate_age_distribution(self):
        """Generate realistic age distribution"""
        ages = []
        
        # Age groups with realistic proportions
        age_groups = [
            (0, 4, 0.06),     # 0-4: 6%
            (5, 14, 0.12),    # 5-14: 12%
            (15, 24, 0.13),   # 15-24: 13%
            (25, 34, 0.13),   # 25-34: 13%
            (35, 44, 0.12),   # 35-44: 12%
            (45, 54, 0.11),   # 45-54: 11%
            (55, 64, 0.10),   # 55-64: 10%
            (65, 74, 0.08),   # 65-74: 8%
            (75, 90, 0.05)    # 75+: 5%
        ]
        
        for age_min, age_max, proportion in age_groups:
            n_people = int(proportion * self.population)
            ages.extend(np.random.randint(age_min, age_max + 1, n_people))
        
        # Fill any remaining
        while len(ages) < self.population:
            ages.append(random.randint(0, 90))
        
        np.random.shuffle(ages)
        return ages
    
    def _generate_occupations(self, ages):
        """Generate occupations based on age"""
        occupations = []
        
        for age in ages:
            if age < 16:
                occupations.append('student')
            elif age < 22:
                # Young adults: mix of students and workers
                if random.random() < 0.4:
                    occupations.append('student')
                else:
                    occupations.append('worker')
            elif age < 65:
                # Working age
                if random.random() < 0.05:  # 5% unemployed
                    occupations.append('unemployed')
                else:
                    occupations.append('worker')
            else:
                # Retirement age
                if random.random() < 0.8:  # 80% retired
                    occupations.append('retired')
                else:
                    occupations.append('worker')  # Some continue working
        
        return occupations
    
    def _calculate_mobility(self, age, occupation):
        """Calculate mobility score (0-1)"""
        base = 0.5
        
        # Age adjustments
        if age < 5:
            base = 0.3
        elif age < 18:
            base = 0.6
        elif age < 30:
            base = 0.8
        elif age < 50:
            base = 0.7
        elif age < 70:
            base = 0.5
        else:
            base = 0.3
        
        # Occupation adjustments
        if occupation == 'student':
            base *= 1.2
        elif occupation == 'worker':
            base *= 1.1
        elif occupation == 'essential':
            base *= 1.3
        elif occupation == 'retired':
            base *= 0.7
        elif occupation == 'unemployed':
            base *= 0.9
        
        # Add some randomness
        base += np.random.normal(0, 0.1)
        
        # Clip to reasonable range
        return np.clip(base, 0.1, 0.95)
    
    def _is_essential_worker(self, age, occupation):
        """Determine if someone is an essential worker"""
        if occupation != 'worker':
            return False
        
        # Essential workers are typically 20-60
        if not (20 <= age <= 60):
            return False
        
        # About 30% of workers are essential
        return random.random() < 0.3
    
    def _calculate_health_risk(self, age, occupation):
        """Calculate health risk factor (0-1)"""
        risk = 0.0
        
        # Age-based risk
        if age < 10:
            risk = 0.1
        elif age < 20:
            risk = 0.05
        elif age < 40:
            risk = 0.1
        elif age < 50:
            risk = 0.2
        elif age < 60:
            risk = 0.3
        elif age < 70:
            risk = 0.5
        elif age < 80:
            risk = 0.7
        else:
            risk = 0.9
        
        # Occupation adjustments
        if occupation == 'worker':
            risk *= 1.1  # Workers have more exposure
        elif occupation == 'essential':
            risk *= 1.3  # Essential workers have highest exposure
        elif occupation == 'retired':
            risk *= 1.2  # Retired are older
        
        # Add some randomness
        risk += np.random.normal(0, 0.05)
        
        return np.clip(risk, 0.0, 1.0)
    
    #  ANALYSIS METHODS 
    def analyze_network(self, G):
        """Print network statistics"""
        logger.info("\n📊 NETWORK ANALYSIS:")
        logger.info(f"   Nodes: {G.number_of_nodes()}")
        logger.info(f"   Edges: {G.number_of_edges()}")
        logger.info(f"   Density: {nx.density(G):.4f}")
        logger.info(f"   Average degree: {np.mean([d for n, d in G.degree()]):.2f}")
        
        # Degree distribution
        degrees = [d for n, d in G.degree()]
        logger.info(f"   Max degree: {max(degrees)}")
        logger.info(f"   Min degree: {min(degrees)}")
        
        # Connected components
        components = list(nx.connected_components(G))
        logger.info(f"   Connected components: {len(components)}")
        logger.info(f"   Largest component: {max(len(c) for c in components)} nodes")
        
        # Edge types
        edge_types = {}
        for u, v, data in G.edges(data=True):
            edge_type = data.get('type', 'unknown')
            if edge_type not in edge_types:
                edge_types[edge_type] = 0
            edge_types[edge_type] += 1
        
        logger.info("\n   Edge types:")
        for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"     {edge_type}: {count} edges ({count/G.number_of_edges()*100:.1f}%)")
        
        return {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_degree': np.mean(degrees),
            'components': len(components),
            'edge_types': edge_types
        }


#  QUICK TEST 
if __name__ == "__main__":
    logger.info("🧪 Testing Network Generator...")
    
    # Create generator
    generator = UltimateNetworkGenerator(population=500)
    
    # Test different network types
    logger.info("\n1. Testing Erdős–Rényi network:")
    G_er = generator.erdos_renyi(p=0.02)
    generator.analyze_network(G_er)
    
    logger.info("\n2. Testing Hybrid Multilayer network:")
    G_hybrid = generator.hybrid_multilayer()
    generator.analyze_network(G_hybrid)
    
    logger.info("\n3. Testing Watts-Strogatz network:")
    G_ws = generator.watts_strogatz(k=6, p=0.3)
    generator.analyze_network(G_ws)
    
    logger.info("\n✅ Network Generator Test Complete!")