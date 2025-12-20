# main_dashboard.py - COMPLETE VERSION WITH MAXIMUM PARAMETER CONTROL
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
            'simulation_complete': False,
            'intervention_schedule': None,
            'custom_interventions': [],
            'new_interv_day': 30,
            'new_interv_type': 'mask_mandate',
            'new_interv_params': '{"efficacy": 0.5, "compliance": 0.7}'
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
        
        .param-section {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border-left: 5px solid #1E88E5;
        }
        
        .param-section h4 {
            color: #1E88E5;
            margin-top: 0;
        }
        
        .advanced-params {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
        }
        
        .intervention-params {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
        }
        
        .disease-params {
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
        }
        
        .network-params {
            background-color: #d1ecf1;
            border-left: 5px solid #17a2b8;
        }
        
        .tab-content {
            padding: 1rem;
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
        """Render the overview tab with configuration guidance"""
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
            
            **🌐 Advanced Network Generation**
            - Multiple network types (Erdős–Rényi, Watts-Strogatz, Barabási–Albert)
            - Hybrid multilayer networks with households, workplaces, schools
            - Custom community structures
            
            **🦠 Comprehensive Disease Modeling**
            - Multiple COVID-19 variants (Wildtype, Alpha, Delta, Omicron)
            - Custom disease parameterization
            - Age-stratified susceptibility and severity
            
            **🛡️ Detailed Intervention Strategies**
            - Mask mandates with adjustable compliance
            - Social distancing with effectiveness settings
            - Vaccination campaigns with priority options
            - Lockdowns with strictness controls
            - Testing regimes with accuracy settings
            
            **📊 Advanced Visualization**
            - Real-time network animation
            - Epidemic curve analysis
            - Healthcare burden tracking
            - Video export (GIF/MP4) of simulations
            """)
            
            # Configuration status
            st.markdown("### ⚙️ Configuration Status")
            status_cols = st.columns(4)
            
            with status_cols[0]:
                if st.session_state.simulator:
                    st.success("✅ Simulator Ready")
                else:
                    st.warning("⏳ Not Configured")
            
            with status_cols[1]:
                if st.session_state.animation_ready:
                    st.success("✅ Animation Ready")
                else:
                    st.info("🎬 Not Prepared")
            
            with status_cols[2]:
                if st.session_state.simulation_history:
                    st.success("✅ Results Available")
                else:
                    st.info("📊 No Results")
            
            with status_cols[3]:
                if st.session_state.simulation_complete:
                    st.success("✅ Simulation Complete")
                else:
                    st.info("⚡ Not Run")
            
            # Quick start guide
            st.markdown("""
            ### 🚀 Quick Start Guide
            
            1. **Go to Simulation tab** ⬅️
            2. **Configure all parameters** (network, disease, interventions)
            3. **Review configuration summary**
            4. **Run simulation**
            5. **Watch animation** in Visualization tab
            6. **Analyze results** in Analysis tab
            7. **Export videos** in Animation tab
            
            **Pro tip:** Start with example simulation to see all features in action!
            """)
            
            # Show animation preview if available
            if st.session_state.animation_ready and st.session_state.animation_frames:
                st.markdown("### 🎬 Current Animation Preview")
                if len(st.session_state.animation_frames) > 1:
                    preview_day = st.slider("Preview Day", 0, len(st.session_state.animation_frames)-1, 0, key="preview_slider")
                    self._display_animation_frame(preview_day)
                else:
                    self._display_animation_frame(0)
        
        with col2:
            st.markdown('<h3 class="sub-header">📈 Quick Stats</h3>', 
                       unsafe_allow_html=True)
            
            # Metrics
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
            
            # Navigation
            st.markdown("### 🔍 Where to Go:")
            nav_options = {
                "⚙️ Simulation": "Configure all simulation parameters",
                "📊 Analysis": "Detailed epidemic analysis and statistics",
                "🎨 Visualization": "Network visualization and animation",
                "🎬 Animation": "Create and export videos",
                "📈 Results": "Download data and reports"
            }
            
            for nav_item, description in nav_options.items():
                st.markdown(f"**{nav_item}**")
                st.caption(description)
        
        with col3:
            st.markdown('<h3 class="sub-header">🚀 Quick Actions</h3>', 
                       unsafe_allow_html=True)
            
            # Action buttons
            if not st.session_state.simulator:
                st.info("**Start here:**")
            
            if st.button("▶️ Run Example Simulation", type="primary", use_container_width=True, key="overview_example_btn"):
                self._run_example_simulation()
            
            if st.session_state.simulator and not st.session_state.animation_ready and st.session_state.simulation_history:
                if st.button("🎬 Prepare Animation", use_container_width=True, key="overview_prepare_btn"):
                    self._prepare_animation()
            
            if st.session_state.simulator:
                if st.button("🔄 New Simulation", use_container_width=True, key="overview_new_btn"):
                    st.session_state.simulator = None
                    st.session_state.simulation_history = None
                    st.session_state.animation_ready = False
                    st.session_state.animation_frames = []
                    st.session_state.simulation_complete = False
                    st.success("Ready for new simulation!")
                    st.rerun()
            
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
            
            # Tips
            st.markdown("### 💡 Tips")
            st.markdown("""
            - Start with 500-1000 population for testing
            - Try different network structures
            - Compare intervention strategies
            - Use custom disease parameters for research
            - Export animations for presentations
            """)
    
    # ==================== TAB 2: SIMULATION ====================
    
    def _render_simulation_tab(self):
        """Render the simulation configuration tab with maximum control"""
        st.markdown('<h2 class="sub-header">⚙️ Complete Simulation Configuration</h2>', 
                   unsafe_allow_html=True)
        
        if not MODULES_AVAILABLE:
            st.error("⚠️ Required modules not available. Please check your imports.")
            st.info("Running in demonstration mode with mock data.")
        
        # Create a container for all configuration inputs (NO FORM)
        config_container = st.container()
        
        with config_container:
            # ========== SECTION 1: NETWORK CONFIGURATION ==========
            st.markdown("""
            <div class="param-section network-params">
                <h4>🌐 1. Network Configuration</h4>
                Configure the social network structure
            </div>
            """, unsafe_allow_html=True)
            
            network_col1, network_col2 = st.columns(2)
            
            with network_col1:
                st.markdown("#### Population & Type")
                
                population = st.slider(
                    "**Population Size**",
                    min_value=100,
                    max_value=10000,
                    value=1000,
                    step=100,
                    help="Total number of individuals in the network",
                    key="population_slider"
                )
                
                network_type = st.selectbox(
                    "**Network Structure Type**",
                    [
                        "hybrid_multilayer - Realistic social network with households, workplaces, schools",
                        "erdos_renyi - Random connections (Erdős–Rényi model)", 
                        "watts_strogatz - Small-world network (Watts-Strogatz model)",
                        "barabasi_albert - Scale-free network (Barabási–Albert model)",
                        "stochastic_block - Community-structured network"
                    ],
                    index=0,
                    help="Type of network structure",
                    key="network_type_select"
                )
                
                # Extract network type
                if " - " in network_type:
                    network_type = network_type.split(" - ")[0]
            
            with network_col2:
                st.markdown("#### Network Parameters")
                
                network_params = {}
                
                if network_type == "erdos_renyi":
                    network_params['erdos_p'] = st.slider(
                        "Connection Probability (p)",
                        min_value=0.001,
                        max_value=0.1,
                        value=0.01,
                        step=0.001,
                        format="%.3f",
                        key="erdos_p_slider"
                    )
                
                elif network_type == "watts_strogatz":
                    network_params['watts_k'] = st.slider(
                        "Nearest Neighbors (k)",
                        min_value=2,
                        max_value=20,
                        value=8,
                        step=1,
                        key="watts_k_slider"
                    )
                    network_params['watts_p'] = st.slider(
                        "Rewiring Probability (p)",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.3,
                        step=0.05,
                        key="watts_p_slider"
                    )
                
                elif network_type == "barabasi_albert":
                    network_params['barabasi_m'] = st.slider(
                        "New Connections (m)",
                        min_value=1,
                        max_value=10,
                        value=3,
                        step=1,
                        key="barabasi_m_slider"
                    )
                
                elif network_type == "stochastic_block":
                    n_communities = st.slider(
                        "Number of Communities",
                        min_value=2,
                        max_value=10,
                        value=4,
                        step=1,
                        key="n_communities_slider"
                    )
                    
                    # Create community sizes
                    community_sizes = []
                    remaining = population
                    for i in range(n_communities - 1):
                        size = st.slider(
                            f"Community {i+1} Size",
                            min_value=10,
                            max_value=remaining - 10 * (n_communities - i - 1),
                            value=remaining // n_communities,
                            step=10,
                            key=f"community_{i}_size"
                        )
                        community_sizes.append(size)
                        remaining -= size
                    community_sizes.append(remaining)
                    
                    network_params['community_sizes'] = community_sizes
                    network_params['block_intra'] = st.slider(
                        "Within-Community Probability",
                        min_value=0.01,
                        max_value=0.5,
                        value=0.15,
                        step=0.01,
                        key="block_intra_slider"
                    )
                    network_params['block_inter'] = st.slider(
                        "Between-Community Probability",
                        min_value=0.001,
                        max_value=0.05,
                        value=0.01,
                        step=0.001,
                        key="block_inter_slider"
                    )
                
                elif network_type == "hybrid_multilayer":
                    network_params['school_p'] = st.slider(
                        "School Connection Probability",
                        min_value=0.1,
                        max_value=1.0,
                        value=0.8,
                        step=0.05,
                        key="school_p_slider"
                    )
                    network_params['workplace_p'] = st.slider(
                        "Workplace Connection Probability",
                        min_value=0.1,
                        max_value=1.0,
                        value=0.6,
                        step=0.05,
                        key="workplace_p_slider"
                    )
                    network_params['community_p'] = st.slider(
                        "Community Connection Probability",
                        min_value=0.1,
                        max_value=1.0,
                        value=0.4,
                        step=0.05,
                        key="community_p_slider"
                    )
            
            # ========== SECTION 2: DISEASE CONFIGURATION ==========
            st.markdown("""
            <div class="param-section disease-params">
                <h4>🦠 2. Disease Configuration</h4>
                Configure disease transmission and progression parameters
            </div>
            """, unsafe_allow_html=True)
            
            disease_col1, disease_col2 = st.columns(2)
            
            with disease_col1:
                st.markdown("#### Disease Selection")
                
                disease_choice = st.selectbox(
                    "**Select Disease Model**",
                    [
                        "custom - Create custom disease parameters",
                        "omicron - COVID-19 Omicron variant (high transmission, lower severity)",
                        "delta - COVID-19 Delta variant (high transmission, higher severity)", 
                        "alpha - COVID-19 Alpha variant (moderate transmission)",
                        "wildtype - COVID-19 original strain",
                        "influenza - Seasonal influenza",
                        "measles - Measles (very high transmission)",
                        "ebola - Ebola (high mortality)",
                        "sars - SARS-CoV-1"
                    ],
                    index=1,
                    help="Select a predefined disease or create custom parameters",
                    key="disease_choice_select"
                )
                
                if " - " in disease_choice:
                    disease_variant = disease_choice.split(" - ")[0]
                else:
                    disease_variant = disease_choice
                
                # Initial infections
                n_seed_infections = st.slider(
                    "**Initial Infections**",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1,
                    help="Number of initially infected individuals",
                    key="n_seed_infections_slider"
                )
                
                seed_method = st.selectbox(
                    "**Infection Seeding Method**",
                    [
                        "random - Random individuals",
                        "hubs - Most connected individuals", 
                        "mobile - Highest mobility individuals",
                        "geographic - Cluster in one area",
                        "age_targeted - Target specific age groups"
                    ],
                    index=0,
                    help="How to select initial infections",
                    key="seed_method_select"
                )
                
                if " - " in seed_method:
                    seed_method = seed_method.split(" - ")[0]
            
            with disease_col2:
                st.markdown("#### Custom Disease Parameters")
                
                custom_params = {}
                
                if disease_variant == "custom":
                    # Basic parameters
                    custom_params['name'] = st.text_input("Disease Name", "Custom Disease", key="disease_name_input")
                    custom_params['R0'] = st.slider(
                        "**Basic Reproduction Number (R₀)**",
                        min_value=0.5,
                        max_value=20.0,
                        value=2.5,
                        step=0.1,
                        key="R0_slider"
                    )
                    
                    custom_params['generation_time'] = st.slider(
                        "**Generation Time (days)**",
                        min_value=1.0,
                        max_value=20.0,
                        value=5.2,
                        step=0.1,
                        key="generation_time_slider"
                    )
                    
                    # Incubation period
                    st.markdown("##### Incubation Period")
                    incubation_mean = st.slider(
                        "Mean (days)",
                        min_value=1.0,
                        max_value=21.0,
                        value=5.2,
                        step=0.1,
                        key="inc_mean_slider"
                    )
                    incubation_std = st.slider(
                        "Standard Deviation (days)",
                        min_value=0.1,
                        max_value=7.0,
                        value=2.8,
                        step=0.1,
                        key="inc_std_slider"
                    )
                    custom_params['incubation_period'] = {'mean': incubation_mean, 'std': incubation_std}
                    
                    # Infectious period
                    st.markdown("##### Infectious Period")
                    infectious_mean = st.slider(
                        "Mean (days)",
                        min_value=3.0,
                        max_value=30.0,
                        value=10.0,
                        step=0.5,
                        key="inf_mean_slider"
                    )
                    infectious_std = st.slider(
                        "Standard Deviation (days)",
                        min_value=0.5,
                        max_value=10.0,
                        value=3.0,
                        step=0.1,
                        key="inf_std_slider"
                    )
                    custom_params['infectious_period'] = {'mean': infectious_mean, 'std': infectious_std}
                    
                    # Severity probabilities
                    st.markdown("##### Severity Probabilities")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        custom_params['p_asymptomatic'] = st.slider(
                            "Asymptomatic",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.4,
                            step=0.01,
                            key="p_asymptomatic_slider"
                        )
                    with col_b:
                        custom_params['p_mild'] = st.slider(
                            "Mild",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.4,
                            step=0.01,
                            key="p_mild_slider"
                        )
                    with col_c:
                        custom_params['p_severe'] = st.slider(
                            "Severe",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.15,
                            step=0.01,
                            key="p_severe_slider"
                        )
                    with col_d:
                        custom_params['p_critical'] = st.slider(
                            "Critical",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.05,
                            step=0.01,
                            key="p_critical_slider"
                        )
                    
                    # Outcomes
                    st.markdown("##### Outcomes")
                    custom_params['hospitalization_rate'] = st.slider(
                        "Hospitalization Rate",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.15,
                        step=0.01,
                        key="hospitalization_rate_slider"
                    )
                    custom_params['icu_rate'] = st.slider(
                        "ICU Rate (of hospitalized)",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.05,
                        step=0.01,
                        key="icu_rate_slider"
                    )
                    custom_params['mortality_rate'] = st.slider(
                        "Mortality Rate",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.02,
                        step=0.001,
                        format="%.3f",
                        key="mortality_rate_slider"
                    )
                    
                    # Vaccine parameters
                    st.markdown("##### Vaccine Parameters")
                    vaccine_col1, vaccine_col2 = st.columns(2)
                    with vaccine_col1:
                        custom_params['vaccine_efficacy'] = {
                            'infection': st.slider(
                                "Infection Efficacy",
                                min_value=0.0,
                                max_value=1.0,
                                value=0.9,
                                step=0.01,
                                key="vac_inf_eff_slider"
                            ),
                            'severity': st.slider(
                                "Severity Efficacy",
                                min_value=0.0,
                                max_value=1.0,
                                value=0.95,
                                step=0.01,
                                key="vac_sev_eff_slider"
                            )
                        }
                    with vaccine_col2:
                        custom_params['vaccine_efficacy']['transmission'] = st.slider(
                            "Transmission Reduction",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.5,
                            step=0.01,
                            key="vac_trans_red_slider"
                        )
                        custom_params['vaccine_efficacy']['waning_start'] = st.slider(
                            "Waning Start (days)",
                            min_value=30,
                            max_value=365,
                            value=180,
                            step=10,
                            key="vac_waning_start_slider"
                        )
                        custom_params['vaccine_efficacy']['waning_rate'] = st.slider(
                            "Waning Rate (daily)",
                            min_value=0.0,
                            max_value=0.01,
                            value=0.001,
                            step=0.0001,
                            format="%.4f",
                            key="vac_waning_rate_slider"
                        )
                else:
                    # Reset custom_params for non-custom diseases
                    custom_params = {}
            
            # ========== SECTION 3: INTERVENTION CONFIGURATION ==========
            st.markdown("""
            <div class="param-section intervention-params">
                <h4>🛡️ 3. Intervention Configuration</h4>
                Configure public health interventions and their timing
            </div>
            """, unsafe_allow_html=True)
            
            intervention_tab1, intervention_tab2, intervention_tab3 = st.tabs([
                "📅 Intervention Schedule",
                "⚡ Intervention Parameters",
                "🎯 Custom Schedule"
            ])
            
            with intervention_tab1:
                inter_col1, inter_col2 = st.columns(2)
                
                with inter_col1:
                    st.markdown("#### Intervention Scenario")
                    
                    intervention_scenario = st.selectbox(
                        "**Select Intervention Strategy**",
                        [
                            "no_intervention - No interventions",
                            "delayed_response - Delayed but effective measures", 
                            "rapid_response - Early and strong measures",
                            "herd_immunity - Focus on vaccination",
                            "full_lockdown - Strict lockdown scenario",
                            "custom - Custom intervention schedule"
                        ],
                        index=1,
                        help="Predefined intervention scenarios",
                        key="intervention_scenario_select"
                    )
                    
                    if " - " in intervention_scenario:
                        intervention_scenario = intervention_scenario.split(" - ")[0]
                    
                    simulation_days = st.slider(
                        "**Simulation Duration (days)**",
                        min_value=30,
                        max_value=365,
                        value=120,
                        step=10,
                        key="simulation_days_slider"
                    )
                
                with inter_col2:
                    st.markdown("#### Scenario Description")
                    
                    scenario_descriptions = {
                        "no_intervention": "No public health interventions. Natural disease progression.",
                        "delayed_response": "Interventions start after 30 days. Includes mask mandates, social distancing, and phased vaccination.",
                        "rapid_response": "Early interventions starting at day 7. Intensive testing, masking, and travel restrictions.",
                        "herd_immunity": "Focus on rapid vaccination to achieve herd immunity. Minimal non-pharmaceutical interventions.",
                        "full_lockdown": "Strict lockdown starting at day 14. Complete travel restrictions, mandatory masking, and isolation.",
                        "custom": "Create your own intervention schedule in the Custom Schedule tab."
                    }
                    
                    if intervention_scenario in scenario_descriptions:
                        st.info(scenario_descriptions[intervention_scenario])
            
            with intervention_tab2:
                st.markdown("#### Intervention Parameters")
                
                # General compliance
                base_compliance = st.slider(
                    "**General Population Compliance**",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.05,
                    help="Baseline compliance rate for all interventions",
                    key="base_compliance_slider"
                )
                
                # Mask parameters
                mask_col1, mask_col2 = st.columns(2)
                with mask_col1:
                    mask_efficacy = st.slider(
                        "**Mask Efficacy**",
                        min_value=0.0,
                        max_value=0.9,
                        value=0.5,
                        step=0.05,
                        help="Effectiveness of masks at reducing transmission",
                        key="mask_efficacy_slider"
                    )
                with mask_col2:
                    mask_compliance = st.slider(
                        "**Mask Compliance**",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.8,
                        step=0.05,
                        help="Percentage of population wearing masks",
                        key="mask_compliance_slider"
                    )
                
                # Social distancing
                sd_col1, sd_col2 = st.columns(2)
                with sd_col1:
                    distancing_effect = st.slider(
                        "**Social Distancing Effectiveness**",
                        min_value=0.0,
                        max_value=0.8,
                        value=0.3,
                        step=0.05,
                        help="How effective social distancing is at reducing contacts",
                        key="distancing_effect_slider"
                    )
                with sd_col2:
                    distancing_compliance = st.slider(
                        "**Distancing Compliance**",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.6,
                        step=0.05,
                        key="distancing_compliance_slider"
                    )
                
                # Vaccination
                vax_col1, vax_col2 = st.columns(2)
                with vax_col1:
                    vaccination_rate = st.slider(
                        "**Daily Vaccination Rate**",
                        min_value=0.0,
                        max_value=0.05,
                        value=0.005,
                        step=0.001,
                        format="%.3f",
                        key="vaccination_rate_slider"
                    )
                    vaccine_efficacy = st.slider(
                        "**Vaccine Efficacy**",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.9,
                        step=0.01,
                        key="vaccine_efficacy_slider"
                    )
                with vax_col2:
                    vaccination_priority = st.selectbox(
                        "**Vaccination Priority**",
                        ["age", "frontline", "random", "vulnerable"],
                        index=0,
                        help="Which groups to vaccinate first",
                        key="vaccination_priority_select"
                    )
                
                # Testing
                test_col1, test_col2 = st.columns(2)
                with test_col1:
                    testing_rate = st.slider(
                        "**Daily Testing Rate**",
                        min_value=0.0,
                        max_value=0.1,
                        value=0.05,
                        step=0.01,
                        key="testing_rate_slider"
                    )
                    testing_accuracy = st.slider(
                        "**Test Accuracy**",
                        min_value=0.5,
                        max_value=1.0,
                        value=0.95,
                        step=0.01,
                        key="testing_accuracy_slider"
                    )
                with test_col2:
                    testing_delay = st.slider(
                        "**Test Result Delay (days)**",
                        min_value=0,
                        max_value=7,
                        value=2,
                        step=1,
                        key="testing_delay_slider"
                    )
                    isolation_compliance = st.slider(
                        "**Isolation Compliance**",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.8,
                        step=0.05,
                        key="isolation_compliance_slider"
                    )
                
                # Lockdown parameters
                if intervention_scenario in ["delayed_response", "rapid_response", "full_lockdown"]:
                    lock_col1, lock_col2 = st.columns(2)
                    with lock_col1:
                        lockdown_strictness = st.slider(
                            "**Lockdown Strictness**",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.7,
                            step=0.05,
                            key="lockdown_strictness_slider"
                        )
                    with lock_col2:
                        lockdown_duration = st.slider(
                            "**Lockdown Duration (days)**",
                            min_value=7,
                            max_value=90,
                            value=30,
                            step=7,
                            key="lockdown_duration_slider"
                        )
                else:
                    lockdown_strictness = 0.0
                    lockdown_duration = 0
            
            with intervention_tab3:
                st.markdown("#### Custom Intervention Schedule")
                st.info("Create your own intervention timeline")
                
                # Display current custom interventions
                if st.session_state.custom_interventions:
                    st.markdown("##### Current Schedule")
                    for i, interv in enumerate(st.session_state.custom_interventions):
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col1:
                            st.write(f"**Day {interv['day']}**")
                        with col2:
                            st.write(f"{interv['type']}: {interv['params']}")
                        with col3:
                            if st.button(f"Remove {i}", key=f"remove_{i}"):
                                st.session_state.custom_interventions.pop(i)
                                st.rerun()
                else:
                    st.info("No custom interventions added yet.")
                
                # Inputs for new intervention
                st.markdown("---")
                st.markdown("##### Add New Intervention")
                col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
                with col_a:
                    new_interv_day = st.number_input("Day", min_value=0, max_value=365, 
                                                    value=st.session_state.new_interv_day, 
                                                    key="new_day_input")
                with col_b:
                    new_interv_type = st.selectbox(
                        "Type",
                        ["mask_mandate", "social_distancing", "vaccination", "testing", 
                         "lockdown", "travel_restrictions", "reopen"],
                        index=0,
                        key="new_type_select"
                    )
                with col_c:
                    new_interv_params = st.text_input("Parameters (JSON)", 
                                                    value=st.session_state.new_interv_params,
                                                    key="new_params_input")
                with col_d:
                    # This button is outside any form
                    if st.button("Add", use_container_width=True, key="add_interv_btn"):
                        try:
                            params = json.loads(new_interv_params)
                            st.session_state.custom_interventions.append({
                                'day': new_interv_day,
                                'type': new_interv_type,
                                'params': params
                            })
                            st.session_state.new_interv_day = 30
                            st.session_state.new_interv_type = 'mask_mandate'
                            st.session_state.new_interv_params = '{"efficacy": 0.5, "compliance": 0.7}'
                            st.success("Added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Invalid JSON: {str(e)}")
            
            # ========== SECTION 4: SIMULATION SETTINGS ==========
            st.markdown("""
            <div class="param-section advanced-params">
                <h4>⚡ 4. Simulation & Animation Settings</h4>
                Configure simulation execution and visualization
            </div>
            """, unsafe_allow_html=True)
            
            sim_col1, sim_col2 = st.columns(2)
            
            with sim_col1:
                st.markdown("#### Animation Settings")
                
                animate_simulation = st.checkbox(
                    "**Enable Animation Recording**",
                    value=True,
                    help="Record simulation states for animation",
                    key="animate_simulation_checkbox"
                )
                
                if animate_simulation:
                    animation_step = st.slider(
                        "**Animation Step Size**",
                        min_value=1,
                        max_value=10,
                        value=2,
                        step=1,
                        help="Days between animation frames",
                        key="animation_step_slider"
                    )
                else:
                    animation_step = 1
                
                save_checkpoints = st.checkbox(
                    "**Save Simulation Checkpoints**",
                    value=True,
                    help="Save intermediate states for restarting simulations",
                    key="save_checkpoints_checkbox"
                )
            
            with sim_col2:
                st.markdown("#### Advanced Settings")
                
                show_progress = st.checkbox(
                    "**Show Progress Bar**",
                    value=True,
                    key="show_progress_checkbox"
                )
                
                random_seed = st.number_input(
                    "**Random Seed**",
                    min_value=0,
                    max_value=10000,
                    value=42,
                    step=1,
                    help="For reproducible simulations",
                    key="random_seed_input"
                )
                
                save_results = st.checkbox(
                    "**Save Results to File**",
                    value=True,
                    key="save_results_checkbox"
                )
            
            # ========== RUN SIMULATION ==========
            st.markdown("---")
            st.markdown("### 🚀 Ready to Run Simulation")
            
            # Configuration summary
            with st.expander("📋 Configuration Summary", expanded=True):
                sum_col1, sum_col2, sum_col3 = st.columns(3)
                
                with sum_col1:
                    st.markdown("**Network**")
                    st.caption(f"Population: {population}")
                    st.caption(f"Type: {network_type}")
                    if network_params:
                        for key, val in network_params.items():
                            if key != 'community_sizes':
                                st.caption(f"{key}: {val}")
                
                with sum_col2:
                    st.markdown("**Disease**")
                    st.caption(f"Model: {disease_variant}")
                    if disease_variant == "custom":
                        st.caption(f"R₀: {custom_params.get('R0', 'N/A')}")
                    else:
                        disease_info = {
                            "omicron": "R₀: 9.5",
                            "delta": "R₀: 5.0", 
                            "alpha": "R₀: 4.0",
                            "wildtype": "R₀: 2.5",
                            "influenza": "R₀: 1.3",
                            "measles": "R₀: 15.0",
                            "ebola": "R₀: 1.8",
                            "sars": "R₀: 3.0"
                        }
                        st.caption(disease_info.get(disease_variant, ""))
                    st.caption(f"Initial cases: {n_seed_infections}")
                
                with sum_col3:
                    st.markdown("**Interventions**")
                    st.caption(f"Scenario: {intervention_scenario}")
                    st.caption(f"Duration: {simulation_days} days")
                    if animate_simulation:
                        st.caption(f"Animation: Enabled (step: {animation_step})")
            
            # Run button - NO FORM, just a regular button
            run_col1, run_col2, run_col3 = st.columns([1, 2, 1])
            with run_col2:
                run_simulation = st.button(
                    "🚀 **RUN SIMULATION NOW**",
                    type="primary",
                    use_container_width=True,
                    key="run_simulation_btn"
                )
        
        # Handle button click outside the container
        if run_simulation:
            # Store all parameters
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
                'base_compliance': base_compliance,
                'mask_efficacy': mask_efficacy,
                'mask_compliance': mask_compliance,
                'distancing_effect': distancing_effect,
                'distancing_compliance': distancing_compliance,
                'vaccination_rate': vaccination_rate,
                'vaccine_efficacy': vaccine_efficacy,
                'vaccination_priority': vaccination_priority,
                'testing_rate': testing_rate,
                'testing_accuracy': testing_accuracy,
                'testing_delay': testing_delay,
                'isolation_compliance': isolation_compliance,
                'lockdown_strictness': lockdown_strictness,
                'lockdown_duration': lockdown_duration,
                'animate_simulation': animate_simulation,
                'animation_step': animation_step,
                'show_progress': show_progress,
                'random_seed': random_seed,
                'save_results': save_results,
                'custom_interventions': st.session_state.custom_interventions if intervention_scenario == 'custom' else []
            }
            
            # Run the simulation
            self._run_simulation(st.session_state.simulation_params)
    
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
                    # Remove show_progress parameter if it causes issues
                    try:
                        history, checkpoints = simulator.run_with_animation(
                            days=60,
                            save_checkpoints=True,
                            checkpoint_interval=2
                        )
                    except TypeError:
                        # Fallback if run_with_animation doesn't accept save_checkpoints
                        history = simulator.run(days=60, show_progress=False)
                        checkpoints = {}
                    
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
                network_params = params['network_params']
                
                if network_type == "erdos_renyi":
                    G = generator.erdos_renyi(p=network_params.get('erdos_p', 0.01))
                elif network_type == "watts_strogatz":
                    G = generator.watts_strogatz(
                        k=network_params.get('watts_k', 8),
                        p=network_params.get('watts_p', 0.3)
                    )
                elif network_type == "barabasi_albert":
                    G = generator.barabasi_albert(m=network_params.get('barabasi_m', 3))
                elif network_type == "stochastic_block":
                    community_sizes = network_params.get('community_sizes', [params['population']//4] * 4)
                    G = generator.stochastic_block(
                        community_sizes,
                        intra_prob=network_params.get('block_intra', 0.15),
                        inter_prob=network_params.get('block_inter', 0.01)
                    )
                elif network_type == "hybrid_multilayer":
                    G = generator.hybrid_multilayer(
                        school_p=network_params.get('school_p', 0.8),
                        workplace_p=network_params.get('workplace_p', 0.6),
                        community_p=network_params.get('community_p', 0.4)
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
                run_days = params['simulation_days']
                
                if params['animate_simulation'] and hasattr(simulator, 'run_with_animation'):
                    with st.spinner(f"Running {run_days}-day simulation with animation..."):
                        try:
                            history, checkpoints = simulator.run_with_animation(
                                days=run_days,
                                save_checkpoints=True,
                                checkpoint_interval=params['animation_step']
                            )
                            simulator.checkpoints = checkpoints
                            st.session_state.checkpoints = checkpoints
                        except TypeError as e:
                            st.warning(f"Animation checkpointing failed: {e}. Running without checkpoints.")
                            history = simulator.run(days=run_days, show_progress=False)
                else:
                    with st.spinner(f"Running {run_days}-day simulation..."):
                        history = simulator.run(
                            days=run_days,
                            show_progress=params['show_progress']
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
            ["Epidemic Curves", "Network Analysis", "Disease Spread", "Intervention Effects", "Detailed Statistics"],
            index=0,
            key="analysis_type"
        )
        
        if analysis_type == "Epidemic Curves":
            self._render_epidemic_curves()
        elif analysis_type == "Network Analysis":
            self._render_network_analysis()
        elif analysis_type == "Disease Spread":
            self._render_disease_spread_analysis()
        elif analysis_type == "Intervention Effects":
            self._render_intervention_analysis()
        elif analysis_type == "Detailed Statistics":
            self._render_detailed_statistics()
    
    def _render_epidemic_curves(self):
        """Render epidemic curves analysis - SIMPLIFIED VERSION"""
        history = st.session_state.simulation_history
        if not history:
            st.info("No simulation history available")
            return
        
        # Create separate plots instead of subplots
        tab1, tab2, tab3, tab4 = st.tabs([
            "Disease Dynamics", 
            "Daily New Cases", 
            "Healthcare Burden", 
            "State Distribution"
        ])
        
        with tab1:
            # Disease Dynamics
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=history['time'], y=history['S'], 
                mode='lines', name='Susceptible', 
                line=dict(color='green', width=2)
            ))
            fig1.add_trace(go.Scatter(
                x=history['time'], y=history['I'], 
                mode='lines', name='Infectious', 
                line=dict(color='red', width=2)
            ))
            fig1.add_trace(go.Scatter(
                x=history['time'], y=history['R'], 
                mode='lines', name='Recovered', 
                line=dict(color='blue', width=2)
            ))
            if 'D' in history:
                fig1.add_trace(go.Scatter(
                    x=history['time'], y=history['D'], 
                    mode='lines', name='Deceased', 
                    line=dict(color='gray', width=2)
                ))
            fig1.update_layout(
                title="Disease Dynamics Over Time",
                xaxis_title="Days",
                yaxis_title="Count",
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            # Daily New Cases
            if 'new_infections' in history:
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=history['time'], y=history['new_infections'],
                    name='New Cases', marker_color='orange'
                ))
                fig2.update_layout(
                    title="Daily New Infections",
                    xaxis_title="Days",
                    yaxis_title="New Cases",
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            # Healthcare Burden
            fig3 = go.Figure()
            if 'Ih' in history:
                fig3.add_trace(go.Scatter(
                    x=history['time'], y=history['Ih'],
                    mode='lines', name='Hospitalized',
                    line=dict(color='purple', width=2)
                ))
            if 'Ic' in history:
                fig3.add_trace(go.Scatter(
                    x=history['time'], y=history['Ic'],
                    mode='lines', name='Critical/ICU',
                    line=dict(color='black', width=2)
                ))
            fig3.update_layout(
                title="Healthcare System Burden",
                xaxis_title="Days",
                yaxis_title="Patients",
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab4:
            # State Distribution (pie chart)
            if history['time']:
                final_day = len(history['time']) - 1
                states = ['S', 'I', 'R', 'D']
                values = []
                state_names = {
                    'S': 'Susceptible',
                    'I': 'Infectious', 
                    'R': 'Recovered',
                    'D': 'Deceased'
                }
                
                for state in states:
                    if state in history and len(history[state]) > final_day:
                        values.append(history[state][final_day])
                    else:
                        values.append(0)
                
                if sum(values) > 0:
                    fig4 = go.Figure(data=[go.Pie(
                        labels=[state_names.get(s, s) for s in states],
                        values=values,
                        marker=dict(colors=['green', 'red', 'blue', 'gray']),
                        hole=0.3
                    )])
                    fig4.update_layout(
                        title=f"Final State Distribution (Day {final_day})",
                        template='plotly_white',
                        height=500
                    )
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.info("No data available for final state distribution")
        
        # Summary statistics
        if hasattr(st.session_state.simulator, 'get_summary_stats'):
            try:
                stats = st.session_state.simulator.get_summary_stats()
                
                st.markdown("### 📊 Summary Statistics")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Attack Rate", f"{stats.get('attack_rate', 0)*100:.1f}%", key="metric_ar")
                with col2:
                    st.metric("Peak Infections", f"{stats.get('peak_infections', 0):.0f}", key="metric_pi")
                with col3:
                    st.metric("Total Deaths", f"{stats.get('total_deaths', 0):.0f}", key="metric_td")
                with col4:
                    st.metric("Case Fatality", f"{stats.get('case_fatality_rate', 0)*100:.2f}%", key="metric_cfr")
                with col5:
                    st.metric("Total Vaccinated", f"{stats.get('total_vaccinated', 0):.0f}", key="metric_tv")
            except:
                pass
    
    def _render_network_analysis(self):
        """Render network analysis"""
        if st.session_state.network_graph is None:
            st.info("No network available for analysis")
            return
        
        G = st.session_state.network_graph
        
        st.markdown("### 📐 Network Structure Analysis")
        
        # Basic metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Nodes", G.number_of_nodes(), key="metric_nodes")
        with col2:
            st.metric("Edges", G.number_of_edges(), key="metric_edges")
        with col3:
            st.metric("Density", f"{nx.density(G):.4f}", key="metric_density")
        with col4:
            degrees = [d for _, d in G.degree()]
            st.metric("Avg Degree", f"{np.mean(degrees):.2f}", key="metric_avg_deg")
        with col5:
            st.metric("Max Degree", f"{max(degrees):.0f}", key="metric_max_deg")
        
        # Degree distribution
        st.markdown("### 📊 Degree Distribution")
        fig = px.histogram(x=degrees, nbins=30, 
                          labels={'x': 'Degree', 'y': 'Count'},
                          title='Node Degree Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        # Network visualization
        st.markdown("### 🌐 Network Visualization")
        viz_type = st.selectbox("Visualization Type", ["Force-directed", "Circular", "Random"], key="viz_type_network")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if viz_type == "Force-directed":
            pos = nx.spring_layout(G, seed=42)
        elif viz_type == "Circular":
            pos = nx.circular_layout(G)
        else:
            pos = nx.random_layout(G)
        
        # Color by degree
        node_colors = [G.degree(n) for n in G.nodes()]
        node_sizes = [50 + G.degree(n) * 5 for n in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                             node_size=node_sizes, cmap=plt.cm.viridis, 
                             alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax)
        
        ax.set_title(f"Network Visualization - {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        ax.axis('off')
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, 
                                 norm=plt.Normalize(vmin=min(node_colors), 
                                                   vmax=max(node_colors)))
        sm.set_array([])
        plt.colorbar(sm, ax=ax, label='Node Degree')
        
        st.pyplot(fig)
        plt.close()
    
    def _render_disease_spread_analysis(self):
        """Render disease spread analysis"""
        if not st.session_state.simulation_history:
            st.info("No simulation history available")
            return
        
        history = st.session_state.simulation_history
        
        # Cumulative infections
        st.markdown("### 📈 Cumulative Infections")
        
        if 'total_infected' not in history and 'I' in history and 'R' in history:
            # Calculate cumulative infections
            total_infected = []
            cumulative = 0
            for i in range(len(history['time'])):
                if i > 0:
                    new_cases = (history['I'][i] + history['R'][i]) - (history['I'][i-1] + history['R'][i-1])
                    cumulative += max(0, new_cases)
                total_infected.append(cumulative)
            
            history['total_infected'] = total_infected
        
        if 'total_infected' in history:
            fig = go.Figure()
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
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Infection rate (R-effective)
        st.markdown("### 🔄 Effective Reproduction Number (R-effective)")
        
        if hasattr(st.session_state.simulator, 'stats') and 'r_effective' in st.session_state.simulator.stats:
            r_eff = st.session_state.simulator.stats['r_effective']
            if r_eff:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(len(r_eff))),
                    y=r_eff,
                    mode='lines',
                    name='R-effective',
                    line=dict(color='blue', width=2)
                ))
                fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                            annotation_text="Epidemic Threshold")
                fig.update_layout(
                    title='Effective Reproduction Number Over Time',
                    xaxis_title='Days',
                    yaxis_title='R-effective',
                    template='plotly_white',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_intervention_analysis(self):
        """Render intervention effects analysis"""
        st.markdown("### 🛡️ Intervention Analysis")
        
        if not st.session_state.simulation_history:
            st.info("No simulation history available")
            return
        
        history = st.session_state.simulation_history
        
        # Show intervention effects if available
        if 'interventions' in history and len(history['interventions']) > 0:
            # Extract intervention days
            intervention_days = []
            intervention_types = []
            
            for i, interv_dict in enumerate(history['interventions']):
                if interv_dict:  # Not empty
                    # Find first intervention day
                    for day, interv_list in enumerate(history['interventions']):
                        if interv_list:
                            intervention_days.append(day)
                            intervention_types.append(list(interv_list.keys())[0])
                            break
            
            if intervention_days:
                fig = go.Figure()
                
                # Plot infections
                fig.add_trace(go.Scatter(
                    x=history['time'],
                    y=history['I'],
                    mode='lines',
                    name='Infectious',
                    line=dict(color='red', width=2)
                ))
                
                # Add intervention markers
                for day, interv_type in zip(intervention_days, intervention_types):
                    fig.add_vline(x=day, line_dash="dash", line_color="green",
                                annotation_text=interv_type, annotation_position="top")
                
                fig.update_layout(
                    title='Intervention Effects on Infections',
                    xaxis_title='Days',
                    yaxis_title='Infectious Individuals',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Comparative analysis section
        st.markdown("#### 📊 Comparative Analysis")
        st.info("Run multiple simulations with different interventions to compare outcomes")
        
        if st.button("Run Intervention Comparison Study", use_container_width=True, key="intervention_compare"):
            st.info("This would run multiple simulations with different intervention scenarios")
            st.info("Feature coming soon: Compare mask mandates vs. social distancing vs. vaccination")
    
    def _render_detailed_statistics(self):
        """Render detailed statistics"""
        if not st.session_state.simulator:
            st.info("No simulator available")
            return
        
        try:
            stats = st.session_state.simulator.get_summary_stats()
            
            st.markdown("### 📋 Complete Simulation Statistics")
            
            # Create metrics in columns
            metric_groups = [
                ["initial_population", "final_susceptible", "total_infected", "total_recovered", "total_deaths"],
                ["peak_infections", "peak_day", "attack_rate", "case_fatality_rate", "total_vaccinated"],
                ["total_hospitalized", "total_days", "final_r_effective", "avg_daily_cases", "doubling_time"]
            ]
            
            for group in metric_groups:
                cols = st.columns(len(group))
                for i, metric in enumerate(group):
                    with cols[i]:
                        if metric in stats:
                            value = stats[metric]
                            if isinstance(value, float):
                                if 'rate' in metric:
                                    display = f"{value:.2%}"
                                else:
                                    display = f"{value:.2f}"
                            else:
                                display = f"{value:,}"
                            
                            # Format metric name
                            name = metric.replace('_', ' ').title()
                            st.metric(name, display, key=f"detailed_{metric}")
            
            # Detailed data table
            st.markdown("### 📈 Time Series Summary")
            if st.session_state.simulation_history:
                df = pd.DataFrame(st.session_state.simulation_history)
                st.dataframe(df.describe(), use_container_width=True)
                
        except Exception as e:
            st.error(f"Could not load statistics: {e}")
    
    # ==================== TAB 4: VISUALIZATION ====================
    
    def _render_visualization_tab(self):
        """Render the visualization tab"""
        st.markdown('<h2 class="sub-header">🎨 Interactive Visualization</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.simulator is None:
            st.info("👈 Run a simulation first to visualize results")
            return
        
        # Visualization controls
        viz_type = st.selectbox(
            "Visualization Type",
            ["Network Spread Animation", "Static Network", "3D Network", "Heatmap", "Timeline"],
            index=0,
            key="viz_type_main"
        )
        
        if viz_type == "Network Spread Animation":
            self._render_network_spread_animation()
        elif viz_type == "Static Network":
            self._render_static_network()
        elif viz_type == "3D Network":
            self._render_3d_network()
        elif viz_type == "Heatmap":
            self._render_heatmap()
        elif viz_type == "Timeline":
            self._render_timeline()
    
    def _render_network_spread_animation(self):
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
        
        # Get current day
        if len(st.session_state.animation_frames) > 1:
            current_day = st.slider(
                "Select Day",
                0,
                len(st.session_state.animation_frames) - 1,
                min(st.session_state.current_day, len(st.session_state.animation_frames) - 1),
                key="animation_day_slider"
            )
            st.session_state.current_day = current_day
        else:
            current_day = 0
        
        # Get frame
        frame_idx = min(current_day, len(st.session_state.animation_frames) - 1)
        frame = st.session_state.animation_frames[frame_idx]
        
        # Create visualization
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Network visualization
            st.markdown(f"#### Network State - Day {frame['day']}")
            
            fig, ax = plt.subplots(figsize=(12, 10))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
            
            G = st.session_state.network_graph
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5, edge_color='gray')
            
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
                anim_col1, anim_col2 = st.columns(2)
                
                with anim_col1:
                    if st.button("▶️ Play Animation", use_container_width=True, key="play_anim_btn"):
                        self._play_animation_in_place()
                
                with anim_col2:
                    speed = st.slider("Speed", 0.25, 4.0, 1.0, 0.25, key="anim_speed")
        
        with col2:
            # Statistics
            st.markdown("#### 📊 Statistics")
            
            stats = frame['statistics']
            
            metric_cols = st.columns(2)
            
            with metric_cols[0]:
                st.metric("Susceptible", stats.get('S', 0), key="stat_s")
                st.metric("Exposed", stats.get('E', 0), key="stat_e")
            
            with metric_cols[1]:
                st.metric("Infectious", stats.get('I', 0), key="stat_i")
                st.metric("Recovered", stats.get('R', 0), key="stat_r")
            
            if 'new_cases' in stats:
                st.metric("New Cases", stats.get('new_cases', 0), key="stat_new")
            
            # State distribution
            st.markdown("#### 📈 State Distribution")
            
            state_counts = {}
            for state in frame['node_states'].values():
                state_counts[state] = state_counts.get(state, 0) + 1
            
            if state_counts:
                fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
                
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
            time.sleep(0.3)
        
        # Clear placeholder when done
        animation_placeholder.empty()
    
    def _display_animation_frame_simple(self, frame, frame_idx):
        """Display a simple animation frame"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
            
            G = st.session_state.network_graph
            
            # Draw network
            node_colors = frame['node_colors']
            
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
            nx.draw_networkx_nodes(G, pos, 
                                  node_color=node_colors,
                                  node_size=50,
                                  ax=ax)
            
            ax.set_title(f"Day {frame['day']} - Frame {frame_idx+1}/{len(st.session_state.animation_frames)}")
            ax.axis('off')
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            stats = frame['statistics']
            st.metric("Day", frame['day'], key="simple_day")
            st.metric("Infectious", stats.get('I', 0), key="simple_i")
            st.metric("New Cases", stats.get('new_cases', 0), key="simple_new")
    
    def _render_static_network(self):
        """Render static network visualization"""
        if st.session_state.network_graph is None:
            st.info("No network available")
            return
        
        G = st.session_state.network_graph
        
        st.markdown("### 🌐 Network Structure")
        
        # Visualization options
        col1, col2 = st.columns(2)
        
        with col1:
            layout_type = st.selectbox(
                "Layout Algorithm",
                ["spring", "circular", "kamada_kawai", "spectral", "random"],
                index=0,
                key="static_layout"
            )
        
        with col2:
            color_by = st.selectbox(
                "Color Nodes By",
                ["degree", "age", "mobility", "state", "community"],
                index=0,
                key="static_color"
            )
        
        # Compute layout
        if layout_type == "spring":
            pos = nx.spring_layout(G, seed=42, iterations=100)
        elif layout_type == "circular":
            pos = nx.circular_layout(G)
        elif layout_type == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif layout_type == "spectral":
            pos = nx.spectral_layout(G)
        else:
            pos = nx.random_layout(G)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Determine node colors
        if color_by == "degree":
            node_colors = [G.degree(n) for n in G.nodes()]
            cmap = plt.cm.viridis
            colorbar_label = "Node Degree"
        elif color_by == "age":
            node_colors = [G.nodes[n].get('age', 40) for n in G.nodes()]
            cmap = plt.cm.plasma
            colorbar_label = "Age"
        elif color_by == "mobility":
            node_colors = [G.nodes[n].get('mobility', 0.5) for n in G.nodes()]
            cmap = plt.cm.coolwarm
            colorbar_label = "Mobility"
        elif color_by == "state":
            node_colors = []
            for n in G.nodes():
                state = G.nodes[n].get('state', 'S')
                color_map = {'S': 0, 'E': 1, 'I': 2, 'R': 3, 'D': 4, 'V': 5}
                node_colors.append(color_map.get(state, 0))
            cmap = plt.cm.Set3
            colorbar_label = "State"
        else:  # community
            try:
                from networkx.algorithms import community
                communities = list(community.greedy_modularity_communities(G))
                community_map = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        community_map[node] = i
                node_colors = [community_map.get(n, 0) for n in G.nodes()]
                cmap = plt.cm.tab20
                colorbar_label = "Community"
            except:
                node_colors = [0] * len(G.nodes())
                cmap = plt.cm.Set3
                colorbar_label = "Default"
        
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
        
        # Add colorbar
        plt.colorbar(nodes, ax=ax, label=colorbar_label)
        
        st.pyplot(fig)
        plt.close()
    
    def _render_3d_network(self):
        """Render 3D network visualization"""
        st.info("3D Network Visualization")
        
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
            node_colors = []
            
            for node in G.nodes():
                x, y, z = pos_3d[node]
                x_vals.append(x)
                y_vals.append(y)
                z_vals.append(z)
                
                # Color by state if available
                state = G.nodes[node].get('state', 'S')
                color_map = {
                    'S': 'green',
                    'E': 'orange',
                    'I': 'red',
                    'R': 'blue',
                    'D': 'gray',
                    'V': 'purple'
                }
                node_colors.append(color_map.get(state, 'blue'))
            
            fig = go.Figure(data=[go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='markers',
                marker=dict(
                    size=5,
                    color=node_colors,
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
    
    def _render_heatmap(self):
        """Render heatmap visualization"""
        st.info("Heatmap visualization - showing disease spread patterns")
        
        if not st.session_state.simulation_history:
            return
        
        history = st.session_state.simulation_history
        
        # Create heatmap of infections over time
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
    
    def _render_timeline(self):
        """Render timeline visualization"""
        st.info("Timeline visualization showing disease progression")
        
        if not st.session_state.simulation_history:
            return
        
        history = st.session_state.simulation_history
        
        # Create timeline with multiple traces
        fig = go.Figure()
        
        traces = [
            ('S', 'Susceptible', 'green'),
            ('I', 'Infectious', 'red'),
            ('R', 'Recovered', 'blue')
        ]
        
        for key, name, color in traces:
            if key in history:
                fig.add_trace(go.Scatter(
                    x=history['time'],
                    y=history[key],
                    mode='lines',
                    name=name,
                    line=dict(color=color, width=2)
                ))
        
        fig.update_layout(
            title='Disease Timeline',
            xaxis_title='Days',
            yaxis_title='Count',
            template='plotly_white',
            height=500,
            hovermode='x unified'
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
            
            if st.button("🎬 Prepare Animation Now", type="primary", use_container_width=True, key="anim_prepare_btn"):
                self._prepare_animation()
                st.rerun()
            return
        
        # Animation export options
        st.markdown("### 🎛️ Animation Export Options")
        
        export_type = st.selectbox(
            "Export Format",
            ["GIF Video", "HTML Interactive", "Frame Images", "MP4 Video", "WebM Video"],
            index=0,
            key="export_type"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fps = st.slider("Frames Per Second", 1, 30, 10, key="fps_slider")
        
        with col2:
            quality = st.select_slider(
                "Quality",
                options=["Low", "Medium", "High"],
                value="Medium",
                key="quality_slider"
            )
        
        with col3:
            resolution = st.selectbox(
                "Resolution",
                ["640x480", "1280x720", "1920x1080"],
                index=1,
                key="resolution_select"
            )
        
        # Generate button
        if st.button("🎥 Generate Animation", type="primary", use_container_width=True, key="generate_anim_btn"):
            if export_type == "GIF Video":
                self._generate_gif_animation(fps, quality)
            elif export_type == "HTML Interactive":
                self._generate_html_animation()
            elif export_type == "Frame Images":
                self._export_animation_frames()
            elif export_type == "MP4 Video":
                self._generate_mp4_animation(fps, quality, resolution)
            elif export_type == "WebM Video":
                self._generate_webm_animation(fps, quality, resolution)
        
        # Live preview
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
            auto_play = st.button("▶️ Play in Streamlit", use_container_width=True, key="autoplay_btn")
        
        with play_col2:
            delay = st.slider("Frame Delay (ms)", 100, 2000, 500, 100, key="delay_slider")
        
        if auto_play:
            self._play_streamlit_animation(delay)
    
    def _display_animation_frame(self, frame_idx):
        """Display a single animation frame"""
        if not st.session_state.animation_frames:
            return
        
        if frame_idx >= len(st.session_state.animation_frames):
            frame_idx = len(st.session_state.animation_frames) - 1
        
        frame = st.session_state.animation_frames[frame_idx]
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            if hasattr(st.session_state.animator, 'node_positions'):
                pos = st.session_state.animator.node_positions
            else:
                pos = nx.spring_layout(st.session_state.network_graph, seed=42)
            
            G = st.session_state.network_graph
            
            # Draw network
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.3, edge_color='gray')
            
            node_colors = frame['node_colors']
            node_sizes = frame.get('node_sizes', [50] * len(G.nodes()))
            
            color_groups = {}
            for i, node in enumerate(G.nodes()):
                color = node_colors[i] if i < len(node_colors) else '#CCCCCC'
                if color not in color_groups:
                    color_groups[color] = []
                color_groups[color].append(node)
            
            for color, nodes in color_groups.items():
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
            
            stats = frame['statistics']
            
            st.metric("Susceptible", stats.get('S', 0), key="frame_s")
            st.metric("Infectious", stats.get('I', 0), key="frame_i")
            st.metric("Recovered", stats.get('R', 0), key="frame_r")
            
            if 'new_cases' in stats:
                st.metric("New Cases", stats.get('new_cases', 0), key="frame_new")
            
            progress = (frame_idx + 1) / len(st.session_state.animation_frames)
            st.progress(progress, text=f"Frame {frame_idx + 1}/{len(st.session_state.animation_frames)}")
    
    def _generate_gif_animation(self, fps, quality):
        """Generate GIF animation"""
        try:
            if st.session_state.animator is None:
                st.error("Animator not available")
                return
            
            with st.spinner("Creating GIF animation..."):
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
                        
                        frame_files = sorted([f for f in os.listdir(tmpdir) if f.endswith('.png')])
                        
                        if not frame_files:
                            st.error("No frames exported")
                            return
                        
                        frames = []
                        for frame_file in frame_files:
                            frame_path = os.path.join(tmpdir, frame_file)
                            frames.append(imageio.imread(frame_path))
                        
                        output_path = "simulation_animation.gif"
                        imageio.mimsave(output_path, frames, fps=fps)
                        
                        st.success(f"✅ GIF created: {output_path}")
                        
                        st.image(output_path, caption="Simulation Animation GIF")
                        
                        with open(output_path, "rb") as f:
                            gif_data = f.read()
                        
                        st.download_button(
                            label="📥 Download GIF",
                            data=gif_data,
                            file_name="pandemic_simulation.gif",
                            mime="image/gif",
                            key="download_gif"
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
                
                if hasattr(st.session_state.animator, 'create_interactive_animation'):
                    st.session_state.animator.create_interactive_animation(output_file)
                    
                    with open(output_file, "r") as f:
                        html_content = f.read()
                    
                    st.success(f"✅ HTML animation created: {output_file}")
                    
                    st.download_button(
                        label="📥 Download HTML Animation",
                        data=html_content,
                        file_name="pandemic_animation.html",
                        mime="text/html",
                        key="download_html"
                    )
                    
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
                import zipfile
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    frames_dir = os.path.join(tmpdir, "frames")
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=frames_dir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    zip_path = os.path.join(tmpdir, "animation_frames.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for root, dirs, files in os.walk(frames_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, frames_dir)
                                zipf.write(file_path, arcname)
                    
                    with open(zip_path, "rb") as f:
                        zip_data = f.read()
                    
                    st.success(f"✅ Exported {len(os.listdir(frames_dir))} frames")
                    st.download_button(
                        label="📥 Download All Frames (ZIP)",
                        data=zip_data,
                        file_name="animation_frames.zip",
                        mime="application/zip",
                        key="download_frames"
                    )
                    
        except Exception as e:
            st.error(f"Error exporting frames: {str(e)}")
    
    def _generate_mp4_animation(self, fps, quality, resolution):
        """Generate MP4 video animation"""
        st.info("MP4 video creation requires ffmpeg. Ensure it's installed on your system.")
        
        try:
            import subprocess
            
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
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    frames_dir = os.path.join(tmpdir, "frames")
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=frames_dir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    output_path = "simulation_animation.mp4"
                    
                    # Parse resolution
                    width, height = map(int, resolution.split('x'))
                    
                    cmd = [
                        'ffmpeg',
                        '-framerate', str(fps),
                        '-pattern_type', 'glob',
                        '-i', f'{frames_dir}/*.png',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-vf', f'scale={width}:{height}',
                        output_path,
                        '-y'
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        st.success(f"✅ MP4 video created: {output_path}")
                        
                        video_file = open(output_path, 'rb')
                        video_bytes = video_file.read()
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="📥 Download MP4 Video",
                            data=video_bytes,
                            file_name="pandemic_simulation.mp4",
                            mime="video/mp4",
                            key="download_mp4"
                        )
                    else:
                        st.error(f"FFmpeg error: {result.stderr}")
                        
        except Exception as e:
            st.error(f"Error generating MP4: {str(e)}")
    
    def _generate_webm_animation(self, fps, quality, resolution):
        """Generate WebM video animation"""
        st.info("WebM video creation requires ffmpeg with VP9 codec support.")
        
        try:
            import subprocess
            
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error("FFmpeg not found.")
                return
            
            with st.spinner("Creating WebM video..."):
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    frames_dir = os.path.join(tmpdir, "frames")
                    try:
                        st.session_state.animator.export_animation_frames(output_dir=frames_dir)
                    except Exception as e:
                        st.error(f"Error exporting frames: {e}")
                        return
                    
                    output_path = "simulation_animation.webm"
                    
                    width, height = map(int, resolution.split('x'))
                    
                    cmd = [
                        'ffmpeg',
                        '-framerate', str(fps),
                        '-pattern_type', 'glob',
                        '-i', f'{frames_dir}/*.png',
                        '-c:v', 'libvpx-vp9',
                        '-pix_fmt', 'yuva420p',
                        '-vf', f'scale={width}:{height}',
                        output_path,
                        '-y'
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        st.success(f"✅ WebM video created: {output_path}")
                        
                        video_file = open(output_path, 'rb')
                        video_bytes = video_file.read()
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="📥 Download WebM Video",
                            data=video_bytes,
                            file_name="pandemic_simulation.webm",
                            mime="video/webm",
                            key="download_webm"
                        )
                    else:
                        st.error(f"FFmpeg error: {result.stderr}")
                        
        except Exception as e:
            st.error(f"Error generating WebM: {str(e)}")
    
    def _play_streamlit_animation(self, delay_ms):
        """Play animation directly in Streamlit"""
        try:
            frames = st.session_state.animation_frames
            if not frames or len(frames) <= 1:
                st.error("No animation frames available or only one frame")
                return
            
            animation_placeholder = st.empty()
            progress_bar = st.progress(0, text="Playing animation...")
            
            for i, frame in enumerate(frames):
                progress_bar.progress((i + 1) / len(frames), text=f"Frame {i+1}/{len(frames)}")
                
                with animation_placeholder.container():
                    self._display_animation_frame(i)
                
                time.sleep(delay_ms / 1000)
            
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
        
        # Export options
        st.markdown("### 📊 Export Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Export CSV", use_container_width=True, key="export_csv_btn"):
                self._export_results_csv()
        
        with col2:
            if st.button("📋 Export JSON", use_container_width=True, key="export_json_btn"):
                self._export_summary()
        
        with col3:
            if st.button("🖼️ Export Visualization", use_container_width=True, key="export_viz_btn"):
                self._export_final_visualization()
        
        with col4:
            if st.button("📁 Export All", use_container_width=True, key="export_all_btn"):
                self._export_all_data()
        
        # Detailed metrics
        st.markdown("---")
        st.markdown("### 📋 Detailed Metrics")
        
        if hasattr(st.session_state.simulator, 'get_summary_stats'):
            try:
                stats = st.session_state.simulator.get_summary_stats()
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown("#### 📈 Epidemic Metrics")
                    epidemic_metrics = ['attack_rate', 'peak_infections', 'peak_day', 
                                       'case_fatality_rate', 'final_r_effective']
                    for key in epidemic_metrics:
                        if key in stats:
                            value = stats[key]
                            if isinstance(value, float):
                                display = f"{value:.2%}" if 'rate' in key else f"{value:.2f}"
                            else:
                                display = str(value)
                            st.metric(key.replace('_', ' ').title(), display, key=f"epidemic_{key}")
                
                with metrics_col2:
                    st.markdown("#### 👥 Population Metrics")
                    population_metrics = ['initial_population', 'total_infected', 
                                         'total_recovered', 'total_deaths', 'total_vaccinated']
                    for key in population_metrics:
                        if key in stats:
                            value = stats[key]
                            st.metric(key.replace('_', ' ').title(), f"{value:,}", key=f"pop_{key}")
            except:
                st.warning("Could not load summary statistics")
        
        # Simulation history
        if st.session_state.simulation_history:
            st.markdown("---")
            st.markdown("### 📈 Time Series Data")
            
            history_df = pd.DataFrame(st.session_state.simulation_history)
            
            st.dataframe(history_df.tail(30), use_container_width=True)
            
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full History CSV",
                data=csv,
                file_name="simulation_history.csv",
                mime="text/csv",
                key="download_history"
            )
        
        # Configuration details
        st.markdown("---")
        st.markdown("### ⚙️ Configuration Details")
        
        if hasattr(st.session_state, 'simulation_params'):
            with st.expander("View Simulation Parameters", expanded=False):
                st.json(st.session_state.simulation_params)
    
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
                    mime="text/csv",
                    key="download_results_csv"
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
                
                if hasattr(st.session_state, 'simulation_params'):
                    stats['simulation_parameters'] = st.session_state.simulation_params
                
                json_str = json.dumps(stats, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON Summary",
                    data=json_str,
                    file_name="simulation_summary.json",
                    mime="application/json",
                    key="download_summary_json"
                )
            else:
                st.warning("No summary statistics available")
        except Exception as e:
            st.error(f"Error exporting summary: {str(e)}")
    
    def _export_final_visualization(self):
        """Export final visualization as image"""
        try:
            if st.session_state.animation_frames:
                final_frame = st.session_state.animation_frames[-1]
                
                fig, ax = plt.subplots(figsize=(12, 10))
                
                if hasattr(st.session_state.animator, 'node_positions'):
                    pos = st.session_state.animator.node_positions
                else:
                    pos = nx.spring_layout(st.session_state.network_graph, seed=42)
                
                G = st.session_state.network_graph
                node_colors = final_frame['node_colors']
                
                nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, width=0.5)
                nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=50, ax=ax)
                
                ax.set_title(f"Final State - Day {final_frame['day']}", fontsize=16, fontweight='bold')
                ax.axis('off')
                
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                plt.close()
                
                st.download_button(
                    label="📥 Download Final Visualization",
                    data=buf.getvalue(),
                    file_name="final_simulation_state.png",
                    mime="image/png",
                    key="download_final_viz"
                )
                
                st.image(buf.getvalue(), caption="Final Simulation State")
                
        except Exception as e:
            st.error(f"Error exporting visualization: {str(e)}")
    
    def _export_all_data(self):
        """Export all data as a zip file"""
        st.info("Complete data export feature coming soon!")
        st.info("This would create a ZIP file containing:")
        st.info("- Simulation results CSV")
        st.info("- Summary statistics JSON")
        st.info("- Configuration parameters")
        st.info("- Final visualization image")
        st.info("- Animation frames (if available)")

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
        print("🎬 Features: Maximum parameter control, Network Animation, Disease Spread Visualization!")
        print("=" * 60)
        
        # Run the dashboard
        main()