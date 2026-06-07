# animation_simulator.py - UPDATED VERSION
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.colors import qualitative
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.cm as cm
import pandas as pd
from typing import Dict, List, Tuple, Optional
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Conditional Streamlit import
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create dummy st module
    class DummySt:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    st = DummySt()
    st.session_state = type('obj', (object,), {'__dict__': {}})()

class LiveAnimationSimulator:
    """
    Real-time animated simulation with video-like visualization
    Shows disease spreading through network frame by frame
    """
    
    def __init__(self, simulator=None):
        self.simulator = simulator
        self.animation_frames = []
        self.current_frame = 0
        self.is_playing = False
        self.speed = 1.0  # Playback speed multiplier
        
        # Color schemes
        self.state_colors = {
            'S': '#4CAF50',  # Green - Susceptible
            'E': '#FF9800',  # Orange - Exposed
            'I': '#F44336',  # Red - Infectious
            'Ia': '#FF5252', # Light red - Asymptomatic
            'Im': '#D32F2F', # Dark red - Mild
            'Is': '#B71C1C', # Darker red - Severe
            'Ih': '#7B1FA2', # Purple - Hospitalized
            'Ic': '#212121', # Black - Critical
            'R': '#2196F3',  # Blue - Recovered
            'D': '#757575',  # Gray - Deceased
            'V': '#9C27B0'   # Purple - Vaccinated
        }
        
        # Layout cache
        self.node_positions = None
        self.layout_method = 'spring'
        
        # Store checkpoints if available
        self.checkpoints = getattr(simulator, 'checkpoints', {}) if simulator else {}
        
        print("🎬 Live Animation Simulator Initialized")
    
    def prepare_animation(self, days_to_animate=None, step_size=1):
        """
        Prepare animation frames from simulation history
        
        Args:
            days_to_animate: Range of days to animate (default: all)
            step_size: Number of days between frames
        """
        if self.simulator is None or not hasattr(self.simulator, 'history'):
            print("⚠️ No simulation data available")
            return
        
        history = self.simulator.history
        
        if days_to_animate is None:
            days_to_animate = range(0, len(history['time']), step_size)
        
        print(f"🎞️ Preparing {len(days_to_animate)} animation frames...")
        
        # Compute node positions once (for consistency)
        if self.node_positions is None:
            self.node_positions = self._compute_layout()
        
        # Create frames
        self.animation_frames = []
        
        for day in days_to_animate:
            frame = self._create_frame(day)
            if frame:
                self.animation_frames.append(frame)
        
        print(f"✅ Prepared {len(self.animation_frames)} animation frames")
    
    def _compute_layout(self):
        """Compute consistent node layout for animation"""
        if self.simulator is None:
            return None
        
        G = self.simulator.G
        
        print("📐 Computing network layout for animation...")
        
        if self.layout_method == 'spring':
            # Force-directed layout
            pos = nx.spring_layout(
                G, 
                dim=2, 
                seed=42,
                k=1.5/np.sqrt(len(G.nodes())),  # Increased k for better spacing
                iterations=200  # More iterations for better layout
            )
        elif self.layout_method == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        elif self.layout_method == 'circular':
            pos = nx.circular_layout(G)
        elif self.layout_method == 'shell':
            pos = nx.shell_layout(G)
        else:
            pos = nx.spring_layout(G, seed=42, iterations=200)
        
        return pos
    
    def _create_frame(self, day):
        """Create a single animation frame for specific day"""
        if self.simulator is None:
            return None
        
        # Create frame data
        frame_data = {
            'day': day,
            'timestamp': f"Day {day}",
            'node_states': {},
            'node_colors': [],
            'node_sizes': [],
            'statistics': {},
            'infection_paths': []
        }
        
        # Get node states for this day
        node_states = self._get_node_states_for_day(day)
        
        if not node_states:
            print(f"⚠️ Could not get node states for day {day}")
            return None
        
        # Collect node states and colors
        G = self.simulator.G
        
        for node in G.nodes():
            state = node_states.get(node, 'S')
            frame_data['node_states'][node] = state
            frame_data['node_colors'].append(self.state_colors.get(state, '#CCCCCC'))
            
            # Adjust node size based on state
            if state == 'I' or state.startswith('I'):
                size = 20  # Infectious nodes are larger
            elif state == 'E':
                size = 16  # Exposed nodes medium
            elif state == 'R':
                size = 12  # Recovered medium
            elif state == 'D':
                size = 10  # Deceased smaller
            elif state == 'V':
                size = 14  # Vaccinated medium
            else:
                size = 10  # Susceptible smaller
            
            frame_data['node_sizes'].append(size)
        
        # Get statistics for this day
        if hasattr(self.simulator, 'history'):
            history = self.simulator.history
            if day < len(history['time']):
                frame_data['statistics'] = {
                    'S': history['S'][day],
                    'E': history['E'][day] if 'E' in history else 0,
                    'I': history['I'][day],
                    'R': history['R'][day],
                    'D': history['D'][day] if 'D' in history else 0,
                    'V': history['V'][day] if 'V' in history else 0,
                    'new_cases': history['new_infections'][day] if 'new_infections' in history else 0
                }
        
        return frame_data
    
    def _get_node_states_for_day(self, day):
        """
        Get node states for a specific day
        Try multiple methods to get accurate states
        """
        # Method 1: Use checkpoints if available
        if day in self.checkpoints:
            return self.checkpoints[day]['node_states']
        
        # Method 2: Infer from history
        if hasattr(self.simulator, 'history'):
            return self._infer_states_from_history(day)
        
        # Method 3: Fallback - all nodes as susceptible
        return {node: 'S' for node in self.simulator.G.nodes()}
    
    def _infer_states_from_history(self, day):
        """
        Infer node states from simulation history
        This is a simplified method - in reality you'd need better tracking
        """
        if not hasattr(self.simulator, 'history'):
            return {}
        
        history = self.simulator.history
        
        # Get total counts for each state
        S_count = history['S'][day] if day < len(history['S']) else 0
        I_count = history['I'][day] if day < len(history['I']) else 0
        R_count = history['R'][day] if day < len(history['R']) else 0
        D_count = history['D'][day] if day < len(history['D']) else 0
        
        # This is a simplified approach - in reality you'd track individual nodes
        # For demonstration, we'll create a synthetic distribution
        nodes = list(self.simulator.G.nodes())
        n_nodes = len(nodes)
        
        node_states = {}
        
        # Assign states based on proportions
        idx = 0
        
        # Assign infectious
        for i in range(min(I_count, n_nodes - idx)):
            node_states[nodes[idx]] = 'I'
            idx += 1
        
        # Assign recovered
        for i in range(min(R_count, n_nodes - idx)):
            node_states[nodes[idx]] = 'R'
            idx += 1
        
        # Assign deceased
        for i in range(min(D_count, n_nodes - idx)):
            node_states[nodes[idx]] = 'D'
            idx += 1
        
        # Assign susceptible to rest
        for i in range(idx, n_nodes):
            node_states[nodes[i]] = 'S'
        
        return node_states
    
    def create_interactive_animation(self, output_file='animated_simulation.html'):
        """Create interactive HTML animation with Play/Pause controls"""
        if not self.animation_frames:
            print("⚠️ No animation frames prepared")
            return
        
        print("🎬 Creating interactive animation...")
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{'type': 'xy', 'rowspan': 2}, {'type': 'xy'}],
                [None, {'type': 'xy'}]
            ],
            subplot_titles=(
                'Disease Spread Animation',
                'Epidemic Curve',
                'Daily New Cases'
            ),
            vertical_spacing=0.1,
            horizontal_spacing=0.15
        )
        
        # Get layout positions
        pos = self.node_positions
        
        if pos is None:
            print("⚠️ No node positions computed")
            return
        
        # Prepare node positions for all frames
        node_x, node_y = [], []
        for node in self.simulator.G.nodes():
            if node in pos:
                node_x.append(pos[node][0])
                node_y.append(pos[node][1])
            else:
                node_x.append(0)
                node_y.append(0)
        
        # Create initial frame
        frame0 = self.animation_frames[0]
        
        # Add network plot
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers',
                marker=dict(
                    size=frame0['node_sizes'],
                    color=frame0['node_colors'],
                    line=dict(width=1, color='darkgray')
                ),
                name='Network',
                text=[f"Node {i}<br>State: {frame0['node_states'].get(i, 'S')}" 
                      for i in range(len(node_x))],
                hoverinfo='text'
            ),
            row=1, col=1
        )
        
        # Add edges (static)
        edge_x, edge_y = [], []
        for u, v in self.simulator.G.edges():
            if u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        if edge_x:  # Only add if we have edges
            fig.add_trace(
                go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    mode='lines',
                    line=dict(width=0.5, color='rgba(150,150,150,0.3)'),
                    hoverinfo='none',
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Add epidemic curve (initialize)
        days = [f['day'] for f in self.animation_frames]
        S_values = [f['statistics'].get('S', 0) for f in self.animation_frames]
        I_values = [f['statistics'].get('I', 0) for f in self.animation_frames]
        R_values = [f['statistics'].get('R', 0) for f in self.animation_frames]
        
        fig.add_trace(
            go.Scatter(x=[days[0]], y=[S_values[0]], 
                      mode='lines', name='Susceptible',
                      line=dict(color=self.state_colors['S'], width=3)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=[days[0]], y=[I_values[0]], 
                      mode='lines', name='Infectious',
                      line=dict(color=self.state_colors['I'], width=3)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=[days[0]], y=[R_values[0]], 
                      mode='lines', name='Recovered',
                      line=dict(color=self.state_colors['R'], width=3)),
            row=1, col=2
        )
        
        # Add daily new cases (initialize)
        new_cases = [f['statistics'].get('new_cases', 0) for f in self.animation_frames]
        fig.add_trace(
            go.Bar(x=[days[0]], y=[new_cases[0]], 
                  name='New Cases',
                  marker_color='red',
                  opacity=0.7),
            row=2, col=2
        )
        
        # Create frames for animation
        frames = []
        for i, frame in enumerate(self.animation_frames):
            # Network frame
            network_frame = go.Frame(
                data=[
                    go.Scatter(
                        x=node_x,
                        y=node_y,
                        marker=dict(
                            size=frame['node_sizes'],
                            color=frame['node_colors']
                        )
                    ),
                    # Epidemic curves up to this point
                    go.Scatter(x=days[:i+1], y=S_values[:i+1]),
                    go.Scatter(x=days[:i+1], y=I_values[:i+1]),
                    go.Scatter(x=days[:i+1], y=R_values[:i+1]),
                    # Daily new cases up to this point
                    go.Bar(x=days[:i+1], y=new_cases[:i+1])
                ],
                name=f"Day {frame['day']}"
            )
            frames.append(network_frame)
        
        fig.frames = frames
        
        # Add slider and play button
        sliders = [dict(
            steps=[
                dict(
                    method='animate',
                    args=[
                        [f"Day {self.animation_frames[i]['day']}"],
                        dict(
                            mode='immediate',
                            frame=dict(duration=300, redraw=True),
                            transition=dict(duration=100)
                        )
                    ],
                    label=f"Day {self.animation_frames[i]['day']}"
                )
                for i in range(len(self.animation_frames))
            ],
            active=0,
            transition=dict(duration=100),
            x=0.1, y=0,
            len=0.8,
            currentvalue=dict(
                font=dict(size=14),
                prefix='Day: ',
                visible=True,
                xanchor='center'
            ),
            pad=dict(t=50, b=10)
        )]
        
        # Add play/pause buttons
        updatemenus = [dict(
            type='buttons',
            showactive=False,
            y=-0.1,
            x=0.1,
            xanchor='right',
            yanchor='top',
            pad=dict(t=0, r=10),
            buttons=[
                dict(
                    label='▶️ Play',
                    method='animate',
                    args=[
                        None,
                        dict(
                            frame=dict(duration=200, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=100)
                        )
                    ]
                ),
                dict(
                    label='⏸️ Pause',
                    method='animate',
                    args=[
                        [None],
                        dict(
                            mode='immediate',
                            transition=dict(duration=0)
                        )
                    ]
                ),
                dict(
                    label='⏭️ Next',
                    method='animate',
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0, redraw=True),
                            mode='next'
                        )
                    ]
                ),
                dict(
                    label='⏮️ Previous',
                    method='animate',
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0, redraw=True),
                            mode='previous'
                        )
                    ]
                )
            ]
        )]
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='Live Pandemic Simulation Animation',
                font=dict(size=20)
            ),
            height=800,
            showlegend=True,
            updatemenus=updatemenus,
            sliders=sliders
        )
        
        # Update subplot titles and axes
        fig.update_xaxes(title_text="X", row=1, col=1)
        fig.update_yaxes(title_text="Y", row=1, col=1)
        fig.update_xaxes(title_text="Day", row=1, col=2)
        fig.update_yaxes(title_text="Individuals", row=1, col=2)
        fig.update_xaxes(title_text="Day", row=2, col=2)
        fig.update_yaxes(title_text="New Cases", row=2, col=2)
        
        # Save animation
        fig.write_html(output_file)
        print(f"✅ Interactive animation saved to {output_file}")
        
        return fig
    
    def create_video_animation(self, output_file='simulation_video.gif', fps=10):
        """Create GIF/MP4 video animation"""
        if not self.animation_frames:
            print("⚠️ No animation frames prepared")
            return
        
        print("🎥 Creating video animation...")
        
        # Create matplotlib animation
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Get layout
        pos = self.node_positions
        
        def update(frame_idx):
            ax1.clear()
            ax2.clear()
            
            frame = self.animation_frames[frame_idx]
            day = frame['day']
            
            # Plot network
            G = self.simulator.G
            
            # Draw nodes
            node_colors = frame['node_colors']
            node_sizes = frame['node_sizes']
            
            if pos:
                # Extract coordinates
                x_vals = [pos[node][0] for node in G.nodes() if node in pos]
                y_vals = [pos[node][1] for node in G.nodes() if node in pos]
                
                if x_vals and y_vals:
                    # Plot nodes
                    ax1.scatter(x_vals, y_vals, 
                              c=node_colors, 
                              s=node_sizes,
                              alpha=0.8,
                              edgecolors='gray',
                              linewidths=0.5)
            
            ax1.set_title(f'Day {day} - Disease Spread')
            ax1.axis('off')
            
            # Plot epidemic curve up to this day
            days = [f['day'] for f in self.animation_frames[:frame_idx+1]]
            S_vals = [f['statistics'].get('S', 0) for f in self.animation_frames[:frame_idx+1]]
            I_vals = [f['statistics'].get('I', 0) for f in self.animation_frames[:frame_idx+1]]
            R_vals = [f['statistics'].get('R', 0) for f in self.animation_frames[:frame_idx+1]]
            
            ax2.plot(days, S_vals, 'g-', label='Susceptible', linewidth=2)
            ax2.plot(days, I_vals, 'r-', label='Infectious', linewidth=2)
            ax2.plot(days, R_vals, 'b-', label='Recovered', linewidth=2)
            
            ax2.set_xlabel('Days')
            ax2.set_ylabel('Individuals')
            ax2.set_title('Epidemic Progression')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Add day counter
            fig.suptitle(f'Pandemic Simulation - Day {day}', fontsize=16, fontweight='bold')
        
        # Create animation
        anim = FuncAnimation(fig, update, 
                           frames=len(self.animation_frames),
                           interval=1000/fps,  # milliseconds per frame
                           repeat=False)
        
        # Save as GIF
        try:
            writer = PillowWriter(fps=fps)
            anim.save(output_file, writer=writer, dpi=100)
            print(f"✅ Video animation saved to {output_file}")
        except Exception as e:
            print(f"⚠️ Could not save video: {e}")
            print("   Try installing pillow: pip install pillow")
        
        plt.close()
        
        return anim
    
    def streamlit_live_animation(self):
        """Streamlit component for live animation"""
        if not STREAMLIT_AVAILABLE:
            print("⚠️ Streamlit not available")
            return
        
        if not self.animation_frames:
            st.warning("No animation frames prepared")
            return
        
        st.markdown("## 🎬 Live Simulation Animation")
        
        # Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            play = st.button("▶️ Play Animation", type="primary")
        
        with col2:
            pause = st.button("⏸️ Pause")
        
        with col3:
            speed = st.slider("Animation Speed", 0.25, 4.0, 1.0, 0.25)
        
        # Day slider
        current_day = st.slider(
            "Select Day",
            0,
            len(self.animation_frames) - 1,
            0,
            key="animation_day"
        )
        
        # Display current frame
        frame = self.animation_frames[current_day]
        
        # Create visualization
        self._display_frame_in_streamlit(frame, current_day)
        
        # Auto-play if requested
        if play:
            self._streamlit_auto_play()
    
    def _display_frame_in_streamlit(self, frame, day):
        """Display a single frame in Streamlit"""
        if not STREAMLIT_AVAILABLE:
            return
        
        # Create columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Network visualization
            st.markdown(f"### Network - Day {day}")
            
            # Create simple network plot
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if self.node_positions:
                G = self.simulator.G
                pos = self.node_positions
                
                # Draw edges
                nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
                
                # Draw nodes with colors
                node_colors = frame['node_colors']
                
                # Group nodes by color for efficient drawing
                color_groups = {}
                for i, node in enumerate(G.nodes()):
                    color = node_colors[i]
                    if color not in color_groups:
                        color_groups[color] = []
                    color_groups[color].append(node)
                
                for color, nodes in color_groups.items():
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                          node_color=color,
                                          node_size=50,
                                          ax=ax)
                
                ax.set_title(f"Day {day} - {len(G.nodes())} individuals")
                ax.axis('off')
                
                st.pyplot(fig)
        
        with col2:
            # Statistics
            st.markdown("### 📊 Statistics")
            
            stats = frame['statistics']
            
            # Key metrics
            metric_cols = st.columns(2)
            
            with metric_cols[0]:
                st.metric("Susceptible", stats.get('S', 0))
                st.metric("Infectious", stats.get('I', 0))
            
            with metric_cols[1]:
                st.metric("Recovered", stats.get('R', 0))
                st.metric("New Cases", stats.get('new_cases', 0))
            
            # State distribution pie chart
            state_counts = {}
            for state in frame['node_states'].values():
                state_counts[state] = state_counts.get(state, 0) + 1
            
            if state_counts:
                states = list(state_counts.keys())
                counts = list(state_counts.values())
                
                fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
                
                # Map state names to readable labels
                state_labels = {
                    'S': 'Susceptible',
                    'E': 'Exposed',
                    'I': 'Infectious',
                    'R': 'Recovered',
                    'D': 'Deceased',
                    'V': 'Vaccinated'
                }
                
                labels = [state_labels.get(s, s) for s in states]
                colors = [self.state_colors.get(s, '#CCCCCC') for s in states]
                
                ax_pie.pie(counts, labels=labels, colors=colors,
                          autopct='%1.1f%%', startangle=90)
                ax_pie.axis('equal')
                ax_pie.set_title("Population State Distribution")
                
                st.pyplot(fig_pie)
    
    def _streamlit_auto_play(self):
        """Auto-play animation in Streamlit"""
        if not STREAMLIT_AVAILABLE:
            return
        
        placeholder = st.empty()
        
        for i in range(len(self.animation_frames)):
            frame = self.animation_frames[i]
            
            # Update display
            with placeholder.container():
                self._display_frame_in_streamlit(frame, i)
            
            # Wait for next frame
            time.sleep(0.5 / self.speed)  # Adjust speed
    
    def export_animation_frames(self, output_dir="animation_frames"):
        """Export all animation frames as individual images"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📸 Exporting {len(self.animation_frames)} frames to {output_dir}/...")
        
        for i, frame in enumerate(self.animation_frames):
            # Create plot for this frame
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if self.node_positions:
                G = self.simulator.G
                pos = self.node_positions
                
                # Draw network
                node_colors = frame['node_colors']
                
                # Draw edges
                nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
                
                # Draw nodes
                nx.draw_networkx_nodes(G, pos, 
                                      node_color=node_colors,
                                      node_size=50,
                                      ax=ax)
                
                # Add title with statistics
                stats = frame['statistics']
                title = (f"Day {frame['day']} | "
                        f"S: {stats.get('S', 0)} | "
                        f"I: {stats.get('I', 0)} | "
                        f"R: {stats.get('R', 0)}")
                ax.set_title(title, fontsize=14)
                ax.axis('off')
            
            # Save frame
            frame_file = f"{output_dir}/frame_{i:04d}_day_{frame['day']}.png"
            plt.savefig(frame_file, dpi=100, bbox_inches='tight')
            plt.close()
        
        print(f"✅ Frames exported to {output_dir}/")
        
        # Create a video from frames (optional)
        self._create_video_from_frames(output_dir)
    
    def _create_video_from_frames(self, frames_dir):
        """Create video from exported frames (requires ffmpeg)"""
        try:
            import subprocess
            import os
            
            # Check if ffmpeg is available
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("🎥 Creating video from frames...")
                
                output_file = f"{frames_dir}/simulation_video.mp4"
                
                # FFmpeg command to create video
                cmd = [
                    'ffmpeg',
                    '-framerate', '10',  # 10 frames per second
                    '-pattern_type', 'glob',
                    '-i', f'{frames_dir}/frame_*.png',
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-vf', 'scale=1920:1080',  # HD resolution
                    output_file
                ]
                
                subprocess.run(cmd, check=True)
                print(f"✅ Video created: {output_file}")
            else:
                print("⚠️ FFmpeg not found. Install with: sudo apt-get install ffmpeg")
                
        except Exception as e:
            print(f"⚠️ Could not create video: {e}")

# ==================== TEST FUNCTION ====================

def create_live_demo():
    """Create a live demo animation"""
    print("🚀 Creating live animation demo...")
    
    # Check if we have a simulator
    try:
        from simulator_engine import UltimateSimulator
        from network_generator import UltimateNetworkGenerator
        from disease_models import DiseaseLibrary
        
        # Create small demo network
        print("Generating network...")
        generator = UltimateNetworkGenerator(population=200)
        G = generator.hybrid_multilayer()
        
        # Create disease
        print("Loading disease model...")
        disease = DiseaseLibrary.covid19_variant("omicron")
        
        # Create and run simulator WITH CHECKPOINTS
        print("Creating simulator...")
        simulator = UltimateSimulator(G, disease)
        simulator.seed_infections(5, method='random')
        
        # Run simulation with checkpoints
        print("Running simulation...")
        if hasattr(simulator, 'run_with_animation'):
            history, checkpoints = simulator.run_with_animation(
                days=60, 
                show_progress=True,
                save_checkpoints=True,
                checkpoint_interval=2
            )
            simulator.checkpoints = checkpoints
        else:
            simulator.run(days=60, show_progress=True)
        
        # Create animator
        print("Creating animator...")
        animator = LiveAnimationSimulator(simulator)
        
        # Prepare animation every 2 days
        days_to_animate = range(0, 61, 2)
        print(f"Preparing animation for {len(days_to_animate)} days...")
        animator.prepare_animation(days_to_animate=days_to_animate)
        
        # Create interactive animation
        print("Creating interactive HTML animation...")
        animator.create_interactive_animation("live_demo_animation.html")
        
        # Create video (if possible)
        try:
            print("Creating GIF animation...")
            animator.create_video_animation("live_demo.gif", fps=10)
            print("✅ GIF created successfully!")
        except Exception as e:
            print(f"⚠️ Could not create GIF: {e}")
        
        print("✅ Demo created successfully!")
        
        # Print color distribution
        if animator.animation_frames:
            print("\n🎨 Color Distribution in Animation:")
            for i, frame in enumerate(animator.animation_frames[::10]):  # Every 10th frame
                colors = frame['node_colors']
                color_counts = {}
                for color in colors:
                    color_counts[color] = color_counts.get(color, 0) + 1
                
                print(f"  Day {frame['day']}: {color_counts}")
        
        return animator
        
    except ImportError as e:
        print(f"⚠️ Could not import modules: {e}")
        print("   Please ensure all project files are available")
        return None
    except Exception as e:
        print(f"⚠️ Error creating demo: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run demo
    print("=" * 60)
    print("🎬 ANIMATION SIMULATOR TEST")
    print("=" * 60)
    
    animator = create_live_demo()
    
    if animator:
        print("\n📁 Files created:")
        print("   - live_demo_animation.html (Interactive animation)")
        print("   - live_demo.gif (Video animation, if Pillow is installed)")
        print("\n🎯 Open live_demo_animation.html in your browser to watch!")
        print("=" * 60)