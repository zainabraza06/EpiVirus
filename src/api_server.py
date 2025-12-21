# api_server.py - FastAPI wrapper for EpiVirus Pandemic Simulator
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import uvicorn
import sys
import json
from datetime import datetime
import asyncio
import numpy as np
import networkx as nx
import traceback
import os
from pathlib import Path

# Add project modules to path
sys.path.append('./src')

from network_generator import UltimateNetworkGenerator
from disease_models import DiseaseLibrary, DiseaseParameters
from simulator_engine import UltimateSimulator

app = FastAPI(
    title="EpiVirus Pandemic Simulation API",
    description="REST API for epidemic simulation with network-based disease spread modeling",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend build)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend"""
        return FileResponse(STATIC_DIR / "index.html")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA routes"""
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")

# Global state for active simulations
active_simulations: Dict[str, Dict[str, Any]] = {}

# ==================== REQUEST/RESPONSE MODELS ====================

class NetworkConfig(BaseModel):
    population: int = 1000
    network_type: str = "hybrid"  # hybrid, erdos_renyi, watts_strogatz, barabasi_albert, stochastic_block
    erdos_p: Optional[float] = 0.01
    watts_k: Optional[int] = 8
    watts_p: Optional[float] = 0.3
    barabasi_m: Optional[int] = 3
    block_intra: Optional[float] = 0.15
    block_inter: Optional[float] = 0.01

class DiseaseConfig(BaseModel):
    variant: str = "omicron"  # omicron, delta, alpha, wildtype
    custom_r0: Optional[float] = None
    custom_mortality: Optional[float] = None
    custom_incubation_mean: Optional[float] = None

class SimulationConfig(BaseModel):
    network: NetworkConfig
    disease: DiseaseConfig
    n_seed_infections: int = 10
    seed_method: str = "random"  # random, hubs, mobile
    simulation_days: int = 120
    intervention_scenario: str = "no_intervention"  # no_intervention, rapid_response, delayed_response
    vaccination_rate: float = 0.0
    compliance_rate: float = 0.8
    animate: bool = True
    animation_step: int = 2

class SimulationStatus(BaseModel):
    simulation_id: str
    status: str  # running, completed, failed
    current_day: int
    total_days: int
    progress: float

class SimulationResult(BaseModel):
    simulation_id: str
    status: str
    history: Dict[str, List[float]]
    summary: Dict[str, Any]
    network_info: Dict[str, Any]

# ==================== HELPER FUNCTIONS ====================

def generate_network(config: NetworkConfig):
    """Generate network based on configuration"""
    generator = UltimateNetworkGenerator(population=config.population)
    
    if config.network_type == "hybrid":
        return generator.hybrid_multilayer()
    elif config.network_type == "erdos_renyi":
        return generator.erdos_renyi(p=config.erdos_p)
    elif config.network_type == "watts_strogatz":
        return generator.watts_strogatz(k=config.watts_k, p=config.watts_p)
    elif config.network_type == "barabasi_albert":
        return generator.barabasi_albert(m=config.barabasi_m)
    elif config.network_type == "stochastic_block":
        return generator.stochastic_block(
            intra_prob=config.block_intra,
            inter_prob=config.block_inter
        )
    else:
        return generator.hybrid_multilayer()

def get_disease_params(config: DiseaseConfig) -> DiseaseParameters:
    """Get disease parameters based on configuration"""
    disease = DiseaseLibrary.covid19_variant(config.variant)
    
    # Apply custom parameters if provided
    if config.custom_r0:
        disease.R0 = config.custom_r0
    if config.custom_mortality:
        disease.mortality_rate = config.custom_mortality
    if config.custom_incubation_mean:
        disease.incubation_period['mean'] = config.custom_incubation_mean
    
    return disease

def apply_interventions(simulator: UltimateSimulator, scenario: str, vaccination_rate: float, compliance_rate: float):
    """Apply intervention scenario"""
    if scenario == "rapid_response":
        # Lockdown at day 30 (strictness and compliance, not strength)
        simulator.apply_intervention('lockdown', strictness=0.7, compliance=compliance_rate, duration=60)
        # Vaccination starting day 60
        if vaccination_rate > 0:
            simulator.apply_intervention('vaccination', rate=vaccination_rate, priority='age')
    
    elif scenario == "delayed_response":
        # Late lockdown at day 60
        simulator.apply_intervention('lockdown', strictness=0.5, compliance=compliance_rate, duration=40)
        if vaccination_rate > 0:
            simulator.apply_intervention('vaccination', rate=vaccination_rate * 0.5, priority='random')
    
    # No intervention for "no_intervention" or "herd_immunity"

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "EpiVirus Pandemic Simulation API",
        "version": "1.0.0",
        "endpoints": {
            "simulation": "/api/simulation",
            "status": "/api/simulation/{id}/status",
            "results": "/api/simulation/{id}/results",
            "diseases": "/api/diseases",
            "networks": "/api/networks"
        }
    }

