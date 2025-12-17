# main_dashboard.py - COMPLETE FIXED VERSION
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
import json
import pickle
import os
from datetime import datetime
import sys
import warnings
import time
warnings.filterwarnings('ignore')

# Add project modules to path
sys.path.append('.')

# Try to import project modules
try:
    from network_generator import UltimateNetworkGenerator
    from disease_models import DiseaseLibrary, DiseaseParameters, InterventionSchedule
    from simulator_engine import UltimateSimulator
    from visualization_3d import PandemicVisualizer3D
    from parameter_sweeper import ParameterSweeper
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
        
        # Load example data if available
        self._load_example_data()
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'simulator' not in st.session_state:
            st.session_state.simulator = None
        if 'simulation_history' not in st.session_state:
            st.session_state.simulation_history = None
        if 'visualizer' not in st.session_state:
            st.session_state.visualizer = None
        if 'animator' not in st.session_state:
            st.session_state.animator = None
        if 'current_day' not in st.session_state:
            st.session_state.current_day = 0
        if 'simulation_running' not in st.session_state:
            st.session_state.simulation_running = False
        if 'parameter_sweeper' not in st.session_state:
            st.session_state.parameter_sweeper = None
        if 'sweep_results' not in st.session_state:
            st.session_state.sweep_results = None
        if 'animation_ready' not in st.session_state:
            st.session_state.animation_ready = False
        if 'animation_frames' not in st.session_state:
            st.session_state.animation_frames = []
    
    def _set_custom_css(self):
        """Set custom CSS for the dashboard"""
        st.markdown("""
        <style>
        /* Main styling */
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
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 5px 5px 0 0;
            padding: 10px 20px;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3rem;
            font-weight: bold;
        }
        
        /* Animation controls */
        .animation-controls {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom colors for states */
        .state-susceptible { color: #4CAF50; }
        .state-exposed { color: #FF9800; }
        .state-infectious { color: #F44336; }
        .state-recovered { color: #2196F3; }
        .state-deceased { color: #9E9E9E; }
        .state-vaccinated { color: #9C27B0; }
        
        /* Progress bar animation */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _load_example_data(self):
        """Load example data for demonstration"""
        if 'example_network' not in st.session_state:
            try:
                # Create a small example network
                if MODULES_AVAILABLE:
                    generator = UltimateNetworkGenerator(population=200)
                    st.session_state.example_network = generator.hybrid_multilayer()
                    
                    # Create example disease
                    st.session_state.example_disease = DiseaseLibrary.covid19_variant("omicron")
                    
                    print("✅ Example data loaded successfully")
            except:
                print("⚠️  Could not load example data")
    
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
            "🔬 Parameter Sweep",
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
            self._render_parameter_sweep_tab()
        
        with tabs[6]:
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
            
            **1. Network Generation**
            - Create realistic social networks with various structures
            - Control population size, connection patterns, and demographics
            
            **2. Disease Modeling**
            - Simulate COVID-19 variants (Wildtype, Alpha, Delta, Omicron)
            - Customize transmission parameters (R0, incubation, mortality)
            
            **3. Intervention Strategies**
            - Test different intervention scenarios
            - Adjust timing and efficacy of measures
            
            **4. Advanced Visualization**
            - 3D interactive network visualization
            - **🎬 Real-time simulation animation**
            - Video export (GIF/MP4) of simulations
            - Comprehensive analytics dashboard
            
            **5. Parameter Exploration**
            - Run parameter sweeps to find optimal strategies
            - Sensitivity analysis for key parameters
            """)
        
        with col2:
            st.markdown('<h3 class="sub-header">📈 Quick Stats</h3>', 
                       unsafe_allow_html=True)
            
            # Example metrics
            if st.session_state.simulator:
                stats = st.session_state.simulator.get_summary_stats() if hasattr(st.session_state.simulator, 'get_summary_stats') else {}
                metrics_data = {
                    "Simulations Run": "1",
                    "Attack Rate": f"{stats.get('attack_rate', 0)*100:.1f}%" if 'attack_rate' in stats else "0%",
                    "Peak Infections": f"{stats.get('peak_infections', 0):.0f}" if 'peak_infections' in stats else "0",
                    "Total Deaths": f"{stats.get('total_deaths', 0):.0f}" if 'total_deaths' in stats else "0"
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
            
            if st.session_state.simulator and not st.session_state.animation_ready:
                if st.button("🎬 Prepare Animation", use_container_width=True):
                    self._prepare_animation()
            
            st.markdown("""
            **Steps:**
            1. Go to **Simulation** tab
            2. Configure network and disease
            3. Click **Run Simulation**
            4. **Prepare Animation** for visualization
            5. Explore results in other tabs
            
            **Need help?**
            - Check tooltips for parameter explanations
            - Start with example simulations
            - Adjust one parameter at a time
            """)
        
        # Recent simulations (if any)
        if st.session_state.simulation_history is not None:
            st.markdown("---")
            st.markdown('<h3 class="sub-header">📋 Recent Simulation</h3>', 
                       unsafe_allow_html=True)
            
            cols = st.columns(5)
            
            stats = st.session_state.simulator.get_summary_stats() if hasattr(st.session_state.simulator, 'get_summary_stats') else {}
            
            metric_keys = ['attack_rate', 'peak_infections', 'total_deaths', 'case_fatality_rate']
            metric_labels = ['Attack Rate', 'Peak Infections', 'Total Deaths', 'Fatality Rate']
            
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
    
    # ==================== TAB 2: SIMULATION ====================
    
    def _render_simulation_tab(self):
        """Render the simulation configuration tab"""
        st.markdown('<h2 class="sub-header">⚙️ Simulation Configuration</h2>', 
                   unsafe_allow_html=True)
        
        if not MODULES_AVAILABLE:
            st.error("⚠️ Required modules not available. Please check your imports.")
            return
        
        # Create configuration form
        with st.form("simulation_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🌐 Network Configuration")
                
                population = st.slider(
                    "Population Size",
                    min_value=100,
                    max_value=10000,
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
                    ["random", "hubs", "youngest", "oldest", "high_mobility"],
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
            
            # Run button
            st.markdown("---")
            submitted = st.form_submit_button(
                "🚀 Run Simulation",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            # Run the simulation with collected parameters
            self._run_simulation(
                population=population,
                network_type=network_type,
                network_params=network_params,
                disease_variant=disease_variant,
                custom_params=custom_params,
                n_seed_infections=n_seed_infections,
                seed_method=seed_method,
                simulation_days=simulation_days,
                intervention_scenario=intervention_scenario,
                vaccination_rate=vaccination_rate,
                compliance_rate=compliance_rate
            )
            st.rerun()
    
    def _run_example_simulation(self):
        """Run an example simulation with default parameters"""
        try:
            with st.spinner("Running example simulation..."):
                # Use example data
                if 'example_network' in st.session_state and 'example_disease' in st.session_state:
                    G = st.session_state.example_network
                    disease = st.session_state.example_disease
                    
                    # Create simulator
                    simulator = UltimateSimulator(G, disease)
                    simulator.seed_infections(10, method='random')
                    
                    # Run simulation
                    history = simulator.run(days=60, show_progress=False)
                    
                    # Store results
                    st.session_state.simulator = simulator
                    st.session_state.simulation_history = history
                    st.session_state.simulation_running = True
                    st.session_state.animation_ready = False
                    
                    # Create visualizer and animator
                    st.session_state.visualizer = PandemicVisualizer3D(simulator)
                    st.session_state.animator = LiveAnimationSimulator(simulator)
                    
                    st.success("✅ Example simulation completed!")
                    st.balloons()
                else:
                    st.error("Example data not available")
        except Exception as e:
            st.error(f"Error running example: {str(e)}")
    
    def _run_simulation(self, **kwargs):
        """Run a simulation with given parameters"""
        try:
            if not MODULES_AVAILABLE:
                st.error("Required modules not available. Please ensure all project files are in the same directory.")
                return
            
            with st.spinner("Setting up simulation..."):
                # Generate network
                generator = UltimateNetworkGenerator(population=kwargs['population'])
                
                network_type = kwargs['network_type']
                if network_type == "erdos_renyi":
                    G = generator.erdos_renyi(p=kwargs['network_params'].get('erdos_p', 0.01))
                elif network_type == "watts_strogatz":
                    G = generator.watts_strogatz(
                        k=kwargs['network_params'].get('watts_k', 8),
                        p=kwargs['network_params'].get('watts_p', 0.3)
                    )
                elif network_type == "barabasi_albert":
                    G = generator.barabasi_albert(m=kwargs['network_params'].get('barabasi_m', 3))
                elif network_type == "stochastic_block":
                    community_sizes = [kwargs['population']//4] * 4
                    G = generator.stochastic_block(
                        community_sizes,
                        intra_prob=kwargs['network_params'].get('block_intra', 0.15),
                        inter_prob=kwargs['network_params'].get('block_inter', 0.01)
                    )
                else:
                    G = generator.hybrid_multilayer()
                
                # Configure disease
                if kwargs['disease_variant'] == 'custom':
                    disease = DiseaseParameters(**kwargs['custom_params'])
                else:
                    disease = DiseaseLibrary.covid19_variant(kwargs['disease_variant'])
                
                # Create simulator
                simulator = UltimateSimulator(G, disease)
                
                # Seed infections
                simulator.seed_infections(
                    kwargs['n_seed_infections'],
                    method=kwargs['seed_method']
                )
                
                # Apply interventions
                if kwargs['intervention_scenario'] != 'no_intervention':
                    # This would normally apply interventions
                    pass
                
                # Store in session state
                st.session_state.simulator = simulator
                st.session_state.simulation_running = True
                st.session_state.animation_ready = False
                
                # Run simulation
                with st.spinner(f"Running {kwargs['simulation_days']}-day simulation..."):
                    history = simulator.run(
                        days=kwargs['simulation_days'],
                        show_progress=False
                    )
                    
                    st.session_state.simulation_history = history
                
                # Create visualizer and animator
                st.session_state.visualizer = PandemicVisualizer3D(simulator)
                st.session_state.animator = LiveAnimationSimulator(simulator)
                
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
                days = len(history['time']) if history else 0
                
                step_size = max(1, days // 100)
                days_to_animate = list(range(0, days, step_size))
                
                # Generate animation frames
                frames = []
                for day in days_to_animate:
                    frame = st.session_state.animator.generate_frame(day)
                    if frame:
                        frames.append(frame)
                
                st.session_state.animation_ready = True
                st.session_state.animation_frames = frames
                
                st.success(f"✅ Prepared {len(frames)} animation frames!")
        
        except Exception as e:
            st.error(f"Error preparing animation: {str(e)}")
    
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
            ["Epidemic Curves", "Key Metrics", "Network Analysis", "Intervention Effects", "Demographic Analysis"],
            index=0
        )
        
        if analysis_type == "Epidemic Curves":
            self._render_epidemic_curves()
        elif analysis_type == "Key Metrics":
            self._render_key_metrics()
        elif analysis_type == "Network Analysis":
            self._render_network_analysis()
        elif analysis_type == "Intervention Effects":
            self._render_intervention_analysis()
        elif analysis_type == "Demographic Analysis":
            self._render_demographic_analysis()
    
    def _render_epidemic_curves(self):
        """Render epidemic curves analysis"""
        history = st.session_state.simulation_history
        if not history:
            st.info("No simulation history available")
            return
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Susceptible vs Infected", "Recovered vs Deceased", 
                           "Cumulative Infections", "Reproduction Number"),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Plot 1: Susceptible vs Infected
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['S'], mode='lines', name='Susceptible', line=dict(color='green')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['I'], mode='lines', name='Infectious', line=dict(color='red')),
            row=1, col=1
        )
        
        # Plot 2: Recovered vs Deceased
        fig.add_trace(
            go.Scatter(x=history['time'], y=history['R'], mode='lines', name='Recovered', line=dict(color='blue')),
            row=1, col=2
        )
        if 'D' in history:
            fig.add_trace(
                go.Scatter(x=history['time'], y=history['D'], mode='lines', name='Deceased', line=dict(color='gray')),
                row=1, col=2
            )
        
        # Plot 3: Cumulative infections
        if 'total_infected' in history:
            fig.add_trace(
                go.Scatter(x=history['time'], y=history['total_infected'], mode='lines', 
                          name='Total Infected', line=dict(color='orange')),
                row=2, col=1
            )
        
        # Plot 4: R effective
        if hasattr(st.session_state.simulator, 'stats') and 'r_effective' in st.session_state.simulator.stats:
            r_eff = st.session_state.simulator.stats['r_effective']
            fig.add_trace(
                go.Scatter(x=list(range(len(r_eff))), y=r_eff, mode='lines', 
                          name='R effective', line=dict(color='purple')),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(height=600, showlegend=True, template='plotly_white')
        fig.update_xaxes(title_text="Days", row=2, col=1)
        fig.update_xaxes(title_text="Days", row=2, col=2)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="R value", row=2, col=2)
        
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
    
    def _render_key_metrics(self):
        """Render key metrics analysis"""
        # This would show detailed metrics analysis
        st.info("Key metrics analysis - to be implemented")
    
    def _render_network_analysis(self):
        """Render network analysis"""
        # This would show network metrics
        st.info("Network analysis - to be implemented")
    
    def _render_intervention_analysis(self):
        """Render intervention effects analysis"""
        # This would compare different intervention scenarios
        st.info("Intervention effects analysis - to be implemented")
    
    def _render_demographic_analysis(self):
        """Render demographic analysis"""
        # This would analyze effects by age, mobility, etc.
        st.info("Demographic analysis - to be implemented")
    
    # ==================== TAB 4: VISUALIZATION ====================
    
    def _render_visualization_tab(self):
        """Render the visualization tab"""
        st.markdown('<h2 class="sub-header">🎨 Interactive Visualization</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to visualize results")
            
            if MODULES_AVAILABLE and 'example_network' in st.session_state:
                if st.button("Show Example Network", use_container_width=True):
                    self._show_example_visualization()
            return
        
        # Visualization controls
        viz_col1, viz_col2, viz_col3 = st.columns(3)
        
        with viz_col1:
            viz_type = st.selectbox(
                "Visualization Type",
                ["3D Network", "2D Network", "Heatmap", "Animation Preview", "Disease Spread Timeline"],
                index=0
            )
        
        with viz_col2:
            color_by = st.selectbox(
                "Color Nodes By",
                ["disease_state", "age", "mobility", "degree", "community", "infection_source"],
                index=0
            )
        
        with viz_col3:
            if viz_type == "Animation Preview":
                if st.session_state.animation_frames:
                    current_day = st.slider(
                        "Animation Day",
                        0,
                        len(st.session_state.animation_frames) - 1,
                        st.session_state.current_day
                    )
                else:
                    current_day = st.slider(
                        "Day to Visualize",
                        0,
                        len(st.session_state.simulation_history['time']) - 1,
                        st.session_state.current_day
                    )
            else:
                current_day = st.slider(
                    "Day to Visualize",
                    0,
                    len(st.session_state.simulation_history['time']) - 1,
                    st.session_state.current_day
                )
            st.session_state.current_day = current_day
        
        # Generate visualization
        if st.button("🔄 Generate Visualization", type="primary", use_container_width=True):
            with st.spinner("Generating visualization..."):
                if viz_type == "3D Network":
                    self._render_3d_network(current_day, color_by)
                elif viz_type == "2D Network":
                    self._render_2d_network(current_day, color_by)
                elif viz_type == "Heatmap":
                    self._render_heatmap()
                elif viz_type == "Animation Preview":
                    self._render_animation_preview(current_day)
                elif viz_type == "Disease Spread Timeline":
                    self._render_disease_spread_timeline()
    
    def _show_example_visualization(self):
        """Show example network visualization"""
        try:
            import networkx as nx
            
            G = st.session_state.example_network
            
            # Simple 2D plot
            fig, ax = plt.subplots(figsize=(10, 8))
            pos = nx.spring_layout(G, seed=42)
            
            # Color by degree
            degrees = dict(G.degree())
            node_colors = [degrees[n] for n in G.nodes()]
            node_sizes = [50 + degrees[n] * 10 for n in G.nodes()]
            
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                 node_size=node_sizes, cmap=plt.cm.viridis, 
                                 alpha=0.8, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax)
            
            ax.set_title("Example Network Visualization", fontsize=16)
            ax.axis('off')
            
            st.pyplot(fig)
            plt.close()
            
        except Exception as e:
            st.error(f"Error showing example: {str(e)}")
    
    def _render_3d_network(self, current_day, color_by):
        """Render 3D network visualization"""
        try:
            if st.session_state.visualizer:
                fig = st.session_state.visualizer.create_interactive_3d_plot(day=current_day)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("3D visualizer not available")
        except Exception as e:
            st.error(f"Error creating 3D visualization: {str(e)}")
    
    def _render_2d_network(self, current_day, color_by):
        """Render 2D network visualization"""
        st.info("2D network visualization - to be implemented")
    
    def _render_heatmap(self):
        """Render heatmap visualization"""
        st.info("Heatmap visualization - to be implemented")
    
    def _render_animation_preview(self, current_day):
        """Render animation preview"""
        if not st.session_state.animation_frames:
            st.warning("Animation frames not prepared. Please prepare animation first.")
            return
        
        frame_idx = min(current_day, len(st.session_state.animation_frames) - 1)
        self._display_animation_frame(frame_idx)
    
    def _render_disease_spread_timeline(self):
        """Render disease spread timeline visualization"""
        st.info("Disease spread timeline - to be implemented")
    
    def _display_animation_frame(self, frame_index):
        """Display a single animation frame"""
        if not st.session_state.animation_frames:
            return
        
        try:
            frame = st.session_state.animation_frames[frame_index]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Simple visualization
                fig, ax = plt.subplots(figsize=(10, 8))
                
                # Get node positions (simplified)
                if hasattr(st.session_state.simulator, 'G'):
                    G = st.session_state.simulator.G
                    import networkx as nx
                    pos = nx.spring_layout(G, seed=42)
                    
                    # Draw network
                    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=50, alpha=0.8)
                    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
                    
                    ax.set_title(f"Day {frame_index} - Network State", fontsize=16)
                    ax.axis('off')
                    
                    st.pyplot(fig)
                    plt.close()
            
            with col2:
                st.markdown(f"### Day {frame_index}")
                
                # Display simple stats
                if 'statistics' in frame:
                    stats = frame['statistics']
                    st.metric("Susceptible", stats.get('S', 0))
                    st.metric("Infectious", stats.get('I', 0))
                    st.metric("Recovered", stats.get('R', 0))
                    if 'new_cases' in stats:
                        st.metric("New Cases", stats.get('new_cases', 0))
        
        except Exception as e:
            st.error(f"Error displaying animation frame: {str(e)}")
    
    # ==================== TAB 5: ANIMATION ====================
    
    def _render_animation_tab(self):
        """Render the animation tab"""
        st.markdown('<h2 class="sub-header">🎬 Simulation Animation</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to create animations")
            return
        
        if not st.session_state.animation_ready:
            st.warning("⚠️ Animation not prepared yet. Click 'Prepare Animation' in Overview tab or below.")
            
            if st.button("🎬 Prepare Animation Now", type="primary", use_container_width=True):
                self._prepare_animation()
                st.rerun()
            return
        
        # Animation controls
        st.markdown('<div class="animation-controls">', unsafe_allow_html=True)
        st.markdown("### 🎛️ Animation Controls")
        
        anim_col1, anim_col2, anim_col3, anim_col4 = st.columns(4)
        
        with anim_col1:
            animation_type = st.selectbox(
                "Animation Type",
                ["Interactive HTML", "GIF Video", "Streamlit Live", "Export Frames"],
                index=0
            )
        
        with anim_col2:
            fps = st.slider("FPS", 1, 30, 10, help="Frames per second for video animations")
        
        with anim_col3:
            speed = st.slider("Speed", 0.25, 4.0, 1.0, 0.25, help="Playback speed multiplier")
        
        with anim_col4:
            quality = st.select_slider(
                "Quality",
                options=["Low", "Medium", "High"],
                value="Medium"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate buttons
        gen_col1, gen_col2, gen_col3 = st.columns(3)
        
        with gen_col1:
            if st.button("🎥 Generate Interactive HTML", type="primary", use_container_width=True):
                self._generate_html_animation()
        
        with gen_col2:
            if st.button("📹 Create GIF Video", use_container_width=True):
                self._generate_gif_animation(fps, quality)
        
        with gen_col3:
            if st.button("🖼️ Export Frames", use_container_width=True):
                self._export_animation_frames()
        
        # Live animation preview
        st.markdown("---")
        st.markdown("### 👁️ Live Preview")
        
        current_day = st.slider(
            "Select Day to Preview",
            0,
            len(st.session_state.animation_frames) - 1,
            st.session_state.current_day,
            key="animation_preview_day"
        )
        
        st.session_state.current_day = current_day
        
        # Display selected frame
        if st.session_state.animation_frames:
            self._display_animation_frame(current_day)
        
        # Auto-play controls
        st.markdown("---")
        st.markdown("### ▶️ Auto-Play Animation")
        
        play_col1, play_col2, play_col3 = st.columns(3)
        
        with play_col1:
            auto_play = st.button("▶️ Play in Streamlit", use_container_width=True)
        
        with play_col2:
            loop = st.checkbox("Loop Animation", value=True)
        
        with play_col3:
            delay = st.slider("Frame Delay (ms)", 100, 2000, 500, 100)
        
        if auto_play:
            self._play_streamlit_animation(loop, delay)
    
    def _generate_html_animation(self):
        """Generate interactive HTML animation"""
        try:
            with st.spinner("Creating interactive HTML animation..."):
                st.info("HTML animation generation - to be implemented")
                # Implementation would go here
        except Exception as e:
            st.error(f"Error generating HTML animation: {str(e)}")
    
    def _generate_gif_animation(self, fps, quality):
        """Generate GIF animation"""
        try:
            with st.spinner("Creating GIF animation..."):
                st.info("GIF animation generation - to be implemented")
                # Implementation would go here
        except Exception as e:
            st.error(f"Error generating GIF: {str(e)}")
    
    def _export_animation_frames(self):
        """Export animation frames as images"""
        try:
            with st.spinner("Exporting animation frames..."):
                st.info("Frame export - to be implemented")
                # Implementation would go here
        except Exception as e:
            st.error(f"Error exporting frames: {str(e)}")
    
    def _play_streamlit_animation(self, loop, delay_ms):
        """Play animation directly in Streamlit"""
        try:
            frames = st.session_state.animation_frames
            if not frames:
                st.error("No animation frames available")
                return
            
            # Create placeholder
            animation_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animation loop
            while True:
                for i, frame in enumerate(frames):
                    progress_bar.progress((i + 1) / len(frames))
                    
                    with animation_placeholder.container():
                        self._display_animation_frame(i)
                    
                    time.sleep(delay_ms / 1000)
                
                if not loop:
                    break
            
            animation_placeholder.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Error playing animation: {str(e)}")
    
    # ==================== TAB 6: PARAMETER SWEEP ====================
    
    def _render_parameter_sweep_tab(self):
        """Render the parameter sweep tab"""
        st.markdown('<h2 class="sub-header">🔬 Parameter Sweep Analysis</h2>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        Run multiple simulations with different parameters to explore the parameter space
        and find optimal intervention strategies.
        """)
        
        # Parameter sweep configuration
        with st.form("parameter_sweep_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Sweep Configuration")
                
                exploration_type = st.selectbox(
                    "Exploration Type",
                    ["basic", "network", "disease", "interventions", "quick_test"],
                    index=0,
                    help="Type of parameter exploration"
                )
                
                n_simulations = st.slider(
                    "Number of Simulations",
                    min_value=2,
                    max_value=100,
                    value=10,
                    step=1,
                    help="Maximum number of simulations to run"
                )
                
                n_parallel = st.slider(
                    "Parallel Processes",
                    min_value=1,
                    max_value=4,
                    value=2,
                    step=1,
                    help="Number of simulations to run in parallel"
                )
            
            with col2:
                st.markdown("### 🎯 Optimization Goal")
                
                objective = st.selectbox(
                    "Optimization Objective",
                    ["minimize_deaths", "minimize_cases", "minimize_peak", "balanced"],
                    index=0,
                    help="What to optimize for"
                )
                
                save_outputs = st.checkbox(
                    "Save Detailed Outputs",
                    value=False,
                    help="Save detailed output for each simulation"
                )
                
                use_cache = st.checkbox(
                    "Use Cached Results",
                    value=True,
                    help="Reuse results from previous runs with same parameters"
                )
            
            st.markdown("---")
            run_sweep = st.form_submit_button(
                "🚀 Run Parameter Sweep",
                type="primary",
                use_container_width=True
            )
        
        if run_sweep:
            with st.spinner(f"Running {n_simulations} simulations..."):
                try:
                    sweeper = ParameterSweeper()
                    param_grid = sweeper.define_parameter_grid(exploration_type)
                    
                    results = sweeper.run_parameter_sweep(
                        parameter_grid=param_grid,
                        n_parallel=n_parallel,
                        save_all_outputs=save_outputs
                    )
                    
                    st.session_state.parameter_sweeper = sweeper
                    st.session_state.sweep_results = results
                    
                    st.success(f"✅ Parameter sweep completed! {len(results)} simulations run.")
                    
                    # Show quick results
                    if hasattr(sweeper, 'results_df') and not sweeper.results_df.empty:
                        st.dataframe(sweeper.results_df.head(), use_container_width=True)
                        
                        # Find optimal
                        optimal = sweeper.find_optimal_interventions(objective=objective)
                        if optimal:
                            st.info(f"Optimal strategy found: {optimal.get('objective_value', 'N/A')}")
                
                except Exception as e:
                    st.error(f"Error running parameter sweep: {str(e)}")
        
        # Display existing results
        if st.session_state.parameter_sweeper is not None:
            st.markdown("---")
            st.markdown("### 📋 Previous Sweep Results")
            
            sweeper = st.session_state.parameter_sweeper
            
            if hasattr(sweeper, 'results_df') and not sweeper.results_df.empty:
                st.dataframe(sweeper.results_df, use_container_width=True)
                
                # Plot key results
                if 'stat_attack_rate' in sweeper.results_df.columns:
                    fig = px.histogram(sweeper.results_df, x='stat_attack_rate',
                                      title='Distribution of Attack Rates',
                                      labels={'stat_attack_rate': 'Attack Rate'})
                    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 7: RESULTS ====================
    
    def _render_results_tab(self):
        """Render the results tab"""
        st.markdown('<h2 class="sub-header">📈 Simulation Results</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to see results")
            return
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Export Results CSV", use_container_width=True):
                self._export_results_csv()
        
        with col2:
            if st.button("📋 Export Summary", use_container_width=True):
                self._export_summary()
        
        with col3:
            if st.button("🖼️ Export Plots", use_container_width=True):
                self._export_plots()
        
        with col4:
            if st.button("📁 Export All", use_container_width=True):
                self._export_all()
        
        # Detailed results
        st.markdown("---")
        st.markdown("### 📊 Detailed Metrics")
        
        if hasattr(st.session_state.simulator, 'get_summary_stats'):
            stats = st.session_state.simulator.get_summary_stats()
            
            # Convert to dataframe for display
            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            st.dataframe(stats_df, use_container_width=True)
        
        # Simulation history
        if st.session_state.simulation_history:
            st.markdown("### 📈 Time Series Data")
            
            history_df = pd.DataFrame(st.session_state.simulation_history)
            st.dataframe(history_df.tail(20), use_container_width=True)  # Show last 20 days
    
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
                json_str = json.dumps(stats, indent=2)
                
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
    
    def _export_plots(self):
        """Export plots as images"""
        st.info("Plot export functionality - to be implemented")
    
    def _export_all(self):
        """Export all data"""
        st.info("Complete export functionality - to be implemented")

def main():
    """Main function to run the dashboard"""
    dashboard = PandemicDashboard()
    dashboard.run()

if __name__ == "__main__":
    # Check for required packages
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy', 'matplotlib']
    
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
        try:
            import networkx as nx
            from PIL import Image
            print("✅ All animation dependencies available")
        except ImportError as e:
            print(f"⚠️  Some animation features may not work: {e}")
            print("For full functionality, install:")
            print("pip install networkx pillow")
        
        print("🚀 Starting Pandemic Simulation Dashboard with Animation...")
        print("📊 Open your browser and go to http://localhost:8501")
        print("🎬 New: Dedicated Animation tab for video exports!")
        
        # Run the dashboard
        main()