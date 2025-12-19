# main_dashboard.py - FIXED VERSION
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
import json
import pickle
import os
from datetime import datetime
import sys
import warnings
import time
import base64
from io import BytesIO
import tempfile
from pathlib import Path
from PIL import Image
import io

warnings.filterwarnings('ignore')

# Add project modules to path
sys.path.append('.')

# Import project modules
try:
    from network_generator import UltimateNetworkGenerator
    from disease_models import DiseaseLibrary, DiseaseParameters, InterventionSchedule
    from simulator_engine import UltimateSimulator
    from animation_simulator import LiveAnimationSimulator
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some modules not available: {e}")
    MODULES_AVAILABLE = False

class PandemicDashboard:
    """
    Complete interactive dashboard for pandemic simulation
    Streamlit-based with real-time controls and visualization
    """
    
    def __init__(self):
        """Initialize the dashboard"""
        st.set_page_config(
            page_title="Pandemic Simulation Dashboard",
            page_icon="🦠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        self._init_session_state()
        
        # Set custom CSS
        self._set_custom_css()
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        default_state = {
            'simulator': None,
            'simulation_history': None,
            'visualizer': None,
            'animator': None,
            'current_day': 0,
            'simulation_running': False,
            'parameter_sweeper': None,
            'sweep_results': None,
            'animation_ready': False,
            'animation_frames': [],
            'network_params': {},
            'disease_params': {},
            'simulation_params': {},
            'example_network': None,
            'example_disease': None,
            'export_data': None,
            'node_positions': None,
            'network_graph': None,
            'disease_spread_data': [],
            'intervention_history': [],
            'checkpoints': {},
            'simulation_complete': False
        }
        
        for key, value in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _set_custom_css(self):
        """Set custom CSS for the dashboard"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        
        .sub-header {
            font-size: 1.5rem;
            color: #424242;
            margin-top: 1rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .network-canvas {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .animation-frame {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        }
        
        .state-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 10px 0;
        }
        
        .state-item {
            display: flex;
            align-items: center;
            margin-right: 15px;
        }
        
        .state-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .node-s {
            background-color: #4CAF50;
        }
        
        .node-e {
            background-color: #FF9800;
        }
        
        .node-i {
            background-color: #F44336;
        }
        
        .node-r {
            background-color: #2196F3;
        }
        
        .node-d {
            background-color: #757575;
        }
        
        .node-v {
            background-color: #9C27B0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main method to run the dashboard"""
        # Title and header
        st.markdown('<h1 class="main-header">🦠 Pandemic Simulation Dashboard</h1>', 
                   unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
        Interactive simulation and visualization of disease spread in social networks
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs
        tabs = st.tabs([
            "🏠 Overview",
            "⚙️ Simulation",
            "📊 Analysis",
            "🎨 Visualization",
            "🎬 Animation",
            "📈 Results"
        ])
        
        with tabs[0]:
            self._render_overview_tab()
        
        with tabs[1]:
            self._render_simulation_tab()
        
        with tabs[2]:
            self._render_analysis_tab()
        
        with tabs[3]:
            self._render_visualization_tab()
        
        with tabs[4]:
            self._render_animation_tab()
        
        with tabs[5]:
            self._render_results_tab()
    
    # ==================== TAB 1: OVERVIEW ====================
    
    def _render_overview_tab(self):
        """Render the overview tab"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown('<h2 class="sub-header">Welcome to the Pandemic Simulator</h2>', 
                       unsafe_allow_html=True)
            
            st.markdown("""
            This interactive dashboard allows you to simulate disease spread in social networks.
            
            ### 🔑 Key Features:
            
            **🎯 Network Animation**
            - Watch disease spread through the network in real-time
            - Color-coded nodes show infection status
            - Animated edges show transmission paths
            
            **🌐 Network Generation**
            - Create realistic social networks with various structures
            - Control population size, connection patterns, and demographics
            
            **🦠 Disease Modeling**
            - Simulate COVID-19 variants (Wildtype, Alpha, Delta, Omicron)
            - Customize transmission parameters
            
            **🛡️ Intervention Strategies**
            - Test different intervention scenarios
            - Adjust timing and efficacy of measures
            
            **📊 Advanced Visualization**
            - 3D interactive network visualization
            - Real-time simulation animation
            - Video export (GIF/MP4) of simulations
            """)
            
            # Show animation preview if available
            if st.session_state.animation_ready and st.session_state.animation_frames:
                st.markdown("### 🎬 Current Animation Preview")
                if len(st.session_state.animation_frames) > 1:
                    preview_day = st.slider("Preview Day", 0, len(st.session_state.animation_frames)-1, 0)
                    self._display_animation_frame(preview_day)
                else:
                    self._display_animation_frame(0)
        
        with col2:
            st.markdown('<h3 class="sub-header">📈 Quick Stats</h3>', 
                       unsafe_allow_html=True)
            
            # Example metrics
            metrics_data = {}
            
            if st.session_state.simulator:
                try:
                    stats = st.session_state.simulator.get_summary_stats()
                    metrics_data = {
                        "Simulations Run": "1",
                        "Attack Rate": f"{stats.get('attack_rate', 0)*100:.1f}%",
                        "Peak Infections": f"{stats.get('peak_infections', 0):.0f}",
                        "Total Deaths": f"{stats.get('total_deaths', 0):.0f}"
                    }
                except:
                    metrics_data = {
                        "Simulations Run": "1",
                        "Average R0": "2.5",
                        "Peak Infections": "0",
                        "Attack Rate": "0%"
                    }
            else:
                metrics_data = {
                    "Simulations Run": "0",
                    "Average R0": "2.5",
                    "Peak Infections": "0",
                    "Attack Rate": "0%"
                }
            
            for label, value in metrics_data.items():
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
        
        with col3:
            st.markdown('<h3 class="sub-header">🚀 Quick Start</h3>', 
                       unsafe_allow_html=True)
            
            if st.button("▶️ Run Example Simulation", type="primary", use_container_width=True):
                self._run_example_simulation()
            
            if st.session_state.simulator and not st.session_state.animation_ready and st.session_state.simulation_history:
                if st.button("🎬 Prepare Animation", use_container_width=True):
                    self._prepare_animation()
            
            # State legend
            st.markdown("### 🎨 State Colors")
            st.markdown("""
            <div class="state-legend">
                <div class="state-item"><div class="state-color node-s"></div>Susceptible</div>
                <div class="state-item"><div class="state-color node-e"></div>Exposed</div>
                <div class="state-item"><div class="state-color node-i"></div>Infectious</div>
                <div class="state-item"><div class="state-color node-r"></div>Recovered</div>
                <div class="state-item"><div class="state-color node-d"></div>Deceased</div>
                <div class="state-item"><div class="state-color node-v"></div>Vaccinated</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent simulations
        if st.session_state.simulation_history is not None:
            st.markdown("---")
            st.markdown('<h3 class="sub-header">📋 Recent Simulation</h3>', 
                       unsafe_allow_html=True)
            
            cols = st.columns(5)
            
            try:
                stats = st.session_state.simulator.get_summary_stats()
                
                metric_keys = ['attack_rate', 'peak_infections', 'total_deaths', 'case_fatality_rate', 'total_vaccinated']
                metric_labels = ['Attack Rate', 'Peak Infections', 'Total Deaths', 'Fatality Rate', 'Vaccinated']
                
                for i, (key, label) in enumerate(zip(metric_keys, metric_labels)):
                    with cols[i]:
                        value = stats.get(key, 0)
                        if isinstance(value, float):
                            display_value = f"{value:.2%}" if 'rate' in key else f"{value:.0f}"
                        else:
                            display_value = str(value)
                        
                        st.metric(label=label, value=display_value)
                
                # Animation status
                with cols[4]:
                    if st.session_state.animation_ready:
                        st.metric("Animation", "✅ Ready", delta="Prepared")
                    else:
                        st.metric("Animation", "⏳ Not Ready")
            except:
                pass
    
    # ==================== TAB 2: SIMULATION ====================
    
    def _render_simulation_tab(self):
        """Render the simulation configuration tab"""
        st.markdown('<h2 class="sub-header">⚙️ Simulation Configuration</h2>', 
                   unsafe_allow_html=True)
        
        if not MODULES_AVAILABLE:
            st.error("⚠️ Required modules not available. Please check your imports.")
            st.info("Running in demonstration mode with mock data.")
        
        # Create configuration form
        with st.form("simulation_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🌐 Network Configuration")
                
                population = st.slider(
                    "Population Size",
                    min_value=100,
                    max_value=5000,
                    value=1000,
                    step=100,
                    help="Total number of individuals in the network"
                )
                
                network_type = st.selectbox(
                    "Network Type",
                    ["hybrid", "erdos_renyi", "watts_strogatz", "barabasi_albert", "stochastic_block"],
                    index=0,
                    help="Type of network structure"
                )
                
                # Network-specific parameters
                network_params = {}
                if network_type == "erdos_renyi":
                    network_params['erdos_p'] = st.slider(
                        "Connection Probability",
                        min_value=0.001,
                        max_value=0.1,
                        value=0.01,
                        step=0.001,
                        format="%.3f"
                    )
                elif network_type == "watts_strogatz":
                    network_params['watts_k'] = st.slider(
                        "Nearest Neighbors",
                        min_value=2,
                        max_value=20,
                        value=8,
                        step=1
                    )
                    network_params['watts_p'] = st.slider(
                        "Rewiring Probability",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.3,
                        step=0.05
                    )
                elif network_type == "barabasi_albert":
                    network_params['barabasi_m'] = st.slider(
                        "New Node Connections",
                        min_value=1,
                        max_value=10,
                        value=3,
                        step=1
                    )
                elif network_type == "stochastic_block":
                    network_params['block_intra'] = st.slider(
                        "Within-Community Probability",
                        min_value=0.01,
                        max_value=0.5,
                        value=0.15,
                        step=0.01
                    )
                    network_params['block_inter'] = st.slider(
                        "Between-Community Probability",
                        min_value=0.001,
                        max_value=0.05,
                        value=0.01,
                        step=0.001
                    )
            
            with col2:
                st.markdown("### 🦠 Disease Configuration")
                
                disease_variant = st.selectbox(
                    "Disease Variant",
                    ["omicron", "delta", "alpha", "wildtype", "custom"],
                    index=0,
                    help="COVID-19 variant to simulate"
                )
                
                if disease_variant == "custom":
                    st.markdown("#### Custom Disease Parameters")
                    
                    custom_params = {}
                    custom_params['R0'] = st.slider(
                        "Basic Reproduction Number (R0)",
                        min_value=1.0,
                        max_value=10.0,
                        value=2.5,
                        step=0.1
                    )
                    
                    custom_params['incubation_period'] = {
                        'mean': st.slider(
                            "Incubation Period (mean days)",
                            min_value=1,
                            max_value=14,
                            value=5,
                            step=1
                        ),
                        'std': st.slider(
                            "Incubation Period (std days)",
                            min_value=0,
                            max_value=7,
                            value=2,
                            step=0.5
                        )
                    }
                    
                    custom_params['mortality_rate'] = st.slider(
                        "Mortality Rate",
                        min_value=0.001,
                        max_value=0.1,
                        value=0.01,
                        step=0.001,
                        format="%.3f"
                    )
                else:
                    custom_params = {}
                
                n_seed_infections = st.slider(
                    "Initial Infections",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1,
                    help="Number of initially infected individuals"
                )
                
                seed_method = st.selectbox(
                    "Infection Seeding Method",
                    ["random", "hubs", "mobile", "geographic", "age_targeted"],
                    index=0,
                    help="How to select initial infections"
                )
            
            # Simulation settings
            st.markdown("---")
            st.markdown("### ⚡ Simulation Settings")
            
            col3, col4 = st.columns(2)
            
            with col3:
                simulation_days = st.slider(
                    "Simulation Days",
                    min_value=30,
                    max_value=365,
                    value=120,
                    step=10
                )
                
                intervention_scenario = st.selectbox(
                    "Intervention Scenario",
                    ["no_intervention", "rapid_response", "delayed_response", "herd_immunity"],
                    index=0,
                    help="Type of intervention strategy"
                )
            
            with col4:
                vaccination_rate = st.slider(
                    "Daily Vaccination Rate",
                    min_value=0.0,
                    max_value=0.05,
                    value=0.005,
                    step=0.001,
                    format="%.3f",
                    help="Percentage of population vaccinated daily"
                ) if intervention_scenario != "no_intervention" else 0.0
                
                compliance_rate = st.slider(
                    "Intervention Compliance",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.8,
                    step=0.05
                ) if intervention_scenario != "no_intervention" else 0.0
            
            # Animation settings
            st.markdown("---")
            st.markdown("### 🎬 Animation Settings")
            
            animate_simulation = st.checkbox(
                "Enable Animation Recording",
                value=True,
                help="Record simulation states for animation"
            )
            
            animation_step = st.slider(
                "Animation Step Size",
                min_value=1,
                max_value=10,
                value=2,
                step=1,
                help="Days between animation frames"
            )
            
            # Run button
            st.markdown("---")
            submitted = st.form_submit_button(
                "🚀 Run Simulation",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            # Store parameters
            st.session_state.simulation_params = {
                'population': population,
                'network_type': network_type,
                'network_params': network_params,
                'disease_variant': disease_variant,
                'custom_params': custom_params,
                'n_seed_infections': n_seed_infections,
                'seed_method': seed_method,
                'simulation_days': simulation_days,
                'intervention_scenario': intervention_scenario,
                'vaccination_rate': vaccination_rate,
                'compliance_rate': compliance_rate,
                'animate_simulation': animate_simulation,
                'animation_step': animation_step
            }
            
            # Run the simulation
            self._run_simulation(st.session_state.simulation_params)
            st.rerun()
    
    def _run_example_simulation(self):
        """Run an example simulation with default parameters"""
        try:
            with st.spinner("Running example simulation..."):
                if not MODULES_AVAILABLE:
                    st.error("Modules not available for example simulation")
                    return
                
                # Generate network
                generator = UltimateNetworkGenerator(population=500)
                G = generator.hybrid_multilayer()
                
                # Create disease
                disease = DiseaseLibrary.covid19_variant("omicron")
                
                # Create simulator
                simulator = UltimateSimulator(G, disease)
                simulator.seed_infections(10, method='random')
                
                # Run simulation WITH checkpoints for animation
                if hasattr(simulator, 'run_with_animation'):
                    # FIX: Remove show_progress parameter
                    history, checkpoints = simulator.run_with_animation(
                        days=60,
                        save_checkpoints=True,
                        checkpoint_interval=2
                    )
                    simulator.checkpoints = checkpoints
                    st.session_state.checkpoints = checkpoints
                else:
                    # Use regular run method
                    history = simulator.run(days=60, show_progress=False)
                
                # Store results
                st.session_state.simulator = simulator
                st.session_state.simulation_history = history
                st.session_state.network_graph = G
                st.session_state.animation_ready = False
                st.session_state.simulation_complete = True
                
                # Create animator
                animator = LiveAnimationSimulator(simulator)
                st.session_state.animator = animator
                
                # Prepare animation
                self._prepare_animation()
                
                st.success("✅ Example simulation completed!")
                st.balloons()
                
        except Exception as e:
            st.error(f"Error running example: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def _run_simulation(self, params):
        """Run a simulation with given parameters"""
        try:
            if not MODULES_AVAILABLE:
                st.error("Required modules not available. Please ensure all project files are in the same directory.")
                return
            
            with st.spinner("Setting up simulation..."):
                # Generate network
                generator = UltimateNetworkGenerator(population=params['population'])
                
                network_type = params['network_type']
                if network_type == "erdos_renyi":
                    G = generator.erdos_renyi(p=params['network_params'].get('erdos_p', 0.01))
                elif network_type == "watts_strogatz":
                    G = generator.watts_strogatz(
                        k=params['network_params'].get('watts_k', 8),
                        p=params['network_params'].get('watts_p', 0.3)
                    )
                elif network_type == "barabasi_albert":
                    G = generator.barabasi_albert(m=params['network_params'].get('barabasi_m', 3))
                elif network_type == "stochastic_block":
                    community_sizes = [params['population']//4] * 4
                    G = generator.stochastic_block(
                        community_sizes,
                        intra_prob=params['network_params'].get('block_intra', 0.15),
                        inter_prob=params['network_params'].get('block_inter', 0.01)
                    )
                else:
                    G = generator.hybrid_multilayer()
                
                # Configure disease
                if params['disease_variant'] == 'custom':
                    disease = DiseaseParameters(**params['custom_params'])
                else:
                    disease = DiseaseLibrary.covid19_variant(params['disease_variant'])
                
                # Create simulator
                simulator = UltimateSimulator(G, disease)
                
                # Seed infections
                simulator.seed_infections(
                    params['n_seed_infections'],
                    method=params['seed_method']
                )
                
                # Store network for visualization
                st.session_state.network_graph = G
                st.session_state.simulator = simulator
                st.session_state.simulation_running = True
                st.session_state.animation_ready = False
                st.session_state.simulation_complete = False
                
                # Run simulation with checkpoints if animation enabled
                if params['animate_simulation'] and hasattr(simulator, 'run_with_animation'):
                    with st.spinner(f"Running {params['simulation_days']}-day simulation with animation..."):
                        # FIX: Remove show_progress parameter
                        history, checkpoints = simulator.run_with_animation(
                            days=params['simulation_days'],
                            save_checkpoints=True,
                            checkpoint_interval=params['animation_step']
                        )
                        simulator.checkpoints = checkpoints
                        st.session_state.checkpoints = checkpoints
                else:
                    with st.spinner(f"Running {params['simulation_days']}-day simulation..."):
                        history = simulator.run(
                            days=params['simulation_days'],
                            show_progress=False
                        )
                
                st.session_state.simulation_history = history
                st.session_state.simulation_complete = True
                
                # Create animator
                st.session_state.animator = LiveAnimationSimulator(simulator)
                
                # Prepare animation
                if params['animate_simulation']:
                    self._prepare_animation()
                
                st.success(f"✅ Simulation completed successfully!")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error running simulation: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def _prepare_animation(self):
        """Prepare animation frames after simulation"""
        try:
            if st.session_state.animator is None and st.session_state.simulator is not None:
                st.session_state.animator = LiveAnimationSimulator(st.session_state.simulator)
            
            if st.session_state.animator is None:
                st.error("No animator available")
                return
            
            with st.spinner("Preparing animation frames..."):
                history = st.session_state.simulation_history
                if not history:
                    st.error("No simulation history available")
                    return
                    
                days = len(history['time']) if history else 0
                
                # Use checkpoints if available
                if hasattr(st.session_state.simulator, 'checkpoints') and st.session_state.simulator.checkpoints:
                    animator = LiveAnimationSimulator(st.session_state.simulator)
                    animator.checkpoints = st.session_state.simulator.checkpoints
                    
                    # Prepare animation from checkpoints
                    animator.prepare_animation(
                        days_to_animate=list(st.session_state.simulator.checkpoints.keys()),
                        step_size=1
                    )
                    
                    st.session_state.animation_frames = animator.animation_frames
                    st.session_state.animation_ready = True
                    st.session_state.animator = animator
                else:
                    # Prepare animation from history
                    step_size = max(1, days // 100)
                    days_to_animate = list(range(0, days, step_size))
                    
                    # Generate animation frames
                    animator = st.session_state.animator
                    animator.prepare_animation(
                        days_to_animate=days_to_animate,
                        step_size=step_size
                    )
                    
                    st.session_state.animation_frames = animator.animation_frames
                    st.session_state.animation_ready = True
                
                st.success(f"✅ Prepared {len(st.session_state.animation_frames)} animation frames!")
        
        except Exception as e:
            st.error(f"Error preparing animation: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    # ==================== TAB 3: ANALYSIS ====================
    
    def _render_analysis_tab(self):
        """Render the analysis tab"""
        st.markdown('<h2 class="sub-header">📊 Simulation Analysis</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to analyze results")
            return
        
        # Analysis options
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Epidemic Curves", "Network Analysis", "Disease Spread", "Intervention Effects"],
            index=0
        )
        
        if analysis_type == "Epidemic Curves":
            self._render_epidemic_curves()
        elif analysis_type == "Network Analysis":
            self._render_network_analysis()
        elif analysis_type == "Disease Spread":
            self._render_disease_spread_analysis()
        elif analysis_type == "Intervention Effects":
            self._render_intervention_analysis()
    
    # main_dashboard.py - FIXED VERSION (Plotly subplot fix)
# Only showing the fixed method - replace the _render_epidemic_curves() method

    def _render_epidemic_curves(self):
        """Render epidemic curves analysis"""
        history = st.session_state.simulation_history
        if not history:
            st.info("No simulation history available")
            return
        
        # FIX: Use different subplot specs for pie chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Disease Dynamics", "Daily New Cases", 
                        "Healthcare Burden", "State Distribution"),
            vertical_spacing=0.15,
            horizontal_spacing=0.15,
            specs=[
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "domain"}]  # FIX: domain for pie chart
            ]
        )
        
        # Plot 1: Disease Dynamics
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['S'], mode='lines', 
                    name='Susceptible', line=dict(color='green', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['I'], mode='lines', 
                    name='Infectious', line=dict(color='red', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['R'], mode='lines', 
                    name='Recovered', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Plot 2: Daily New Cases
        if 'new_infections' in history:
            fig.add_trace(
                go.Bar(x=history['time'], y=history['new_infections'], 
                    name='New Cases', marker_color='orange'),
                row=1, col=2
            )
        
        # Plot 3: Healthcare Burden
        if 'Ih' in history:
            fig.add_trace(
                go.Scatter(x=history['time'], y=history['Ih'], mode='lines',
                        name='Hospitalized', line=dict(color='purple', width=2)),
                row=2, col=1
            )
        
        # Plot 4: State Distribution (pie chart for final day) - FIXED POSITION
        if history['time']:
            final_day = len(history['time']) - 1
            states = ['S', 'I', 'R', 'D']
            values = []
            for state in states:
                if state in history and len(history[state]) > final_day:
                    values.append(history[state][final_day])
                else:
                    values.append(0)
            
            # Only show pie if we have values
            if sum(values) > 0:
                fig.add_trace(
                    go.Pie(labels=states, values=values, 
                        marker=dict(colors=['green', 'red', 'blue', 'gray']),
                        name="Final State Distribution"),
                    row=2, col=2  # FIX: Correct position for domain type
                )
        
        # Update layout
        fig.update_layout(
            height=700, 
            showlegend=True, 
            template='plotly_white',
            title_text="Epidemic Analysis Dashboard"
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Days", row=1, col=1)
        fig.update_xaxes(title_text="Days", row=1, col=2)
        fig.update_xaxes(title_text="Days", row=2, col=1)
        
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="New Cases", row=1, col=2)
        fig.update_yaxes(title_text="Hospitalized", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        if hasattr(st.session_state.simulator, 'get_summary_stats'):
            stats = st.session_state.simulator.get_summary_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Attack Rate", f"{stats.get('attack_rate', 0)*100:.1f}%")
            with col2:
                st.metric("Peak Infections", f"{stats.get('peak_infections', 0):.0f}")
            with col3:
                st.metric("Total Deaths", f"{stats.get('total_deaths', 0):.0f}")
            with col4:
                st.metric("Case Fatality", f"{stats.get('case_fatality_rate', 0)*100:.2f}%")
        
        def _render_network_analysis(self):
            """Render network analysis"""
            if st.session_state.network_graph is None:
                st.info("No network available for analysis")
                return
            
            G = st.session_state.network_graph
            
            # Calculate network metrics
            st.markdown("### 📐 Network Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Nodes", G.number_of_nodes())
            with col2:
                st.metric("Edges", G.number_of_edges())
            with col3:
                st.metric("Density", f"{nx.density(G):.4f}")
            with col4:
                avg_degree = np.mean([d for _, d in G.degree()])
                st.metric("Avg Degree", f"{avg_degree:.2f}")
            
            # Degree distribution
            st.markdown("### 📊 Degree Distribution")
            degrees = [d for _, d in G.degree()]
            
            fig = px.histogram(x=degrees, nbins=30, 
                            labels={'x': 'Degree', 'y': 'Count'},
                            title='Node Degree Distribution')
            st.plotly_chart(fig, use_container_width=True)
            
            # Community detection
            st.markdown("### 🏘️ Community Structure")
            
            try:
                from networkx.algorithms import community
                
                # Use greedy modularity communities
                communities = list(community.greedy_modularity_communities(G))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Communities", len(communities))
                with col2:
                    avg_community_size = np.mean([len(c) for c in communities])
                    st.metric("Avg Community Size", f"{avg_community_size:.0f}")
                
                # Show community sizes distribution
                community_sizes = [len(c) for c in communities]
                fig = px.bar(x=list(range(len(community_sizes))), y=community_sizes,
                            labels={'x': 'Community ID', 'y': 'Size'},
                            title='Community Sizes')
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.info(f"Community detection not available: {e}")
    
    def _render_disease_spread_analysis(self):
        """Render disease spread analysis"""
        if not st.session_state.simulation_history:
            st.info("No simulation history available")
            return
        
        history = st.session_state.simulation_history
        
        # Infection timeline
        st.markdown("### 🦠 Infection Timeline")
        
        fig = go.Figure()
        
        # Cumulative infections
        if 'total_infected' not in history and 'I' in history and 'R' in history:
            # Calculate cumulative infections
            total_infected = []
            cumulative = 0
            for i in range(len(history['time'])):
                # New infections = change in I + R
                if i > 0:
                    new_cases = (history['I'][i] + history['R'][i]) - (history['I'][i-1] + history['R'][i-1])
                    cumulative += max(0, new_cases)
                total_infected.append(cumulative)
            
            history['total_infected'] = total_infected
        
        if 'total_infected' in history:
            fig.add_trace(go.Scatter(
                x=history['time'], 
                y=history['total_infected'],
                mode='lines',
                name='Cumulative Infections',
                line=dict(color='darkred', width=3)
            ))
        
        fig.update_layout(
            title='Cumulative Infections Over Time',
            xaxis_title='Days',
            yaxis_title='Cumulative Infections',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Transmission network
        st.markdown("### 🔗 Transmission Network")
        
        if hasattr(st.session_state.simulator, 'infection_tree'):
            try:
                infection_tree = st.session_state.simulator.get_infection_tree(max_depth=3)
                
                if infection_tree:
                    # Visualize transmission tree
                    self._visualize_transmission_tree(infection_tree)
                else:
                    st.info("No detailed infection tree available")
            except:
                st.info("Infection tree data not available")
        else:
            st.info("Infection tree data not available")
    
    def _visualize_transmission_tree(self, infection_tree):
        """Visualize infection transmission tree"""
        # Create hierarchical tree visualization
        import plotly.graph_objects as go
        
        # Flatten tree for visualization
        nodes = []
        edges = []
        node_labels = {}
        
        def add_node(node_id, label, depth):
            nodes.append({
                'id': node_id,
                'label': label,
                'depth': depth
            })
            node_labels[node_id] = label
        
        def traverse_tree(tree, parent_id=None, depth=0):
            for node_id, children in tree.items():
                node_label = f"Node {node_id}"
                add_node(node_id, node_label, depth)
                
                if parent_id is not None:
                    edges.append({
                        'from': parent_id,
                        'to': node_id
                    })
                
                if children:
                    traverse_tree({child['id']: child.get('children', []) 
                                 for child in children}, node_id, depth + 1)
        
        traverse_tree(infection_tree)
        
        # Create network graph
        fig = go.Figure()
        
        # Add edges
        for edge in edges:
            fig.add_trace(go.Scatter(
                x=[edge['from'], edge['to'], None],
                y=[0, 1, None],  # Simplified layout
                mode='lines',
                line=dict(width=1, color='gray'),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=[node['id'] for node in nodes],  # Simplified layout
            y=[node['depth'] for node in nodes],
            mode='markers+text',
            marker=dict(size=20, color='red'),
            text=[node['label'] for node in nodes],
            textposition="top center",
            hoverinfo='text',
            name='Infected Individuals'
        ))
        
        fig.update_layout(
            title='Infection Transmission Tree',
            showlegend=False,
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_intervention_analysis(self):
        """Render intervention effects analysis"""
        st.info("Intervention analysis - Run simulation with different interventions to compare")
        
        # Placeholder for intervention comparison
        if st.button("Run Intervention Comparison", use_container_width=True):
            st.info("This would run simulations with different intervention scenarios")
    
    # ==================== TAB 4: VISUALIZATION ====================
    
    def _render_visualization_tab(self):
        """Render the visualization tab"""
        st.markdown('<h2 class="sub-header">🎨 Interactive Visualization</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to visualize results")
            return
        
        # Visualization controls
        viz_col1, viz_col2 = st.columns([2, 1])
        
        with viz_col1:
            viz_type = st.selectbox(
                "Visualization Type",
                ["Network Spread Animation", "Static Network", "Heatmap", "3D Network"],
                index=0
            )
        
        with viz_col2:
            if viz_type == "Network Spread Animation":
                if st.session_state.animation_frames and len(st.session_state.animation_frames) > 1:
                    current_day = st.slider(
                        "Animation Day",
                        0,
                        len(st.session_state.animation_frames) - 1,
                        min(st.session_state.current_day, len(st.session_state.animation_frames) - 1)
                    )
                    st.session_state.current_day = current_day
                elif st.session_state.simulation_history:
                    max_day = len(st.session_state.simulation_history['time']) - 1 if st.session_state.simulation_history else 0
                    if max_day > 0:
                        current_day = st.slider(
                            "Day to Visualize",
                            0,
                            max_day,
                            min(st.session_state.current_day, max_day)
                        )
                        st.session_state.current_day = current_day
        
        # Generate visualization
        if viz_type == "Network Spread Animation":
            self._render_network_spread_animation(st.session_state.current_day)
        elif viz_type == "Static Network":
            self._render_static_network()
        elif viz_type == "Heatmap":
            self._render_heatmap()
        elif viz_type == "3D Network":
            self._render_3d_network()
    
    def _render_network_spread_animation(self, current_day):
        """Render animated network spread visualization"""
        st.markdown("### 🦠 Disease Spread Through Network")
        
        if not st.session_state.animation_frames:
            if st.session_state.simulation_complete:
                st.warning("Animation frames not prepared. Preparing now...")
                self._prepare_animation()
                st.rerun()
                return
            else:
                st.info("Run a simulation first to see animation")
                return
        
        # Get frame - safely handle index
        if current_day >= len(st.session_state.animation_frames):
            current_day = len(st.session_state.animation_frames) - 1
            st.session_state.current_day = current_day
            
        frame = st.session_state.animation_frames[current_day]
        
        # Create visualization
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Network visualization
            st.markdown(f"#### Network State - Day {frame['day']}")
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(12, 10))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                # Compute layout if not available
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
                st.session_state.animator.node_positions = pos
            
            G = st.session_state.network_graph
            
            # Draw edges (light gray, thin)
            nx.draw_networkx_edges(
                G, pos, 
                ax=ax, 
                alpha=0.1, 
                width=0.3,
                edge_color='gray'
            )
            
            # Draw nodes with colors from frame
            node_colors = frame['node_colors']
            node_sizes = frame.get('node_sizes', [50] * len(G.nodes()))
            
            # Group nodes by color for efficient drawing
            color_groups = {}
            for i, node in enumerate(G.nodes()):
                color = node_colors[i] if i < len(node_colors) else '#CCCCCC'
                if color not in color_groups:
                    color_groups[color] = []
                color_groups[color].append(node)
            
            # Draw each color group
            for color, nodes in color_groups.items():
                # Get sizes for these nodes
                sizes = []
                for node in nodes:
                    node_idx = list(G.nodes()).index(node)
                    if node_idx < len(node_sizes):
                        sizes.append(node_sizes[node_idx])
                    else:
                        sizes.append(50)
                
                nx.draw_networkx_nodes(
                    G, pos, 
                    nodelist=nodes,
                    node_color=color,
                    node_size=sizes,
                    ax=ax,
                    edgecolors='black',
                    linewidths=0.5
                )
            
            # Add title and legend
            ax.set_title(f"Day {frame['day']} - Disease Spread Visualization", fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#4CAF50', label='Susceptible'),
                Patch(facecolor='#FF9800', label='Exposed'),
                Patch(facecolor='#F44336', label='Infectious'),
                Patch(facecolor='#2196F3', label='Recovered'),
                Patch(facecolor='#757575', label='Deceased'),
                Patch(facecolor='#9C27B0', label='Vaccinated')
            ]
            
            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
            
            st.pyplot(fig)
            plt.close()
            
            # Animation controls
            if len(st.session_state.animation_frames) > 1:
                st.markdown("#### 🎛️ Animation Controls")
                anim_col1, anim_col2, anim_col3 = st.columns(3)
                
                with anim_col1:
                    if st.button("▶️ Play Animation", use_container_width=True):
                        self._play_animation_in_place()
                
                with anim_col2:
                    if st.button("⏸️ Pause", use_container_width=True):
                        st.info("Animation paused")
                
                with anim_col3:
                    speed = st.slider("Speed", 0.25, 4.0, 1.0, 0.25)
        
        with col2:
            # Statistics
            st.markdown("#### 📊 Statistics")
            
            stats = frame['statistics']
            
            # Key metrics
            metric_cols = st.columns(2)
            
            with metric_cols[0]:
                st.metric("Susceptible", stats.get('S', 0))
                st.metric("Exposed", stats.get('E', 0))
            
            with metric_cols[1]:
                st.metric("Infectious", stats.get('I', 0))
                st.metric("Recovered", stats.get('R', 0))
            
            # New cases
            if 'new_cases' in stats:
                st.metric("New Cases", stats.get('new_cases', 0))
            
            # State distribution
            st.markdown("#### 📈 State Distribution")
            
            state_counts = {}
            for state in frame['node_states'].values():
                state_counts[state] = state_counts.get(state, 0) + 1
            
            if state_counts:
                # Create pie chart
                fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
                
                # Map state codes to readable names
                state_names = {
                    'S': 'Susceptible',
                    'E': 'Exposed',
                    'I': 'Infectious',
                    'R': 'Recovered',
                    'D': 'Deceased',
                    'V': 'Vaccinated'
                }
                
                labels = [state_names.get(s, s) for s in state_counts.keys()]
                sizes = list(state_counts.values())
                colors = [self._get_state_color(s) for s in state_counts.keys()]
                
                ax_pie.pie(sizes, labels=labels, colors=colors,
                          autopct='%1.1f%%', startangle=90)
                ax_pie.axis('equal')
                ax_pie.set_title(f"Day {frame['day']} Distribution")
                
                st.pyplot(fig_pie)
                plt.close()
    
    def _get_state_color(self, state):
        """Get color for a state"""
        color_map = {
            'S': '#4CAF50',
            'E': '#FF9800',
            'I': '#F44336',
            'R': '#2196F3',
            'D': '#757575',
            'V': '#9C27B0'
        }
        return color_map.get(state, '#CCCCCC')
    
    def _play_animation_in_place(self):
        """Play animation in the current visualization"""
        if not st.session_state.animation_frames or len(st.session_state.animation_frames) <= 1:
            return
        
        # Create a placeholder
        animation_placeholder = st.empty()
        
        # Play animation
        for i, frame in enumerate(st.session_state.animation_frames):
            # Update the placeholder with current frame
            with animation_placeholder.container():
                self._display_animation_frame_simple(frame, i)
            
            # Wait before next frame
            time.sleep(0.3)  # Adjust speed as needed
        
        # Clear placeholder when done
        animation_placeholder.empty()
    
    def _display_animation_frame_simple(self, frame, frame_idx):
        """Display a simple animation frame"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Simple network visualization
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
            
            G = st.session_state.network_graph
            
            # Draw network
            node_colors = frame['node_colors']
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, 
                                  node_color=node_colors,
                                  node_size=50,
                                  ax=ax)
            
            ax.set_title(f"Day {frame['day']} - Frame {frame_idx+1}/{len(st.session_state.animation_frames)}")
            ax.axis('off')
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # Simple stats
            stats = frame['statistics']
            st.metric("Day", frame['day'])
            st.metric("Infectious", stats.get('I', 0))
            st.metric("New Cases", stats.get('new_cases', 0))
    
    def _render_static_network(self):
        """Render static network visualization"""
        if st.session_state.network_graph is None:
            st.info("No network available")
            return
        
        G = st.session_state.network_graph
        
        st.markdown("### 🌐 Network Structure")
        
        # Network visualization options
        layout_type = st.selectbox(
            "Layout Algorithm",
            ["spring", "circular", "kamada_kawai", "random"],
            index=0
        )
        
        node_color_by = st.selectbox(
            "Color Nodes By",
            ["degree", "age", "mobility", "state"],
            index=0
        )
        
        # Compute layout
        if layout_type == "spring":
            pos = nx.spring_layout(G, seed=42, iterations=100)
        elif layout_type == "circular":
            pos = nx.circular_layout(G)
        elif layout_type == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.random_layout(G)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Determine node colors
        if node_color_by == "degree":
            degrees = dict(G.degree())
            node_colors = [degrees[n] for n in G.nodes()]
            cmap = plt.cm.viridis
        elif node_color_by == "age":
            node_colors = [G.nodes[n].get('age', 40) for n in G.nodes()]
            cmap = plt.cm.plasma
        elif node_color_by == "mobility":
            node_colors = [G.nodes[n].get('mobility', 0.5) for n in G.nodes()]
            cmap = plt.cm.coolwarm
        else:  # state
            node_colors = []
            for n in G.nodes():
                state = G.nodes[n].get('state', 'S')
                color_map = {'S': 0, 'E': 1, 'I': 2, 'R': 3, 'D': 4, 'V': 5}
                node_colors.append(color_map.get(state, 0))
            cmap = plt.cm.Set3
        
        # Draw network
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=0.5)
        
        nodes = nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=100,
            cmap=cmap,
            ax=ax,
            edgecolors='black',
            linewidths=0.5
        )
        
        ax.set_title(f"Network Visualization - {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        ax.axis('off')
        
        # Add colorbar if numeric
        if node_color_by in ["degree", "age", "mobility"]:
            plt.colorbar(nodes, ax=ax, label=node_color_by.capitalize())
        
        st.pyplot(fig)
        plt.close()
    
    def _render_heatmap(self):
        """Render heatmap visualization"""
        st.info("Heatmap visualization - showing disease spread patterns")
        
        if not st.session_state.simulation_history:
            return
        
        history = st.session_state.simulation_history
        
        # Create a heatmap of infections over time
        fig = go.Figure(data=go.Heatmap(
            z=[history['I']],
            x=history['time'],
            y=['Infectious'],
            colorscale='Reds',
            showscale=True
        ))
        
        fig.update_layout(
            title='Infection Heatmap Over Time',
            xaxis_title='Days',
            yaxis_title='State',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_3d_network(self):
        """Render 3D network visualization"""
        st.info("3D Network Visualization")
        
        # Simple 3D visualization using plotly
        if st.session_state.network_graph:
            G = st.session_state.network_graph
            
            # Create 3D positions
            pos_3d = {}
            for node in G.nodes():
                pos_3d[node] = (
                    np.random.random(),
                    np.random.random(),
                    np.random.random()
                )
            
            # Create 3D scatter plot
            x_vals, y_vals, z_vals = [], [], []
            for node in G.nodes():
                x, y, z = pos_3d[node]
                x_vals.append(x)
                y_vals.append(y)
                z_vals.append(z)
            
            fig = go.Figure(data=[go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='markers',
                marker=dict(
                    size=5,
                    color='blue',
                    opacity=0.8
                )
            )])
            
            fig.update_layout(
                title='3D Network Visualization',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                ),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 5: ANIMATION ====================
    
    def _render_animation_tab(self):
        """Render the animation tab"""
        st.markdown('<h2 class="sub-header">🎬 Simulation Animation</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to create animations")
            return
        
        if not st.session_state.animation_ready:
            st.warning("⚠️ Animation not prepared yet.")
            
            if st.button("🎬 Prepare Animation Now", type="primary", use_container_width=True):
                self._prepare_animation()
                st.rerun()
            return
        
        # Animation controls
        st.markdown("### 🎛️ Animation Export")
        
        anim_col1, anim_col2, anim_col3 = st.columns(3)
        
        with anim_col1:
            animation_type = st.selectbox(
                "Export Format",
                ["GIF Video", "HTML Interactive", "Frame Images", "MP4 Video"],
                index=0
            )
        
        with anim_col2:
            fps = st.slider("Frames Per Second", 1, 30, 10)
        
        with anim_col3:
            quality = st.select_slider(
                "Quality",
                options=["Low", "Medium", "High"],
                value="Medium"
            )
        
        # Generate buttons
        if st.button("🎥 Generate Animation", type="primary", use_container_width=True):
            if animation_type == "GIF Video":
                self._generate_gif_animation(fps, quality)
            elif animation_type == "HTML Interactive":
                self._generate_html_animation()
            elif animation_type == "Frame Images":
                self._export_animation_frames()
            elif animation_type == "MP4 Video":
                self._generate_mp4_animation(fps, quality)
        
        # Live animation preview
        st.markdown("---")
        st.markdown("### 👁️ Live Preview")
        
        if st.session_state.animation_frames and len(st.session_state.animation_frames) > 1:
            current_day = st.slider(
                "Select Day to Preview",
                0,
                len(st.session_state.animation_frames) - 1,
                min(st.session_state.current_day, len(st.session_state.animation_frames) - 1),
                key="animation_preview_day"
            )
            
            st.session_state.current_day = current_day
            
            # Display selected frame
            self._display_animation_frame(current_day)
        
        # Auto-play controls
        st.markdown("---")
        st.markdown("### ▶️ Auto-Play Animation")
        
        play_col1, play_col2 = st.columns(2)
        
        with play_col1:
            auto_play = st.button("▶️ Play in Streamlit", use_container_width=True)
        
        with play_col2:
            delay = st.slider("Frame Delay (ms)", 100, 2000, 500, 100)
        
        if auto_play:
            self._play_streamlit_animation(delay)
    
    def _display_animation_frame(self, frame_idx):
        """Display a single animation frame"""
        if not st.session_state.animation_frames:
            return
        
        # Safely handle frame index
        if frame_idx >= len(st.session_state.animation_frames):
            frame_idx = len(st.session_state.animation_frames) - 1
        
        frame = st.session_state.animation_frames[frame_idx]
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create network visualization
            fig, ax = plt.subplots(figsize=(12, 10))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
            
            G = st.session_state.network_graph
            
            # Draw edges (light gray, thin)
            nx.draw_networkx_edges(
                G, pos, 
                ax=ax, 
                alpha=0.1, 
                width=0.3,
                edge_color='gray'
            )
            
            # Draw nodes with colors from frame
            node_colors = frame['node_colors']
            node_sizes = frame.get('node_sizes', [50] * len(G.nodes()))
            
            # Group nodes by color for efficient drawing
            color_groups = {}
            for i, node in enumerate(G.nodes()):
                color = node_colors[i] if i < len(node_colors) else '#CCCCCC'
                if color not in color_groups:
                    color_groups[color] = []
                color_groups[color].append(node)
            
            # Draw each color group
            for color, nodes in color_groups.items():
                # Get sizes for these nodes
                sizes = []
                for node in nodes:
                    node_idx = list(G.nodes()).index(node)
                    if node_idx < len(node_sizes):
                        sizes.append(node_sizes[node_idx])
                    else:
                        sizes.append(50)
                
                nx.draw_networkx_nodes(
                    G, pos, 
                    nodelist=nodes,
                    node_color=color,
                    node_size=sizes,
                    ax=ax,
                    edgecolors='black',
                    linewidths=0.5
                )
            
            ax.set_title(f"Day {frame['day']} - Disease Spread", fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#4CAF50', label='Susceptible'),
                Patch(facecolor='#FF9800', label='Exposed'),
                Patch(facecolor='#F44336', label='Infectious'),
                Patch(facecolor='#2196F3', label='Recovered')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.markdown(f"### Day {frame['day']}")
            
            # Display statistics
            stats = frame['statistics']
            
            st.metric("Susceptible", stats.get('S', 0))
            st.metric("Infectious", stats.get('I', 0))
            st.metric("Recovered", stats.get('R', 0))
            
            if 'new_cases' in stats:
                st.metric("New Cases", stats.get('new_cases', 0))
            
            # Progress indicator
            progress = (frame_idx + 1) / len(st.session_state.animation_frames)
            st.progress(progress, text=f"Frame {frame_idx + 1}/{len(st.session_state.animation_frames)}")
    
    def _generate_gif_animation(self, fps, quality):
        """Generate GIF animation"""
        try:
            if st.session_state.animator is None:
                st.error("Animator not available")
                return
            
            with st.spinner("Creating GIF animation..."):
                # Create temporary directory for frames
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Export frames
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=tmpdir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    # Create GIF using imageio
                    try:
                        import imageio
                        
                        # Get all frame files
                        frame_files = sorted([f for f in os.listdir(tmpdir) if f.endswith('.png')])
                        
                        if not frame_files:
                            st.error("No frames exported")
                            return
                        
                        # Read frames
                        frames = []
                        for frame_file in frame_files:
                            frame_path = os.path.join(tmpdir, frame_file)
                            frames.append(imageio.imread(frame_path))
                        
                        # Save as GIF
                        output_path = "simulation_animation.gif"
                        imageio.mimsave(output_path, frames, fps=fps)
                        
                        # Display GIF
                        st.success(f"✅ GIF created: {output_path}")
                        
                        # Show preview
                        st.image(output_path, caption="Simulation Animation GIF")
                        
                        # Download button
                        with open(output_path, "rb") as f:
                            gif_data = f.read()
                        
                        st.download_button(
                            label="📥 Download GIF",
                            data=gif_data,
                            file_name="pandemic_simulation.gif",
                            mime="image/gif"
                        )
                        
                    except ImportError:
                        st.error("imageio not installed. Install with: pip install imageio")
                        return
                    
        except Exception as e:
            st.error(f"Error generating GIF: {str(e)}")
    
    def _generate_html_animation(self):
        """Generate interactive HTML animation"""
        try:
            if st.session_state.animator is None:
                st.error("Animator not available")
                return
            
            with st.spinner("Creating interactive HTML animation..."):
                output_file = "interactive_animation.html"
                
                # Check if animator has the method
                if hasattr(st.session_state.animator, 'create_interactive_animation'):
                    st.session_state.animator.create_interactive_animation(output_file)
                    
                    # Read the HTML file
                    with open(output_file, "r") as f:
                        html_content = f.read()
                    
                    # Display in Streamlit
                    st.success(f"✅ HTML animation created: {output_file}")
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download HTML Animation",
                        data=html_content,
                        file_name="pandemic_animation.html",
                        mime="text/html"
                    )
                    
                    # Show preview
                    st.components.v1.html(html_content, height=600, scrolling=True)
                else:
                    st.error("Interactive animation method not available in animator")
                    
        except Exception as e:
            st.error(f"Error generating HTML animation: {str(e)}")
    
    def _export_animation_frames(self):
        """Export animation frames as images"""
        try:
            if st.session_state.animator is None:
                st.error("Animator not available")
                return
            
            with st.spinner("Exporting animation frames..."):
                # Create zip file of frames
                import zipfile
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Export frames
                    frames_dir = os.path.join(tmpdir, "frames")
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=frames_dir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    # Create zip file
                    zip_path = os.path.join(tmpdir, "animation_frames.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for root, dirs, files in os.walk(frames_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, frames_dir)
                                zipf.write(file_path, arcname)
                    
                    # Read zip file
                    with open(zip_path, "rb") as f:
                        zip_data = f.read()
                    
                    # Create download button
                    st.success(f"✅ Exported {len(os.listdir(frames_dir))} frames")
                    st.download_button(
                        label="📥 Download All Frames (ZIP)",
                        data=zip_data,
                        file_name="animation_frames.zip",
                        mime="application/zip"
                    )
                    
        except Exception as e:
            st.error(f"Error exporting frames: {str(e)}")
    
    def _generate_mp4_animation(self, fps, quality):
        """Generate MP4 video animation"""
        st.info("MP4 video creation requires ffmpeg. Ensure it's installed on your system.")
        
        try:
            import subprocess
            
            # Check if ffmpeg is available
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error("FFmpeg not found. Please install ffmpeg to create MP4 videos.")
                st.info("Installation instructions:")
                st.code("""
                # Ubuntu/Debian
                sudo apt-get install ffmpeg
                
                # macOS
                brew install ffmpeg
                
                # Windows
                Download from https://ffmpeg.org/download.html
                """)
                return
            
            with st.spinner("Creating MP4 video..."):
                # Create temporary directory for frames
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Export frames
                    frames_dir = os.path.join(tmpdir, "frames")
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=frames_dir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    # Create MP4 using ffmpeg
                    output_path = "simulation_animation.mp4"
                    
                    # Build ffmpeg command
                    cmd = [
                        'ffmpeg',
                        '-framerate', str(fps),
                        '-pattern_type', 'glob',
                        '-i', f'{frames_dir}/*.png',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-vf', 'scale=1920:1080' if quality == "High" else 'scale=1280:720',
                        output_path,
                        '-y'  # Overwrite output file
                    ]
                    
                    # Run ffmpeg
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Display video
                        st.success(f"✅ MP4 video created: {output_path}")
                        
                        # Show video preview
                        video_file = open(output_path, 'rb')
                        video_bytes = video_file.read()
                        st.video(video_bytes)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download MP4 Video",
                            data=video_bytes,
                            file_name="pandemic_simulation.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error(f"FFmpeg error: {result.stderr}")
                        
        except Exception as e:
            st.error(f"Error generating MP4: {str(e)}")
    
    def _play_streamlit_animation(self, delay_ms):
        """Play animation directly in Streamlit"""
        try:
            frames = st.session_state.animation_frames
            if not frames or len(frames) <= 1:
                st.error("No animation frames available or only one frame")
                return
            
            # Create placeholder
            animation_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animation loop
            for i, frame in enumerate(frames):
                progress_bar.progress((i + 1) / len(frames))
                
                # Update display
                with animation_placeholder.container():
                    self._display_animation_frame(i)
                
                # Wait for next frame
                time.sleep(delay_ms / 1000)
            
            # Clear when done
            animation_placeholder.empty()
            progress_bar.empty()
            
            st.success("✅ Animation complete!")
            
        except Exception as e:
            st.error(f"Error playing animation: {str(e)}")
    
    # ==================== TAB 6: RESULTS ====================
    
    def _render_results_tab(self):
        """Render the results tab"""
        st.markdown('<h2 class="sub-header">📈 Simulation Results</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to see results")
            return
        
        # Results summary
        st.markdown("### 📊 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Results CSV", use_container_width=True):
                self._export_results_csv()
        
        with col2:
            if st.button("📋 Export Summary JSON", use_container_width=True):
                self._export_summary()
        
        with col3:
            if st.button("🖼️ Export Final Visualization", use_container_width=True):
                self._export_final_visualization()
        
        # Detailed results
        st.markdown("---")
        st.markdown("### 📋 Detailed Metrics")
        
        if hasattr(st.session_state.simulator, 'get_summary_stats'):
            try:
                stats = st.session_state.simulator.get_summary_stats()
                
                # Display metrics in a nice format
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown("#### 📈 Epidemic Metrics")
                    for key in ['attack_rate', 'peak_infections', 'peak_day', 'case_fatality_rate']:
                        if key in stats:
                            value = stats[key]
                            if isinstance(value, float):
                                display = f"{value:.2%}" if 'rate' in key else f"{value:.2f}"
                            else:
                                display = str(value)
                            st.metric(key.replace('_', ' ').title(), display)
                
                with metrics_col2:
                    st.markdown("#### 👥 Population Metrics")
                    for key in ['initial_population', 'total_infected', 'total_recovered', 'total_deaths', 'total_vaccinated']:
                        if key in stats:
                            value = stats[key]
                            st.metric(key.replace('_', ' ').title(), f"{value:,}")
            except:
                st.warning("Could not load summary statistics")
        
        # Simulation history
        if st.session_state.simulation_history:
            st.markdown("---")
            st.markdown("### 📈 Time Series Data")
            
            # Create dataframe
            history_df = pd.DataFrame(st.session_state.simulation_history)
            
            # Show last 30 days
            st.dataframe(history_df.tail(30), use_container_width=True)
            
            # Download full history
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full History CSV",
                data=csv,
                file_name="simulation_history.csv",
                mime="text/csv"
            )
    
    def _export_results_csv(self):
        """Export results to CSV"""
        try:
            if st.session_state.simulation_history:
                df = pd.DataFrame(st.session_state.simulation_history)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="simulation_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No simulation results to export")
        except Exception as e:
            st.error(f"Error exporting CSV: {str(e)}")
    
    def _export_summary(self):
        """Export summary to JSON"""
        try:
            if hasattr(st.session_state.simulator, 'get_summary_stats'):
                stats = st.session_state.simulator.get_summary_stats()
                
                # Add simulation parameters
                if hasattr(st.session_state, 'simulation_params'):
                    stats['simulation_parameters'] = st.session_state.simulation_params
                
                json_str = json.dumps(stats, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON Summary",
                    data=json_str,
                    file_name="simulation_summary.json",
                    mime="application/json"
                )
            else:
                st.warning("No summary statistics available")
        except Exception as e:
            st.error(f"Error exporting summary: {str(e)}")
    
    def _export_final_visualization(self):
        """Export final visualization as image"""
        try:
            if st.session_state.animation_frames:
                # Use the last frame
                final_frame = st.session_state.animation_frames[-1]
                
                # Create visualization
                fig, ax = plt.subplots(figsize=(12, 10))
                
                if hasattr(st.session_state.animator, 'node_positions'):
                    pos = st.session_state.animator.node_positions
                else:
                    pos = nx.spring_layout(st.session_state.network_graph, seed=42)
                
                G = st.session_state.network_graph
                node_colors = final_frame['node_colors']
                
                # Draw network
                nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
                nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=50, ax=ax)
                
                ax.set_title(f"Final State - Day {final_frame['day']}", fontsize=16, fontweight='bold')
                ax.axis('off')
                
                # Save to buffer
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                plt.close()
                
                # Create download button
                st.download_button(
                    label="📥 Download Final Visualization",
                    data=buf.getvalue(),
                    file_name="final_simulation_state.png",
                    mime="image/png"
                )
                
                # Show preview
                st.image(buf.getvalue(), caption="Final Simulation State")
                
        except Exception as e:
            st.error(f"Error exporting visualization: {str(e)}")

def main():
    """Main function to run the dashboard"""
    dashboard = PandemicDashboard()
    dashboard.run()

if __name__ == "__main__":
    # Check for required packages
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy', 'matplotlib', 'networkx']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        # Check for optional packages
        optional_packages = ['PIL', 'imageio', 'ffmpeg-python']
        for package in optional_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                print(f"⚠️  Optional package '{package}' not installed. Some features may be limited.")
                print(f"   Install with: pip install {package}")
        
        print("🚀 Starting Pandemic Simulation Dashboard...")
        print("📊 Open your browser and go to http://localhost:8501")
        print("🎬 Features: Network Animation, Disease Spread Visualization, Video Export!")
        print("=" * 60)
        
        # Run the dashboard
        main()