@app.get("/api/diseases")
async def get_diseases():
    """Get available disease variants"""
    return {
        "diseases": [
            {
                "id": "wildtype",
                "name": "COVID-19 (Wildtype)",
                "r0": 2.5,
                "mortality_rate": 0.02,
                "description": "Original COVID-19 variant"
            },
            {
                "id": "alpha",
                "name": "COVID-19 (Alpha)",
                "r0": 4.0,
                "mortality_rate": 0.025,
                "description": "Alpha variant (B.1.1.7)"
            },
            {
                "id": "delta",
                "name": "COVID-19 (Delta)",
                "r0": 6.0,
                "mortality_rate": 0.03,
                "description": "Delta variant (B.1.617.2)"
            },
            {
                "id": "omicron",
                "name": "COVID-19 (Omicron)",
                "r0": 10.0,
                "mortality_rate": 0.01,
                "description": "Omicron variant (B.1.1.529)"
            }
        ]
    }

@app.get("/api/networks")
async def get_networks():
    """Get available network types"""
    return {
        "networks": [
            {
                "id": "hybrid",
                "name": "Hybrid Multilayer",
                "description": "Realistic social network with households, workplaces, and schools"
            },
            {
                "id": "erdos_renyi",
                "name": "Erdős-Rényi",
                "description": "Random network with uniform connection probability"
            },
            {
                "id": "watts_strogatz",
                "name": "Watts-Strogatz",
                "description": "Small-world network with clustering and short paths"
            },
            {
                "id": "barabasi_albert",
                "name": "Barabási-Albert",
                "description": "Scale-free network with power-law degree distribution"
            },
            {
                "id": "stochastic_block",
                "name": "Stochastic Block",
                "description": "Community-structured network"
            }
        ]
    }

