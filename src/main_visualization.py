# main_visualization.py - Complete visualization pipeline
import os
from datetime import datetime

def create_project_visualizations():
    """Main function to create all project visualizations"""
    
    PROJECT_NAME = "Pandemic_Simulation"
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR = f"visualizations/{PROJECT_NAME}_{TIMESTAMP}"
    
    print("=" * 60)
    print("🎨 PANDEMIC SIMULATION VISUALIZATION PIPELINE")
    print("=" * 60)
    
    # Import project components
    from network_generator import UltimateNetworkGenerator
    from disease_models import DiseaseLibrary
    from simulator_engine import UltimateSimulator
    from visualization_3d import PandemicVisualizer3D, visualize_simulation
    
    # ========== CONFIGURATION ==========
    CONFIG = {
        'population': 1000,
        'network_type': 'hybrid',
        'disease': 'omicron',
        'simulation_days': 120,
        'n_seed_infections': 10,
        'intervention_scenario': 'delayed_response'
    }
    
    print(f"\n⚙️  Configuration:")
    for key, value in CONFIG.items():
        print(f"   {key}: {value}")
    
    # ========== STEP 1: GENERATE NETWORK ==========
    print(f"\n1️⃣  Generating {CONFIG['network_type']} network...")
    generator = UltimateNetworkGenerator(population=CONFIG['population'])
    
    if CONFIG['network_type'] == 'erdos_renyi':
        G = generator.erdos_renyi(p=0.01)
    elif CONFIG['network_type'] == 'watts_strogatz':
        G = generator.watts_strogatz(k=8, p=0.3)
    elif CONFIG['network_type'] == 'barabasi_albert':
        G = generator.barabasi_albert(m=3)
    elif CONFIG['network_type'] == 'stochastic_block':
        G = generator.stochastic_block()
    else:
        G = generator.hybrid_multilayer()
    
    print(f"   ✅ Network created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # ========== STEP 2: SET UP DISEASE ==========
    print(f"\n2️⃣  Configuring {CONFIG['disease']} disease model...")
    disease = DiseaseLibrary.covid19_variant(CONFIG['disease'])
    print(f"   ✅ Disease: {disease.name}, R0={disease.R0}")
    
    # ========== STEP 3: RUN SIMULATION ==========
    print(f"\n3️⃣  Running {CONFIG['simulation_days']}-day simulation...")
    simulator = UltimateSimulator(G, disease)
    simulator.seed_infections(CONFIG['n_seed_infections'], method='hubs')
    history = simulator.run(days=CONFIG['simulation_days'], show_progress=True)
    
    stats = simulator.get_summary_stats()
    print(f"   ✅ Simulation complete:")
    print(f"      - Total infected: {stats['total_infected']}")
    print(f"      - Peak infections: {stats['peak_infections']}")
    print(f"      - Attack rate: {stats['attack_rate']:.2%}")
    print(f"      - Case fatality: {stats['case_fatality_rate']:.2%}")
    
    # ========== STEP 4: GENERATE VISUALIZATIONS ==========
    print(f"\n4️⃣  Generating visualizations in {OUTPUT_DIR}...")
    
    # Create all visualizations
    visualize_simulation(simulator, output_dir=OUTPUT_DIR)
    
    # ========== STEP 5: CREATE ANIMATION ==========
    print(f"\n5️⃣  Creating time-lapse animation...")
    visualizer = PandemicVisualizer3D(simulator)
    
    # Create animation of key days
    key_days = list(range(0, CONFIG['simulation_days'], 5))  # Every 5 days
    key_days.append(CONFIG['simulation_days'] - 1)  # Add final day
    
    animation_frames = []
    for day in key_days:
        fig = visualizer.create_3d_network_plot(
            day=day,
            title=f"Day {day}",
            color_by='disease_state',
            show_edges=True
        )
        animation_frames.append(fig)
    
    # Save as interactive HTML
    visualizer._create_html_animation(
        animation_frames, 
        f"{OUTPUT_DIR}/animation.html"
    )
    
    # ========== STEP 6: CREATE SUMMARY REPORT ==========
    print(f"\n6️⃣  Creating final summary...")
    
    summary_file = f"{OUTPUT_DIR}/SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(f"# Pandemic Simulation Summary\n\n")
        f.write(f"**Project:** {PROJECT_NAME}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Configuration\n")
        for key, value in CONFIG.items():
            f.write(f"- **{key}:** {value}\n")
        
        f.write(f"\n## Results\n")
        for key, value in stats.items():
            if isinstance(value, float):
                f.write(f"- **{key}:** {value:.4f}\n")
            else:
                f.write(f"- **{key}:** {value}\n")
        
        f.write(f"\n## Files Generated\n")
        f.write(f"- `3d_network.html` - Interactive 3D visualization\n")
        f.write(f"- `dashboard.html` - Comprehensive dashboard\n")
        f.write(f"- `animation.html` - Time-lapse animation\n")
        f.write(f"- `epidemic_curves.png` - Epidemic curves plot\n")
        f.write(f"- `network_metrics.png` - Network analysis\n")
        f.write(f"- `report.html` - HTML report\n")
        f.write(f"- `data/` - Exported data files\n")
    
    print(f"\n" + "=" * 60)
    print("✅ VISUALIZATION PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n📁 All outputs saved to: {OUTPUT_DIR}/")
    print(f"\n📋 Quick access:")
    print(f"   1. Open {OUTPUT_DIR}/dashboard.html for interactive dashboard")
    print(f"   2. Open {OUTPUT_DIR}/animation.html for time-lapse")
    print(f"   3. Check {OUTPUT_DIR}/SUMMARY.md for results summary")
    
    return OUTPUT_DIR

if __name__ == "__main__":
    output_dir = create_project_visualizations()
    
    # Open dashboard in browser (optional)
    import webbrowser
    import os
    
    dashboard_path = os.path.join(output_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        print(f"\n🌐 Opening dashboard in browser...")
        webbrowser.open(f"file://{os.path.abspath(dashboard_path)}")