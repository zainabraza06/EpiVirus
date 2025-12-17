# visualization_3d.py
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import plotly.io as pio
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import json
import os
from tqdm import tqdm
# visualization_3d.py - ADD THIS IMPORT
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class PandemicVisualizer3D:
    """
    Advanced 3D visualization for pandemic simulation
    Force-directed layouts + Time animation + Interactive dashboards
    """
    
    def __init__(self, simulator=None):
        """
        Initialize visualizer with optional simulator
        
        Args:
            simulator: UltimateSimulator instance (optional)
        """
        self.simulator = simulator
        self.G = simulator.G if simulator else None
        self.history = simulator.history if simulator else None
        
        # Visualization settings
        self.config = {
            'node_size': 8,
            'edge_width': 0.5,
            'edge_alpha': 0.1,
            'animation_fps': 10,
            'color_scheme': 'disease_state',  # 'disease_state', 'age', 'mobility', 'degree'
            'layout_algorithm': 'spring',  # 'spring', 'kamada_kawai', 'fruchterman_reingold'
            '3d_enabled': True,
            'interactive': True,
            'save_frames': False
        }
        
        # Color mappings
        self.color_palettes = {
            'disease_state': {
                'S': 'rgb(100, 200, 100)',   # Green - Susceptible
                'E': 'rgb(255, 165, 0)',     # Orange - Exposed
                'I': 'rgb(255, 50, 50)',     # Red - Infectious
                'Ia': 'rgb(255, 100, 100)',  # Light red - Asymptomatic
                'Im': 'rgb(255, 0, 0)',      # Red - Mild
                'Is': 'rgb(200, 0, 0)',      # Dark red - Severe
                'Ih': 'rgb(128, 0, 128)',    # Purple - Hospitalized
                'Ic': 'rgb(0, 0, 0)',        # Black - Critical
                'R': 'rgb(100, 100, 255)',   # Blue - Recovered
                'D': 'rgb(100, 100, 100)',   # Gray - Deceased
                'V': 'rgb(180, 100, 255)'    # Purple - Vaccinated
            },
            'age': 'viridis',
            'mobility': 'plasma',
            'degree': 'hot',
            'community': 'Set3'
        }
        
        # Layout cache
        self.layout_cache = {}
        self.current_frame = 0
        
        print("🎨 Pandemic 3D Visualizer Initialized")
    
    # ==================== NETWORK LAYOUTS ====================
    
    def compute_force_directed_layout(self, G=None, dimensions=3, iterations=100, 
                                     seed=42, algorithm='spring'):
        """
        Compute force-directed layout for network visualization
        
        Args:
            G: NetworkX graph (uses self.G if None)
            dimensions: 2 or 3 dimensions
            iterations: Number of layout iterations
            algorithm: 'spring', 'kamada_kawai', 'fruchterman_reingold'
            
        Returns:
            Dictionary of node positions
        """
        if G is None:
            G = self.G
        if G is None:
            raise ValueError("No graph provided")
        
        print(f"🔄 Computing {dimensions}D layout using {algorithm} algorithm...")
        
        # Check cache first
        cache_key = f"{len(G.nodes())}_{dimensions}_{algorithm}_{seed}"
        if cache_key in self.layout_cache:
            print("   Using cached layout")
            return self.layout_cache[cache_key]
        
        if algorithm == 'spring':
            # Fruchterman-Reingold force-directed algorithm
            pos = nx.spring_layout(G, dim=dimensions, iterations=iterations, 
                                  seed=seed, k=2/np.sqrt(len(G)))
        
        elif algorithm == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G, dim=dimensions)
        
        elif algorithm == 'fruchterman_reingold':
            # Custom implementation for more control
            pos = self._fruchterman_reingold_3d(G, iterations=iterations)
        
        else:
            pos = nx.spring_layout(G, dim=dimensions, seed=seed)
        
        # Cache the layout
        self.layout_cache[cache_key] = pos
        
        print(f"✅ Layout computed for {len(G.nodes())} nodes")
        return pos
    
    def _fruchterman_reingold_3d(self, G, iterations=100, 
                                 k=None, scale=1.0, seed=42):
        """
        Custom 3D Fruchterman-Reingold force-directed layout
        Provides more control than NetworkX default
        """
        np.random.seed(seed)
        
        n = len(G)
        if k is None:
            k = np.sqrt(1.0 / n)
        
        # Initialize random positions
        pos = {i: np.random.rand(3) * scale for i in G.nodes()}
        
        # Precompute adjacency matrix for efficiency
        adj_matrix = nx.adjacency_matrix(G).todense()
        
        # Temperature (cooling schedule)
        t = scale
        dt = t / (iterations + 1)
        
        for iteration in range(iterations):
            # Calculate repulsive forces
            repulsive_forces = {}
            for i in G.nodes():
                repulsive_forces[i] = np.zeros(3)
                for j in G.nodes():
                    if i != j:
                        diff = pos[i] - pos[j]
                        distance = np.linalg.norm(diff) + 0.01  # Avoid division by zero
                        repulsive_forces[i] += (k**2 / distance) * (diff / distance)
            
            # Calculate attractive forces
            attractive_forces = {}
            for i in G.nodes():
                attractive_forces[i] = np.zeros(3)
            
            for i, j in G.edges():
                diff = pos[i] - pos[j]
                distance = np.linalg.norm(diff)
                attractive_force = (distance**2 / k) * (diff / distance)
                attractive_forces[i] -= attractive_force
                attractive_forces[j] += attractive_force
            
            # Update positions
            for i in G.nodes():
                displacement = repulsive_forces[i] + attractive_forces[i]
                # Normalize and apply temperature
                norm = np.linalg.norm(displacement)
                if norm > 0:
                    displacement = displacement / norm
                
                pos[i] += displacement * min(t, norm)
                # Keep within bounds
                pos[i] = np.clip(pos[i], -scale, scale)
            
            # Cool down
            t -= dt
            
            if iteration % 20 == 0:
                print(f"   Iteration {iteration}/{iterations}, temperature: {t:.3f}")
        
        return pos
    
    def compute_community_layout(self, G=None, community_detection='louvain'):
        """
        Compute layout that emphasizes community structure
        
        Args:
            G: NetworkX graph
            community_detection: 'louvain', 'girvan_newman', 'label_propagation'
            
        Returns:
            Dictionary of node positions with community info
        """
        if G is None:
            G = self.G
        
        print(f"🏘️  Computing community-based layout using {community_detection}...")
        
        # Detect communities
        if community_detection == 'louvain':
            import community as community_louvain
            partitions = community_louvain.best_partition(G)
        elif community_detection == 'label_propagation':
            from networkx.algorithms.community import label_propagation_communities
            communities = list(label_propagation_communities(G))
            partitions = {}
            for i, comm in enumerate(communities):
                for node in comm:
                    partitions[node] = i
        else:  # girvan_newman
            from networkx.algorithms.community import girvan_newman
            communities = next(girvan_newman(G))
            partitions = {}
            for i, comm in enumerate(communities):
                for node in comm:
                    partitions[node] = i
        
        # Compute layout within each community
        pos = {}
        community_nodes = {}
        
        for node, comm_id in partitions.items():
            if comm_id not in community_nodes:
                community_nodes[comm_id] = []
            community_nodes[comm_id].append(node)
        
        # Position communities in a circle
        n_communities = len(community_nodes)
        community_centers = []
        for i in range(n_communities):
            angle = 2 * np.pi * i / n_communities
            community_centers.append([np.cos(angle), np.sin(angle), 0])
        
        # Position nodes within each community
        for comm_id, nodes in community_nodes.items():
            center = community_centers[comm_id % n_communities]
            subgraph = G.subgraph(nodes)
            
            # Compute local layout for this community
            if len(nodes) > 1:
                local_pos = nx.spring_layout(subgraph, dim=3, seed=42, scale=0.3)
                for node, local_pos_vec in local_pos.items():
                    pos[node] = np.array(center) + local_pos_vec
            else:
                pos[nodes[0]] = np.array(center)
            
            # Add community attribute
            for node in nodes:
                G.nodes[node]['community'] = comm_id
        
        print(f"✅ Found {n_communities} communities")
        return pos, partitions
    
    # ==================== 3D NETWORK VISUALIZATION ====================
    
    def create_3d_network_plot(self, G=None, pos=None, day=0, 
                              color_by='disease_state', title=None,
                              show_edges=True, show_labels=False):
        """
        Create interactive 3D network plot using Plotly
        
        Returns:
            plotly.graph_objects.Figure
        """
        if G is None:
            G = self.G
        if G is None:
            raise ValueError("No graph provided")
        
        print(f"🔄 Creating 3D network visualization (Day {day})...")
        
        # Compute layout if not provided
        if pos is None:
            pos = self.compute_force_directed_layout(G, dimensions=3)
        
        # Prepare node data
        node_x, node_y, node_z = [], [], []
        node_colors, node_sizes, node_text = [], [], []
        node_symbols = []
        
        for node in G.nodes():
            x, y, z = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            
            # Node color based on attribute
            color = self._get_node_color(G, node, color_by)
            node_colors.append(color)
            
            # Node size based on degree or importance
            size = self._get_node_size(G, node)
            node_sizes.append(size)
            
            # Node symbol based on state
            symbol = self._get_node_symbol(G, node)
            node_symbols.append(symbol)
            
            # Tooltip text
            text = self._get_node_tooltip(G, node, day)
            node_text.append(text)
        
        # Create node trace
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                symbol=node_symbols,
                line=dict(color='rgba(50, 50, 50, 0.5)', width=1),
                opacity=0.9
            ),
            text=node_text,
            hoverinfo='text',
            name='Individuals'
        )
        
        # Create edge traces if requested
        edge_traces = []
        if show_edges:
            # Group edges by type for better visualization
            edge_types = defaultdict(list)
            for u, v, data in G.edges(data=True):
                edge_type = data.get('type', 'default')
                edge_types[edge_type].append((u, v))
            
            # Different styles for different edge types
            edge_styles = {
                'household': dict(color='rgba(0, 100, 255, 0.4)', width=3),
                'workplace': dict(color='rgba(255, 100, 0, 0.3)', width=2),
                'school': dict(color='rgba(0, 200, 100, 0.3)', width=2),
                'hub': dict(color='rgba(255, 50, 50, 0.5)', width=4),
                'random': dict(color='rgba(150, 150, 150, 0.1)', width=1),
                'default': dict(color='rgba(150, 150, 150, 0.2)', width=1)
            }
            
            for edge_type, edges in edge_types.items():
                edge_x, edge_y, edge_z = [], [], []
                
                for u, v in edges:
                    x0, y0, z0 = pos[u]
                    x1, y1, z1 = pos[v]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    edge_z.extend([z0, z1, None])
                
                style = edge_styles.get(edge_type, edge_styles['default'])
                
                edge_trace = go.Scatter3d(
                    x=edge_x, y=edge_y, z=edge_z,
                    mode='lines',
                    line=style,
                    hoverinfo='none',
                    name=f'{edge_type} connections',
                    opacity=0.6,
                    showlegend=len(edge_types) > 1
                )
                edge_traces.append(edge_trace)
        
        # Create figure
        data = edge_traces + [node_trace] if edge_traces else [node_trace]
        
        fig = go.Figure(data=data)
        
        # Update layout
        if title is None:
            title = f"3D Social Network - Day {day}"
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color='white')
            ),
            scene=dict(
                xaxis=dict(
                    showbackground=False,
                    showticklabels=False,
                    title='',
                    gridcolor='rgba(50, 50, 50, 0.2)',
                    zerolinecolor='rgba(50, 50, 50, 0.5)'
                ),
                yaxis=dict(
                    showbackground=False,
                    showticklabels=False,
                    title='',
                    gridcolor='rgba(50, 50, 50, 0.2)',
                    zerolinecolor='rgba(50, 50, 50, 0.5)'
                ),
                zaxis=dict(
                    showbackground=False,
                    showticklabels=False,
                    title='',
                    gridcolor='rgba(50, 50, 50, 0.2)',
                    zerolinecolor='rgba(50, 50, 50, 0.5)'
                ),
                bgcolor='rgba(10, 10, 20, 1)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0)
                )
            ),
            paper_bgcolor='rgba(0, 0, 0, 1)',
            plot_bgcolor='rgba(0, 0, 0, 1)',
            font=dict(color='white'),
            height=800,
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0, 0, 0, 0.7)',
                bordercolor='rgba(255, 255, 255, 0.3)',
                borderwidth=1
            )
        )
        
        # Add annotation for statistics
        if self.simulator and day < len(self.history['time']):
            stats_text = self._get_day_stats(day)
            fig.add_annotation(
                x=0.02, y=0.98,
                xref="paper", yref="paper",
                text=stats_text,
                showarrow=False,
                font=dict(size=12, color='white'),
                align='left',
                bgcolor='rgba(0, 0, 0, 0.5)',
                bordercolor='rgba(255, 255, 255, 0.3)',
                borderwidth=1,
                borderpad=10
            )
        
        print("✅ 3D network plot created")
        return fig
    
    def _get_node_color(self, G, node, color_by='disease_state'):
        """Get color for a node based on attribute"""
        if color_by == 'disease_state':
            state = G.nodes[node].get('state', 'S')
            return self.color_palettes['disease_state'].get(state, 'rgb(150, 150, 150)')
        
        elif color_by == 'age':
            age = G.nodes[node].get('age', 40)
            # Normalize age to 0-1
            age_norm = min(age / 100, 1.0)
            # Use colormap
            cmap = cm.get_cmap(self.color_palettes['age'])
            rgba = cmap(age_norm)
            return f'rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})'
        
        elif color_by == 'mobility':
            mobility = G.nodes[node].get('mobility', 0.5)
            cmap = cm.get_cmap(self.color_palettes['mobility'])
            rgba = cmap(mobility)
            return f'rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})'
        
        elif color_by == 'degree':
            degree = G.degree(node)
            max_degree = max([d for _, d in G.degree()])
            degree_norm = degree / max_degree if max_degree > 0 else 0
            cmap = cm.get_cmap(self.color_palettes['degree'])
            rgba = cmap(degree_norm)
            return f'rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})'
        
        elif color_by == 'community':
            community = G.nodes[node].get('community', 0)
            # Cycle through colors for communities
            colors = px.colors.qualitative.Set3
            return colors[community % len(colors)]
        
        else:
            return 'rgb(150, 150, 150)'
    
    def _get_node_size(self, G, node):
        """Get size for a node based on importance"""
        base_size = self.config['node_size']
        
        # Larger for infectious individuals
        state = G.nodes[node].get('state', 'S')
        if state in ['I', 'Ia', 'Im', 'Is', 'Ih', 'Ic']:
            base_size *= 1.5
        
        # Larger for super-spreaders (high degree)
        degree = G.degree(node)
        if degree > np.percentile([d for _, d in G.degree()], 90):
            base_size *= 1.3
        
        # Larger for recently infected
        if 'infection_time' in G.nodes[node]:
            infection_time = G.nodes[node]['infection_time']
            days_infected = self.current_frame - infection_time
            if days_infected < 7:  # Recently infected
                base_size *= 1.2
        
        return base_size
    
    def _get_node_symbol(self, G, node):
        """Get symbol for a node based on state"""
        state = G.nodes[node].get('state', 'S')
        
        symbols = {
            'S': 'circle',      # Susceptible
            'E': 'square',      # Exposed
            'I': 'diamond',     # Infectious
            'Ia': 'circle',     # Asymptomatic
            'Im': 'diamond',    # Mild
            'Is': 'diamond',    # Severe
            'Ih': 'cross',      # Hospitalized
            'Ic': 'x',          # Critical
            'R': 'circle',      # Recovered
            'D': 'square',      # Deceased
            'V': 'triangle-up'  # Vaccinated
        }
        
        return symbols.get(state, 'circle')
    
    def _get_node_tooltip(self, G, node, day):
        """Create tooltip text for a node"""
        state = G.nodes[node].get('state', 'S')
        age = G.nodes[node].get('age', 'Unknown')
        occupation = G.nodes[node].get('occupation', 'Unknown')
        mobility = G.nodes[node].get('mobility', 0.5)
        degree = G.degree(node)
        
        tooltip = f"<b>Node {node}</b><br>"
        tooltip += f"State: {state}<br>"
        tooltip += f"Age: {age}<br>"
        tooltip += f"Occupation: {occupation}<br>"
        tooltip += f"Mobility: {mobility:.2f}<br>"
        tooltip += f"Connections: {degree}<br>"
        
        if 'infection_time' in G.nodes[node]:
            infection_time = G.nodes[node]['infection_time']
            days_infected = day - infection_time
            tooltip += f"Infected: Day {infection_time} ({days_infected} days ago)<br>"
        
        if 'symptoms' in G.nodes[node]:
            symptoms = G.nodes[node]['symptoms']
            if symptoms:
                tooltip += f"Symptoms: {symptoms}<br>"
        
        if G.nodes[node].get('vaccinated', False):
            tooltip += "Vaccinated: Yes<br>"
        
        if G.nodes[node].get('isolated', False):
            tooltip += "Isolated: Yes<br>"
        
        return tooltip
    
    def _get_day_stats(self, day):
        """Get statistics text for a given day"""
        if not self.history or day >= len(self.history['time']):
            return ""
        
        stats = f"<b>Day {day}</b><br>"
        stats += f"Susceptible: {self.history['S'][day]}<br>"
        stats += f"Infectious: {self.history['I'][day]}<br>"
        stats += f"Recovered: {self.history['R'][day]}<br>"
        stats += f"Deceased: {self.history['D'][day]}<br>"
        
        if day > 0:
            new_cases = self.history['new_infections'][day]
            stats += f"New Cases: {new_cases}<br>"
        
        return stats
    
    # ==================== TIME ANIMATION ====================
    
    def create_animation(self, days=None, output_file='animation.mp4', 
                        fps=10, dpi=150, show_progress=True):
        """
        Create animation of pandemic spread over time
        
        Args:
            days: List of days to animate (or range if None)
            output_file: Output file path
            fps: Frames per second
            dpi: Resolution
        """
        if self.simulator is None:
            raise ValueError("No simulator provided for animation")
        
        if days is None:
            days = range(len(self.history['time']))
        
        print(f"🎬 Creating animation for {len(days)} days...")
        
        # Create frames
        frames = []
        
        day_range = tqdm(days) if show_progress else days
        for day in day_range:
            # Update simulator state to this day
            self._restore_simulator_state(day)
            
            # Create frame
            fig = self.create_3d_network_plot(
                day=day,
                color_by=self.config['color_scheme'],
                title=f"Day {day}",
                show_edges=True,
                show_labels=False
            )
            
            frames.append(fig)
            
            if show_progress:
                day_range.set_description(f"Frame {day+1}/{len(days)}")
        
        print("✅ All frames created")
        
        # Save animation
        self._save_animation(frames, output_file, fps)
        
        return frames
    
    def _restore_simulator_state(self, day):
        """Restore simulator state to a specific day (simplified)"""
        # In a full implementation, you would restore from saved states
        # For now, we just update the current frame
        self.current_frame = day
        
        # Update node states based on history
        if self.history and day < len(self.history['time']):
            # This is simplified - in reality you'd need to restore full state
            pass
    
    def _save_animation(self, frames, output_file, fps):
        """Save animation to file"""
        print(f"💾 Saving animation to {output_file}...")
        
        # Determine output format
        file_ext = output_file.split('.')[-1].lower()
        
        if file_ext in ['html', 'htm']:
            # Create interactive HTML animation
            self._create_html_animation(frames, output_file)
        
        elif file_ext in ['gif']:
            # Create GIF animation
            self._create_gif_animation(frames, output_file, fps)
        
        elif file_ext in ['mp4', 'avi', 'mov']:
            # Create video (requires ffmpeg)
            self._create_video_animation(frames, output_file, fps)
        
        else:
            print(f"⚠️  Unsupported file format: {file_ext}")
            print("   Saving as HTML instead")
            html_file = output_file.rsplit('.', 1)[0] + '.html'
            self._create_html_animation(frames, html_file)
    
    def _create_html_animation(self, frames, output_file):
        """Create interactive HTML animation"""
        # Create slider animation
        fig = frames[0]
        
        # Add frames for animation
        animation_frames = []
        for i, frame in enumerate(frames):
            animation_frames.append(
                go.Frame(
                    data=frame.data,
                    layout=frame.layout,
                    name=f"Day {i}"
                )
            )
        
        fig.frames = animation_frames
        
        # Add slider
        sliders = [dict(
            steps=[dict(
                method='animate',
                args=[[f"Day {i}"], 
                     dict(mode='immediate', frame=dict(duration=300, redraw=True))],
                label=f"Day {i}"
            ) for i in range(len(frames))],
            active=0,
            transition=dict(duration=300),
            x=0.1, y=0,
            len=0.8,
            currentvalue=dict(
                font=dict(size=16),
                prefix='Day: ',
                visible=True,
                xanchor='center'
            ),
            pad=dict(t=50, b=10)
        )]
        
        fig.update_layout(sliders=sliders)
        
        # Add play button
        fig.update_layout(
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                y=-0.1,
                x=0.1,
                xanchor='right',
                yanchor='top',
                pad=dict(t=0, r=10),
                buttons=[dict(
                    label='▶️ Play',
                    method='animate',
                    args=[None, dict(
                        frame=dict(duration=500, redraw=True),
                        fromcurrent=True,
                        transition=dict(duration=300)
                    )]
                ),
                dict(
                    label='⏸️ Pause',
                    method='animate',
                    args=[[None], dict(
                        mode='immediate',
                        transition=dict(duration=0)
                    )]
                )]
            )]
        )
        
        # Save HTML
        fig.write_html(output_file)
        print(f"✅ HTML animation saved to {output_file}")
    
    def _create_gif_animation(self, frames, output_file, fps):
        """Create GIF animation using matplotlib"""
        print("⚠️  GIF creation requires matplotlib animation - creating simplified version")
        
        # Create a simple 2D animation instead
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def update(frame):
            ax.clear()
            day = frame
            
            # Create simplified 2D visualization
            G = self.simulator.G
            
            # Use 2D layout
            pos = self.compute_force_directed_layout(G, dimensions=2)
            
            # Draw nodes
            node_colors = []
            for node in G.nodes():
                color = self._get_node_color(G, node, 'disease_state')
                # Convert rgb string to matplotlib color
                if color.startswith('rgb('):
                    rgb = color[4:-1].split(',')
                    node_colors.append([int(c)/255 for c in rgb])
                else:
                    node_colors.append('gray')
            
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                  node_size=50, alpha=0.8, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.5, ax=ax)
            
            ax.set_title(f"Day {day}")
            ax.axis('off')
        
        anim = FuncAnimation(fig, update, frames=len(self.history['time']), 
                           interval=1000/fps)
        
        # Save GIF
        writer = PillowWriter(fps=fps)
        anim.save(output_file, writer=writer, dpi=150)
        
        plt.close()
        print(f"✅ GIF animation saved to {output_file}")
    
    def _create_video_animation(self, frames, output_file, fps):
        """Create video animation (requires ffmpeg)"""
        print("⚠️  Video creation requires ffmpeg and more complex setup")
        print("   Consider using HTML animation instead")
        
        # For now, create HTML as fallback
        html_file = output_file.rsplit('.', 1)[0] + '.html'
        self._create_html_animation(frames, html_file)
    
    # ==================== DASHBOARD VISUALIZATION ====================
    
    def create_comprehensive_dashboard(self, output_file='dashboard.html'):
        """
        Create comprehensive interactive dashboard with multiple visualizations
        """
        print("📊 Creating comprehensive dashboard...")
        
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=3,
            specs=[
                [{'type': 'scene', 'rowspan': 2, 'colspan': 2}, None, {'type': 'xy'}],
                [None, None, {'type': 'xy'}],
                [{'type': 'xy'}, {'type': 'xy'}, {'type': 'xy'}]
            ],
            subplot_titles=(
                '3D Network Visualization',
                'Epidemic Curve',
                'Age Distribution of Cases',
                'Network Metrics',
                'Intervention Timeline',
                'Reproduction Number (R)'
            ),
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        # 1. 3D Network (top-left)
        network_fig = self.create_3d_network_plot(day=0)
        for trace in network_fig.data:
            fig.add_trace(trace, row=1, col=1)
        
        # 2. Epidemic Curve (top-right)
        if self.history:
            days = self.history['time']
            fig.add_trace(
                go.Scatter(x=days, y=self.history['S'], name='Susceptible',
                          line=dict(color='green', width=2)),
                row=1, col=3
            )
            fig.add_trace(
                go.Scatter(x=days, y=self.history['I'], name='Infectious',
                          line=dict(color='red', width=3)),
                row=1, col=3
            )
            fig.add_trace(
                go.Scatter(x=days, y=self.history['R'], name='Recovered',
                          line=dict(color='blue', width=2)),
                row=1, col=3
            )
        
        # 3. Age Distribution (middle-right)
        if self.G:
            ages = [self.G.nodes[node]['age'] for node in self.G.nodes()]
            fig.add_trace(
                go.Histogram(x=ages, name='Population Age',
                            marker_color='lightblue', opacity=0.7),
                row=2, col=3
            )
        
        # 4. Network Metrics (bottom-left)
        if self.G:
            degrees = [d for _, d in self.G.degree()]
            fig.add_trace(
                go.Histogram(x=degrees, name='Degree Distribution',
                            marker_color='orange', opacity=0.7),
                row=3, col=1
            )
        
        # 5. Intervention Timeline (bottom-middle)
        if self.simulator and hasattr(self.simulator, 'interventions'):
            # Create timeline of interventions
            intervention_days = []
            intervention_names = []
            
            # This would need actual intervention history
            # For now, add placeholder
            fig.add_trace(
                go.Scatter(x=[30, 60, 90], y=[1, 1, 1],
                          mode='markers+text',
                          marker=dict(size=20, color='purple'),
                          text=['Mask Mandate', 'Vaccination', 'Reopening'],
                          textposition='top center'),
                row=3, col=2
            )
        
        # 6. Reproduction Number (bottom-right)
        if self.simulator and self.simulator.stats['r_effective']:
            r_values = self.simulator.stats['r_effective']
            fig.add_trace(
                go.Scatter(y=r_values, name='R-effective',
                          line=dict(color='red', width=2)),
                row=3, col=3
            )
            fig.add_hline(y=1.0, line_dash='dash', line_color='gray',
                         row=3, col=3)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='Pandemic Simulation Dashboard',
                font=dict(size=24, color='white'),
                x=0.5
            ),
            height=1200,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,1)',
            plot_bgcolor='rgba(0,0,0,1)',
            font=dict(color='white'),
            legend=dict(
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='rgba(255,255,255,0.3)'
            )
        )
        
        # Update 3D scene
        fig.update_scenes(
            dict(
                xaxis_showbackground=False,
                yaxis_showbackground=False,
                zaxis_showbackground=False,
                bgcolor='rgba(10,10,20,1)'
            ),
            row=1, col=1
        )
        
        # Update axes
        for i in [3, 4, 5, 6, 7, 8]:
            fig.update_xaxes(gridcolor='rgba(50,50,50,0.5)', row=(i-1)//3+1, col=(i-1)%3+1)
            fig.update_yaxes(gridcolor='rgba(50,50,50,0.5)', row=(i-1)//3+1, col=(i-1)%3+1)
        
        # Save dashboard
        fig.write_html(output_file)
        print(f"✅ Dashboard saved to {output_file}")
        
        return fig
    
    # ==================== STATIC PLOTS ====================
    
    def create_epidemic_curves_plot(self, output_file='epidemic_curves.png'):
        """Create static plot of epidemic curves"""
        if not self.history:
            raise ValueError("No history data available")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: SEIR curves
        days = self.history['time']
        axes[0, 0].plot(days, self.history['S'], 'g-', label='Susceptible', linewidth=3)
        axes[0, 0].plot(days, self.history['E'], 'orange', label='Exposed', linewidth=2)
        axes[0, 0].plot(days, self.history['I'], 'r-', label='Infectious', linewidth=3)
        axes[0, 0].plot(days, self.history['R'], 'b-', label='Recovered', linewidth=3)
        axes[0, 0].plot(days, self.history['D'], 'gray', label='Deceased', linewidth=2)
        axes[0, 0].set_xlabel('Days', fontsize=12)
        axes[0, 0].set_ylabel('Individuals', fontsize=12)
        axes[0, 0].set_title('SEIRD Dynamics', fontsize=14, fontweight='bold')
        axes[0, 0].legend(loc='best')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Daily new cases
        axes[0, 1].bar(days, self.history['new_infections'], 
                      color='darkred', alpha=0.7, label='New Cases')
        axes[0, 1].set_xlabel('Days', fontsize=12)
        axes[0, 1].set_ylabel('New Infections', fontsize=12)
        axes[0, 1].set_title('Daily New Cases', fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Hospital burden
        axes[1, 0].stackplot(days, 
                            self.history.get('Ih', [0]*len(days)),
                            self.history.get('Ic', [0]*len(days)),
                            colors=['purple', 'black'],
                            labels=['Hospitalized', 'Critical'])
        axes[1, 0].set_xlabel('Days', fontsize=12)
        axes[1, 0].set_ylabel('Patients', fontsize=12)
        axes[1, 0].set_title('Hospital Bed Usage', fontsize=14, fontweight='bold')
        axes[1, 0].legend(loc='best')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Age distribution of infections
        if self.G:
            # Get ages of infected individuals
            infected_ages = []
            for node in self.G.nodes():
                if self.G.nodes[node].get('infection_time', float('inf')) < float('inf'):
                    infected_ages.append(self.G.nodes[node]['age'])
            
            if infected_ages:
                axes[1, 1].hist(infected_ages, bins=20, color='red', 
                               alpha=0.7, edgecolor='black')
                axes[1, 1].set_xlabel('Age', fontsize=12)
                axes[1, 1].set_ylabel('Count', fontsize=12)
                axes[1, 1].set_title('Age Distribution of Infections', 
                                   fontsize=14, fontweight='bold')
                axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle('Pandemic Simulation Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Epidemic curves saved to {output_file}")
    
    def create_network_metrics_plot(self, output_file='network_metrics.png'):
        """Create plot showing network metrics"""
        if self.G is None:
            raise ValueError("No graph available")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Degree distribution
        degrees = [d for _, d in self.G.degree()]
        axes[0, 0].hist(degrees, bins=30, color='blue', alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('Degree', fontsize=12)
        axes[0, 0].set_ylabel('Frequency', fontsize=12)
        axes[0, 0].set_title('Degree Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Age distribution
        ages = [self.G.nodes[node]['age'] for node in self.G.nodes()]
        axes[0, 1].hist(ages, bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0, 1].set_xlabel('Age', fontsize=12)
        axes[0, 1].set_ylabel('Frequency', fontsize=12)
        axes[0, 1].set_title('Age Distribution', fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Mobility distribution
        mobilities = [self.G.nodes[node].get('mobility', 0.5) for node in self.G.nodes()]
        axes[1, 0].hist(mobilities, bins=20, color='orange', alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Mobility', fontsize=12)
        axes[1, 0].set_ylabel('Frequency', fontsize=12)
        axes[1, 0].set_title('Mobility Distribution', fontsize=14, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Clustering by age
        age_bins = [0, 18, 30, 50, 70, 100]
        age_labels = ['0-17', '18-29', '30-49', '50-69', '70+']
        clustering_by_age = []
        
        for i in range(len(age_bins)-1):
            age_nodes = [n for n in self.G.nodes() 
                        if age_bins[i] <= self.G.nodes[n]['age'] < age_bins[i+1]]
            if len(age_nodes) > 1:
                subgraph = self.G.subgraph(age_nodes)
                clustering = nx.average_clustering(subgraph)
                clustering_by_age.append(clustering)
            else:
                clustering_by_age.append(0)
        
        axes[1, 1].bar(age_labels, clustering_by_age, color='purple', alpha=0.7)
        axes[1, 1].set_xlabel('Age Group', fontsize=12)
        axes[1, 1].set_ylabel('Average Clustering', fontsize=12)
        axes[1, 1].set_title('Social Clustering by Age', fontsize=14, fontweight='bold')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle('Network and Demographic Metrics', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Network metrics saved to {output_file}")
    
    # ==================== EXPORT FUNCTIONS ====================
    
    def export_visualization_data(self, output_dir='visualization_data'):
        """Export all visualization data for external tools"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📤 Exporting visualization data to {output_dir}/...")
        
        # 1. Export network data
        if self.G:
            # Export as GraphML
            nx.write_graphml(self.G, f'{output_dir}/network.graphml')
            
            # Export as CSV for easier processing
            nodes_data = []
            for node in self.G.nodes():
                node_data = {'id': node}
                node_data.update(self.G.nodes[node])
                nodes_data.append(node_data)
            
            pd.DataFrame(nodes_data).to_csv(f'{output_dir}/nodes.csv', index=False)
            
            edges_data = []
            for u, v, data in self.G.edges(data=True):
                edge_data = {'source': u, 'target': v}
                edge_data.update(data)
                edges_data.append(edge_data)
            
            pd.DataFrame(edges_data).to_csv(f'{output_dir}/edges.csv', index=False)
        
        # 2. Export simulation history
        if self.history:
            history_df = pd.DataFrame(self.history)
            history_df.to_csv(f'{output_dir}/simulation_history.csv', index=False)
        
        # 3. Export layout positions
        if self.G and self.layout_cache:
            for layout_name, pos in self.layout_cache.items():
                pos_df = pd.DataFrame.from_dict(pos, orient='index')
                pos_df.columns = ['x', 'y', 'z'] if pos_df.shape[1] == 3 else ['x', 'y']
                pos_df.to_csv(f'{output_dir}/layout_{layout_name}.csv')
        
        # 4. Export configuration
        config_data = {
            'config': self.config,
            'color_palettes': self.color_palettes
        }
        
        with open(f'{output_dir}/config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ All data exported to {output_dir}/")
    
    def generate_report(self, output_file='visualization_report.html'):
        """Generate HTML report with all visualizations"""
        print("📋 Generating visualization report...")
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pandemic Simulation Visualization Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
                .section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                          box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .plot-container { margin: 20px 0; text-align: center; }
                img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                            gap: 15px; margin: 20px 0; }
                .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
                .stat-value { font-size: 24px; font-weight: bold; color: #667eea; }
                .stat-label { font-size: 14px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Pandemic Simulation Visualization Report</h1>
                <p>Comprehensive analysis of disease spread in social networks</p>
            </div>
        """
        
        # Add statistics
        if self.simulator:
            stats = self.simulator.get_summary_stats()
            html_content += """
            <div class="section">
                <h2>📊 Simulation Summary</h2>
                <div class="stats-grid">
            """
            
            for key, value in stats.items():
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                
                html_content += f"""
                    <div class="stat-card">
                        <div class="stat-value">{display_value}</div>
                        <div class="stat-label">{key.replace('_', ' ').title()}</div>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
            """
        
        # Add network information
        if self.G:
            html_content += f"""
            <div class="section">
                <h2>🔗 Network Information</h2>
                <p><strong>Nodes:</strong> {self.G.number_of_nodes()}</p>
                <p><strong>Edges:</strong> {self.G.number_of_edges()}</p>
                <p><strong>Average Degree:</strong> {np.mean([d for _, d in self.G.degree()]):.2f}</p>
                <p><strong>Clustering Coefficient:</strong> {nx.average_clustering(self.G):.3f}</p>
            </div>
            """
        
        # Add visualization placeholders
        html_content += """
        <div class="section">
            <h2>🎨 Visualizations</h2>
            <div class="plot-container">
                <h3>3D Network Visualization</h3>
                <p>Interactive 3D plot showing disease spread</p>
                <div id="3d-plot"></div>
            </div>
            <div class="plot-container">
                <h3>Epidemic Curves</h3>
                <p>Time series of disease states</p>
                <img src="epidemic_curves.png" alt="Epidemic Curves">
            </div>
            <div class="plot-container">
                <h3>Network Metrics</h3>
                <p>Analysis of network structure</p>
                <img src="network_metrics.png" alt="Network Metrics">
            </div>
        </div>
        """
        
        # Add export section
        html_content += """
        <div class="section">
            <h2>📤 Data Export</h2>
            <p>The following data files have been exported:</p>
            <ul>
                <li><code>network.graphml</code> - Complete network structure</li>
                <li><code>nodes.csv</code> - Node attributes</li>
                <li><code>edges.csv</code> - Edge attributes</li>
                <li><code>simulation_history.csv</code> - Time series data</li>
                <li><code>config.json</code> - Visualization configuration</li>
            </ul>
        </div>
        
        <div class="section" style="text-align: center; color: #666;">
            <p>Generated by Pandemic Visualization System</p>
            <p>📅 """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
        
        </body>
        </html>
        """
        
        # Write HTML file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Report generated: {output_file}")
        return html_content

# ==================== QUICK START FUNCTIONS ====================

def visualize_simulation(simulator, output_dir='visualizations'):
    """
    Quick function to generate all visualizations for a simulation
    
    Args:
        simulator: UltimateSimulator instance
        output_dir: Output directory for visualizations
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Generating comprehensive visualizations...")
    
    # Create visualizer
    visualizer = PandemicVisualizer3D(simulator)
    
    # 1. Compute layout
    pos = visualizer.compute_force_directed_layout()
    
    # 2. Create 3D network plot for day 0
    fig_3d = visualizer.create_3d_network_plot(day=0, pos=pos)
    fig_3d.write_html(f'{output_dir}/3d_network.html')
    
    # 3. Create dashboard
    dashboard = visualizer.create_comprehensive_dashboard(
        output_file=f'{output_dir}/dashboard.html'
    )
    
    # 4. Create static plots
    visualizer.create_epidemic_curves_plot(
        output_file=f'{output_dir}/epidemic_curves.png'
    )
    
    visualizer.create_network_metrics_plot(
        output_file=f'{output_dir}/network_metrics.png'
    )
    
    # 5. Export data
    visualizer.export_visualization_data(output_dir=f'{output_dir}/data')
    
    # 6. Generate report
    visualizer.generate_report(output_file=f'{output_dir}/report.html')
    
    print(f"\n✅ All visualizations saved to {output_dir}/")
    print("   Files created:")
    print(f"   - {output_dir}/3d_network.html (Interactive 3D plot)")
    print(f"   - {output_dir}/dashboard.html (Comprehensive dashboard)")
    print(f"   - {output_dir}/epidemic_curves.png (Epidemic curves)")
    print(f"   - {output_dir}/network_metrics.png (Network analysis)")
    print(f"   - {output_dir}/report.html (HTML report)")
    print(f"   - {output_dir}/data/ (Exported data files)")

# ==================== TEST FUNCTION ====================

def test_visualization():
    """Test the visualization system"""
    print("🧪 Testing Visualization System...")
    
    # Create a test network
    from network_generator import UltimateNetworkGenerator
    from disease_models import DiseaseLibrary
    from simulator_engine import UltimateSimulator
    
    # Generate small test network
    generator = UltimateNetworkGenerator(population=200)
    G = generator.hybrid_multilayer()
    
    # Create simple simulator
    disease = DiseaseLibrary.covid19_variant("wildtype")
    simulator = UltimateSimulator(G, disease)
    
    # Seed infections and run short simulation
    simulator.seed_infections(n_infections=5)
    simulator.run(days=30, show_progress=False)
    
    # Test visualizer
    visualizer = PandemicVisualizer3D(simulator)
    
    # Create 3D plot
    print("\n1. Creating 3D network plot...")
    fig = visualizer.create_3d_network_plot(day=15)
    fig.write_html('test_3d_plot.html')
    
    # Create static plots
    print("\n2. Creating static plots...")
    visualizer.create_epidemic_curves_plot('test_epidemic_curves.png')
    visualizer.create_network_metrics_plot('test_network_metrics.png')
    
    print("\n✅ Visualization test complete!")
    print("   Files created:")
    print("   - test_3d_plot.html")
    print("   - test_epidemic_curves.png")
    print("   - test_network_metrics.png")

if __name__ == "__main__":
    test_visualization()