@app.post("/api/simulation")
async def create_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Create and run a new simulation"""
    simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Initialize simulation state
        active_simulations[simulation_id] = {
            "status": "initializing",
            "current_day": 0,
            "total_days": config.simulation_days,
            "progress": 0,
            "config": config.dict(),
            "history": None,
            "summary": None,
            "network_info": None
        }
        
        # Run simulation in background
        background_tasks.add_task(run_simulation, simulation_id, config)
        
        return {
            "simulation_id": simulation_id,
            "status": "initializing",
            "message": "Simulation started"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")

async def run_simulation(simulation_id: str, config: SimulationConfig):
    """Run simulation in background"""
    try:
        # Update status
        active_simulations[simulation_id]["status"] = "running"
        
        # 1. Generate network
        print(f"[{simulation_id}] Generating network...")
        G = generate_network(config.network)
        
        network_info = {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "avg_degree": sum(dict(G.degree()).values()) / G.number_of_nodes(),
            "network_type": config.network.network_type
        }
        active_simulations[simulation_id]["network_info"] = network_info
        
        # 2. Configure disease
        print(f"[{simulation_id}] Configuring disease...")
        disease = get_disease_params(config.disease)
        
        # 3. Initialize simulator
        print(f"[{simulation_id}] Initializing simulator...")
        simulator = UltimateSimulator(G, disease)
        
        # 4. Seed infections
        simulator.seed_infections(config.n_seed_infections, method=config.seed_method)
        
        # 5. Apply interventions
        apply_interventions(
            simulator,
            config.intervention_scenario,
            config.vaccination_rate,
            config.compliance_rate
        )
        
        # 6. Run simulation
        print(f"[{simulation_id}] Running simulation for {config.simulation_days} days...")
        history = simulator.run(days=config.simulation_days, show_progress=False)
        
        # 7. Get results
        summary = simulator.get_summary_stats()
        
        # Convert history arrays to lists for JSON serialization
        history_serializable = {}
        for key, value in history.items():
            if isinstance(value, np.ndarray):
                history_serializable[key] = value.tolist()
            elif isinstance(value, list):
                history_serializable[key] = [float(v) if isinstance(v, (np.integer, np.floating)) else v for v in value]
            else:
                history_serializable[key] = value
        
        # Calculate daily new cases from cumulative infections
        cumulative_infections = [history_serializable['S'][0] - s for s in history_serializable['S']]
        daily_new_cases = [cumulative_infections[0]]
        for i in range(1, len(cumulative_infections)):
            daily_new_cases.append(cumulative_infections[i] - cumulative_infections[i-1])
        
        # Get additional detailed data
        detailed_data = {
            'daily_new_cases': daily_new_cases,
            'severity_breakdown': {
                'asymptomatic': history_serializable.get('Ia', [0] * len(history_serializable['S'])),
                'mild': history_serializable.get('Im', [0] * len(history_serializable['S'])),
                'severe': history_serializable.get('Is', [0] * len(history_serializable['S'])),
                'hospitalized': history_serializable.get('Ih', [0] * len(history_serializable['S'])),
                'critical': history_serializable.get('Ic', [0] * len(history_serializable['S']))
            },
            'hospital_capacity': {
                'beds_used': simulator.stats.get('hospital_bed_usage', []),
                'capacity': float(G.number_of_nodes() * 0.10)  # 10% of population as capacity
            },
            'age_distribution': {},
            'degree_distribution': {},
            'r_effective': simulator.stats.get('r_effective', [])
        }
        
        # Calculate age distribution of infections
        age_groups = {node: G.nodes[node].get('age', 30) for node in G.nodes()}
        age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 100]
        infected_ages = [age_groups[node] for node in G.nodes() 
                        if G.nodes[node].get('state') in ['I', 'R', 'D']]
        
        if infected_ages:
            age_hist, _ = np.histogram(infected_ages, bins=age_bins)
            detailed_data['age_distribution'] = {
                'bins': age_bins,
                'counts': age_hist.tolist()
            }
        
        # Calculate degree distribution
        degrees = [d for _, d in G.degree()]
        degree_hist, degree_bins = np.histogram(degrees, bins=20)
        detailed_data['degree_distribution'] = {
            'bins': degree_bins.tolist(),
            'counts': degree_hist.tolist()
        }
        
        # Calculate mobility distribution
        mobilities = [G.nodes[node].get('mobility', 0.5) for node in G.nodes()]
        mobility_hist, mobility_bins = np.histogram(mobilities, bins=20)
        detailed_data['mobility_distribution'] = {
            'bins': mobility_bins.tolist(),
            'counts': mobility_hist.tolist()
        }
        
        # Calculate social clustering by age group
        age_groups_for_clustering = ['0-17', '18-29', '30-49', '50-69', '70+']
        age_bins_clustering = [0, 18, 30, 50, 70, 100]
        clustering_by_age = []
        
        for i in range(len(age_bins_clustering)-1):
            age_nodes = [n for n in G.nodes() 
                        if age_bins_clustering[i] <= G.nodes[n]['age'] < age_bins_clustering[i+1]]
            if len(age_nodes) > 1:
                subgraph = G.subgraph(age_nodes)
                clustering = nx.average_clustering(subgraph)
                clustering_by_age.append(clustering)
            else:
                clustering_by_age.append(0.0)
        
        detailed_data['social_clustering'] = {
            'age_groups': age_groups_for_clustering,
            'clustering': clustering_by_age
        }
        
        # Update state with results
        active_simulations[simulation_id].update({
            "status": "completed",
            "current_day": config.simulation_days,
            "progress": 100,
            "history": history_serializable,
            "summary": summary,
            "detailed_data": detailed_data
        })
        
        print(f"[{simulation_id}] Simulation completed!")
        
    except Exception as e:
        print(f"[{simulation_id}] Simulation failed: {str(e)}")
        print(f"[{simulation_id}] Full traceback:")
        traceback.print_exc()
        active_simulations[simulation_id].update({
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        })

@app.get("/api/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get simulation status"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "status": sim["status"],
        "current_day": sim["current_day"],
        "total_days": sim["total_days"],
        "progress": sim["progress"],
        "network_info": sim.get("network_info")
    }

@app.get("/api/simulation/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get simulation results"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = active_simulations[simulation_id]
    
    if sim["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Simulation status is {sim['status']}, not completed")
    
    return {
        "simulation_id": simulation_id,
        "status": sim["status"],
        "history": sim["history"],
        "summary": sim["summary"],
        "network_info": sim["network_info"],
        "config": sim["config"],
        "detailed_data": sim.get("detailed_data", {})
    }

@app.delete("/api/simulation/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    del active_simulations[simulation_id]
    
    return {"message": "Simulation deleted"}

@app.get("/api/simulations")
async def list_simulations():
    """List all simulations"""
    simulations = []
    for sim_id, sim in active_simulations.items():
        simulations.append({
            "simulation_id": sim_id,
            "status": sim["status"],
            "progress": sim["progress"],
            "network_type": sim["config"]["network"]["network_type"],
            "disease_variant": sim["config"]["disease"]["variant"]
        })
    
    return {"simulations": simulations}

# ==================== MAIN ====================

if __name__ == "__main__":
    print("🦠 Starting EpiVirus Pandemic Simulation API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 WebSocket support: Coming soon")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
