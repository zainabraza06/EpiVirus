# api_server.py - FastAPI wrapper for the EpiVirus pandemic simulator
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import networkx as nx
import numpy as np
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from disease_models import DiseaseLibrary, DiseaseParameters, InterventionSchedule
from network_generator import UltimateNetworkGenerator
from simulator_engine import UltimateSimulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("epivirus.api")

app = FastAPI(
    title="EpiVirus Pandemic Simulation API",
    description="REST API for epidemic simulation with network-based disease spread modeling",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== LIMITS ====================

MAX_POPULATION = 10_000
MAX_DAYS = 365
MAX_STORED_SIMULATIONS = 20

# The 3D view renders a sampled subgraph; the full network would be far too
# heavy to ship over JSON and to draw at interactive frame rates.
VIS_MAX_NODES = 350
VIS_MAX_EDGES = 1_200
VIS_MAX_FRAMES = 150

# Simulations live in memory only. The lock guards against the background
# worker and a status poll touching the dict at the same time.
active_simulations: "Dict[str, Dict[str, Any]]" = {}
_simulations_lock = Lock()


# ==================== REQUEST MODELS ====================

class NetworkConfig(BaseModel):
    population: int = Field(1000, ge=50, le=MAX_POPULATION)
    network_type: str = "hybrid"
    erdos_p: float = Field(0.01, gt=0, le=1)
    watts_k: int = Field(8, ge=2, le=100)
    watts_p: float = Field(0.3, ge=0, le=1)
    barabasi_m: int = Field(3, ge=1, le=50)
    n_blocks: int = Field(4, ge=2, le=50)
    block_intra: float = Field(0.15, ge=0, le=1)
    block_inter: float = Field(0.01, ge=0, le=1)


class CustomDiseaseParams(BaseModel):
    """Optional overrides from the custom disease builder."""
    name: Optional[str] = None
    r0: Optional[float] = Field(None, ge=0, le=20)
    mortality_rate: Optional[float] = Field(None, ge=0, le=1)
    hospitalization_rate: Optional[float] = Field(None, ge=0, le=1)
    incubation_mean: Optional[float] = Field(None, ge=1, le=30)
    incubation_std: Optional[float] = Field(None, gt=0, le=15)
    infectious_mean: Optional[float] = Field(None, ge=1, le=60)
    infectious_std: Optional[float] = Field(None, gt=0, le=30)
    p_asymptomatic: Optional[float] = Field(None, ge=0, le=1)
    p_mild: Optional[float] = Field(None, ge=0, le=1)
    p_severe: Optional[float] = Field(None, ge=0, le=1)
    p_critical: Optional[float] = Field(None, ge=0, le=1)
    seasonality_amplitude: Optional[float] = Field(None, ge=0, le=1)
    seasonality_peak: Optional[int] = Field(None, ge=0, le=364)


class DiseaseConfig(BaseModel):
    variant: str = "omicron"
    custom_params: Optional[CustomDiseaseParams] = None
    # Retained for backwards compatibility with the original API shape
    custom_r0: Optional[float] = Field(None, ge=0, le=20)
    custom_mortality: Optional[float] = Field(None, ge=0, le=1)
    custom_incubation_mean: Optional[float] = Field(None, ge=1, le=30)


class CustomIntervention(BaseModel):
    day: int = Field(0, ge=0, le=MAX_DAYS)
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class SimulationConfig(BaseModel):
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    disease: DiseaseConfig = Field(default_factory=DiseaseConfig)
    n_seed_infections: int = Field(10, ge=1, le=MAX_POPULATION)
    seed_method: str = "random"
    simulation_days: int = Field(120, ge=1, le=MAX_DAYS)
    intervention_scenario: str = "no_intervention"
    vaccination_rate: float = Field(0.0, ge=0, le=1)
    compliance_rate: float = Field(0.8, ge=0, le=1)
    custom_interventions: List[CustomIntervention] = Field(default_factory=list)


# ==================== HELPERS ====================

def generate_network(config: NetworkConfig):
    """Generate the contact network described by `config`."""
    generator = UltimateNetworkGenerator(population=config.population)

    builders = {
        "hybrid": lambda: generator.hybrid_multilayer(),
        "erdos_renyi": lambda: generator.erdos_renyi(p=config.erdos_p),
        "watts_strogatz": lambda: generator.watts_strogatz(
            k=min(config.watts_k, max(2, config.population - 1)), p=config.watts_p
        ),
        "barabasi_albert": lambda: generator.barabasi_albert(
            m=min(config.barabasi_m, max(1, config.population - 1))
        ),
        "stochastic_block": lambda: generator.stochastic_block(
            intra_prob=config.block_intra,
            inter_prob=config.block_inter,
            n_blocks=config.n_blocks,
        ),
    }
    return builders.get(config.network_type, builders["hybrid"])()


def get_disease_params(config: DiseaseConfig) -> DiseaseParameters:
    """Build the disease parameters, applying any custom overrides."""
    disease = DiseaseLibrary.covid19_variant(config.variant)

    # Legacy flat overrides
    if config.custom_r0 is not None:
        disease.R0 = config.custom_r0
    if config.custom_mortality is not None:
        disease.mortality_rate = config.custom_mortality
    if config.custom_incubation_mean is not None:
        disease.incubation_period["mean"] = config.custom_incubation_mean

    custom = config.custom_params
    if custom:
        if custom.name:
            disease.name = custom.name
        if custom.r0 is not None:
            disease.R0 = custom.r0
        if custom.mortality_rate is not None:
            disease.mortality_rate = custom.mortality_rate
        if custom.hospitalization_rate is not None:
            disease.hospitalization_rate = custom.hospitalization_rate
        if custom.incubation_mean is not None:
            disease.incubation_period["mean"] = custom.incubation_mean
        if custom.incubation_std is not None:
            disease.incubation_period["std"] = custom.incubation_std
        if custom.infectious_mean is not None:
            disease.infectious_period["mean"] = custom.infectious_mean
        if custom.infectious_std is not None:
            disease.infectious_period["std"] = custom.infectious_std
        if custom.seasonality_amplitude is not None:
            disease.seasonality_amplitude = custom.seasonality_amplitude
        if custom.seasonality_peak is not None:
            disease.seasonality_peak = custom.seasonality_peak

        severities = (custom.p_asymptomatic, custom.p_mild, custom.p_severe, custom.p_critical)
        if any(s is not None for s in severities):
            disease.p_asymptomatic = custom.p_asymptomatic if custom.p_asymptomatic is not None else disease.p_asymptomatic
            disease.p_mild = custom.p_mild if custom.p_mild is not None else disease.p_mild
            disease.p_severe = custom.p_severe if custom.p_severe is not None else disease.p_severe
            disease.p_critical = custom.p_critical if custom.p_critical is not None else disease.p_critical

    # Re-run validation/normalisation after the overrides
    disease.__post_init__()
    return disease


def build_intervention_schedule(config: SimulationConfig) -> List[Dict[str, Any]]:
    """Combine the preset scenario with any user-defined interventions.

    Everything the simulator applies comes from this one schedule, so an
    intervention can only ever fire on the day it is scheduled for.
    """
    schedule = InterventionSchedule()
    schedule.create_preset_scenario(config.intervention_scenario)
    entries = list(schedule.scheduled_interventions)

    # The vaccination-rate slider tunes the preset campaign when the scenario
    # has one, and introduces one when it does not.
    if config.vaccination_rate > 0:
        vaccination_entries = [e for e in entries if e["type"] == "vaccination"]
        if vaccination_entries:
            for entry in vaccination_entries:
                entry["params"]["rate"] = config.vaccination_rate
        elif config.intervention_scenario != "no_intervention":
            entries.append({
                "day": 30,
                "type": "vaccination",
                "params": {"rate": config.vaccination_rate, "efficacy": 0.9, "priority": "age"},
            })

    # The compliance slider applies to every intervention that takes one.
    for entry in entries:
        if "compliance" in entry["params"]:
            entry["params"]["compliance"] = config.compliance_rate

    for custom in config.custom_interventions:
        entries.append({"day": custom.day, "type": custom.type, "params": dict(custom.params)})

    entries.sort(key=lambda e: e["day"])
    return entries


def _to_python(value):
    """Convert numpy scalars/arrays into JSON-serialisable Python values."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, list):
        return [_to_python(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_python(v) for k, v in value.items()}
    return value


def build_network_snapshot(simulator: UltimateSimulator) -> Dict[str, Any]:
    """Build the sampled 3D network payload for the visualisation tab.

    The frontend used to invent node positions and re-roll each node's state
    every day from the daily compartment proportions, which made individuals
    flicker between recovered and susceptible. This ships real nodes, real
    edges and each node's real state timeline instead.
    """
    G = simulator.G
    all_nodes = list(G.nodes())

    if len(all_nodes) > VIS_MAX_NODES:
        # Keep the highest-degree nodes plus a random sample so the sampled
        # graph keeps its hubs and stays connected enough to look like a network
        by_degree = sorted(all_nodes, key=lambda n: G.degree(n), reverse=True)
        hub_count = VIS_MAX_NODES // 3
        sampled = set(by_degree[:hub_count])
        remaining = [n for n in all_nodes if n not in sampled]
        rng = np.random.default_rng(42)
        extra = rng.choice(len(remaining), size=VIS_MAX_NODES - len(sampled), replace=False)
        sampled.update(remaining[int(i)] for i in extra)
        sampled_nodes = [n for n in all_nodes if n in sampled]
    else:
        sampled_nodes = all_nodes

    subgraph = G.subgraph(sampled_nodes)
    positions = nx.spring_layout(subgraph, dim=3, seed=42, iterations=30)

    index_of_node = {node: i for i, node in enumerate(all_nodes)}
    node_payload = []
    for node in sampled_nodes:
        pos = positions[node]
        node_payload.append({
            "id": int(node),
            "x": round(float(pos[0]) * 20, 3),
            "y": round(float(pos[1]) * 20, 3),
            "z": round(float(pos[2]) * 20, 3),
            "age": int(G.nodes[node].get("age", 30)),
            "degree": int(G.degree(node)),
        })

    sampled_index = {node: i for i, node in enumerate(sampled_nodes)}
    edges = [
        [sampled_index[u], sampled_index[v]]
        for u, v in subgraph.edges()
    ][:VIS_MAX_EDGES]

    # Downsample the timeline so playback stays smooth on long simulations
    total_frames = len(simulator.state_frames)
    stride = max(1, total_frames // VIS_MAX_FRAMES) if total_frames else 1
    frame_indices = list(range(0, total_frames, stride))

    frames = []
    for frame_idx in frame_indices:
        day_states = simulator.state_frames[frame_idx]
        frames.append("".join(
            day_states[index_of_node[node]][0] for node in sampled_nodes
        ))

    return {
        "nodes": node_payload,
        "edges": edges,
        # Each frame is a string with one character per node, in `nodes` order
        "frames": frames,
        "frame_days": [simulator.history["time"][i] for i in frame_indices],
        "sampled": len(sampled_nodes) < len(all_nodes),
        "total_nodes": len(all_nodes),
        "total_edges": G.number_of_edges(),
    }


def build_detailed_data(simulator: UltimateSimulator, history: Dict[str, List]) -> Dict[str, Any]:
    """Assemble the derived series and distributions the charts consume."""
    G = simulator.G
    n_days = len(history["time"])
    zeros = [0] * n_days

    # Cumulative infections tracked from the actual transmission counts. Taking
    # a difference of the susceptible pool instead counted every vaccination as
    # a new case.
    daily_new_cases = history.get("new_infections", zeros)
    cumulative_cases = list(np.cumsum(daily_new_cases)) if daily_new_cases else []

    detailed: Dict[str, Any] = {
        "daily_new_cases": daily_new_cases,
        "cumulative_cases": [int(c) for c in cumulative_cases],
        "daily_deaths": history.get("daily_deaths", zeros),
        "daily_hospitalizations": history.get("daily_hospitalizations", zeros),
        "new_hospitalizations": history.get("new_hospitalizations", zeros),
        "severity_breakdown": {
            "asymptomatic": history.get("Ia", zeros),
            "mild": history.get("Im", zeros),
            "severe": history.get("Is", zeros),
            "hospitalized": history.get("Ih", zeros),
            "critical": history.get("Ic", zeros),
        },
        "hospital_capacity": {
            "beds_used": simulator.stats.get("hospital_bed_usage", []),
            # A rough 1 bed per 100 people, consistent with OECD-scale capacity
            "capacity": max(1, int(G.number_of_nodes() * 0.01)),
        },
        "r_effective": simulator.stats.get("r_effective", []),
    }

    # Age distribution of everyone who was ever infected (E, I, R and D all
    # count - the old version only looked at three states and undercounted).
    age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 100]
    infected_ages = [
        G.nodes[n].get("age", 30)
        for n in G.nodes()
        if G.nodes[n].get("state") in ("E", "I", "R", "D")
    ]
    counts = np.histogram(infected_ages, bins=age_bins)[0] if infected_ages else np.zeros(len(age_bins) - 1)
    detailed["age_distribution"] = {"bins": age_bins, "counts": counts.astype(int).tolist()}

    degrees = [d for _, d in G.degree()]
    degree_counts, degree_bins = np.histogram(degrees, bins=20)
    detailed["degree_distribution"] = {
        "bins": [round(float(b), 2) for b in degree_bins],
        "counts": degree_counts.astype(int).tolist(),
    }

    mobilities = [G.nodes[n].get("mobility", 0.5) for n in G.nodes()]
    mobility_counts, mobility_bins = np.histogram(mobilities, bins=10, range=(0, 1))
    detailed["mobility_distribution"] = {
        "bins": [round(float(b), 2) for b in mobility_bins],
        "counts": mobility_counts.astype(int).tolist(),
    }

    age_group_labels = ["0-17", "18-29", "30-49", "50-69", "70+"]
    clustering_bins = [0, 18, 30, 50, 70, 200]
    clustering = []
    for i in range(len(clustering_bins) - 1):
        group_nodes = [
            n for n in G.nodes()
            if clustering_bins[i] <= G.nodes[n].get("age", 30) < clustering_bins[i + 1]
        ]
        if len(group_nodes) > 1:
            clustering.append(round(nx.average_clustering(G.subgraph(group_nodes)), 4))
        else:
            clustering.append(0.0)
    detailed["social_clustering"] = {"age_groups": age_group_labels, "clustering": clustering}

    return detailed


def _prune_simulations():
    """Drop the oldest finished simulations so memory stays bounded."""
    with _simulations_lock:
        if len(active_simulations) <= MAX_STORED_SIMULATIONS:
            return
        finished = [
            sim_id for sim_id, sim in active_simulations.items()
            if sim["status"] in ("completed", "failed")
        ]
        for sim_id in sorted(finished)[: len(active_simulations) - MAX_STORED_SIMULATIONS]:
            active_simulations.pop(sim_id, None)


def _update(simulation_id: str, **fields):
    with _simulations_lock:
        if simulation_id in active_simulations:
            active_simulations[simulation_id].update(fields)


# ==================== SIMULATION RUNNER ====================

def run_simulation(simulation_id: str, config: SimulationConfig):
    """Run a simulation. Plain `def` so FastAPI schedules it on a worker
    thread and the event loop stays free to answer status polls."""
    try:
        _update(simulation_id, status="running")

        G = generate_network(config.network)
        _update(simulation_id, network_info={
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "avg_degree": round(
                sum(d for _, d in G.degree()) / max(1, G.number_of_nodes()), 3
            ),
            "network_type": config.network.network_type,
        })

        disease = get_disease_params(config.disease)
        simulator = UltimateSimulator(G, disease)
        simulator.seed_infections(
            min(config.n_seed_infections, G.number_of_nodes()),
            method=config.seed_method,
        )
        simulator.scheduled_interventions = build_intervention_schedule(config)

        total = config.simulation_days
        for day in range(total):
            simulator.step(1)
            _update(
                simulation_id,
                current_day=day + 1,
                progress=round((day + 1) / total * 100, 1),
            )

        history = {key: _to_python(value) for key, value in simulator.history.items()
                   if key != "interventions"}
        summary = _to_python(simulator.get_summary_stats())

        _update(
            simulation_id,
            status="completed",
            current_day=total,
            progress=100,
            history=history,
            summary=summary,
            detailed_data=_to_python(build_detailed_data(simulator, history)),
            network_snapshot=build_network_snapshot(simulator),
        )
        logger.info("[%s] Simulation completed", simulation_id)

    except Exception as exc:  # noqa: BLE001 - surfaced to the client verbatim
        logger.error("[%s] Simulation failed: %s", simulation_id, exc)
        logger.debug(traceback.format_exc())
        _update(simulation_id, status="failed", error=str(exc))


# ==================== API ENDPOINTS ====================

@app.get("/api")
async def api_root():
    return {
        "message": "EpiVirus Pandemic Simulation API",
        "version": app.version,
        "endpoints": {
            "simulation": "/api/simulation",
            "status": "/api/simulation/{id}/status",
            "results": "/api/simulation/{id}/results",
            "network": "/api/simulation/{id}/network",
            "diseases": "/api/diseases",
            "networks": "/api/networks",
        },
    }


@app.get("/api/diseases")
async def get_diseases():
    """Available disease variants, read from the same library the engine uses."""
    return {
        "diseases": [
            {
                "id": variant,
                "name": params.name,
                "r0": params.R0,
                "mortality_rate": params.mortality_rate,
                "description": description,
            }
            for variant, description in (
                ("wildtype", "Original COVID-19 variant"),
                ("alpha", "Alpha variant (B.1.1.7)"),
                ("delta", "Delta variant (B.1.617.2)"),
                ("omicron", "Omicron variant (B.1.1.529)"),
            )
            for params in [DiseaseLibrary.covid19_variant(variant)]
        ]
    }


@app.get("/api/networks")
async def get_networks():
    return {
        "networks": [
            {"id": "hybrid", "name": "Hybrid Multilayer",
             "description": "Realistic social network with households, workplaces, and schools"},
            {"id": "erdos_renyi", "name": "Erdős-Rényi",
             "description": "Random network with uniform connection probability"},
            {"id": "watts_strogatz", "name": "Watts-Strogatz",
             "description": "Small-world network with clustering and short paths"},
            {"id": "barabasi_albert", "name": "Barabási-Albert",
             "description": "Scale-free network with power-law degree distribution"},
            {"id": "stochastic_block", "name": "Stochastic Block",
             "description": "Community-structured network"},
        ]
    }


@app.get("/api/scenarios")
async def get_scenarios():
    return {
        "scenarios": [
            {"id": "no_intervention", "name": "No Intervention",
             "description": "Natural epidemic spread with no countermeasures"},
            {"id": "rapid_response", "name": "Rapid Response",
             "description": "Masks day 7, testing day 14, distancing day 21, vaccination day 30"},
            {"id": "delayed_response", "name": "Delayed Response",
             "description": "Masks day 30, distancing day 45, vaccination day 60, lockdown day 75"},
            {"id": "herd_immunity", "name": "Herd Immunity",
             "description": "Mass vaccination campaign from day 0, no other measures"},
            {"id": "full_lockdown", "name": "Full Lockdown",
             "description": "Strict lockdown from day 14, reopening day 45, vaccination day 50"},
        ]
    }


@app.post("/api/simulation")
async def create_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start a simulation and return immediately with its id."""
    _prune_simulations()

    simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    with _simulations_lock:
        active_simulations[simulation_id] = {
            "status": "initializing",
            "current_day": 0,
            "total_days": config.simulation_days,
            "progress": 0,
            "config": config.model_dump(),
            "history": None,
            "summary": None,
            "network_info": None,
        }

    background_tasks.add_task(run_simulation, simulation_id, config)

    return {"simulation_id": simulation_id, "status": "initializing",
            "message": "Simulation started"}


def _get_simulation(simulation_id: str) -> Dict[str, Any]:
    with _simulations_lock:
        sim = active_simulations.get(simulation_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@app.get("/api/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    sim = _get_simulation(simulation_id)
    return {
        "simulation_id": simulation_id,
        "status": sim["status"],
        "current_day": sim["current_day"],
        "total_days": sim["total_days"],
        "progress": sim["progress"],
        "network_info": sim.get("network_info"),
        "error": sim.get("error"),
    }


@app.get("/api/simulation/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    sim = _get_simulation(simulation_id)

    if sim["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Simulation status is '{sim['status']}', not completed",
        )

    return {
        "simulation_id": simulation_id,
        "status": sim["status"],
        "history": sim["history"],
        "summary": sim["summary"],
        "network_info": sim["network_info"],
        "config": sim["config"],
        "detailed_data": sim.get("detailed_data", {}),
    }


@app.get("/api/simulation/{simulation_id}/network")
async def get_simulation_network(simulation_id: str):
    """Real node positions, edges and per-day states for the 3D network view."""
    sim = _get_simulation(simulation_id)

    if sim["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Simulation status is '{sim['status']}', not completed",
        )

    snapshot = sim.get("network_snapshot")
    if not snapshot:
        raise HTTPException(status_code=404, detail="No network snapshot for this simulation")
    return snapshot


@app.delete("/api/simulation/{simulation_id}")
async def delete_simulation(simulation_id: str):
    _get_simulation(simulation_id)
    with _simulations_lock:
        active_simulations.pop(simulation_id, None)
    return {"message": "Simulation deleted"}


@app.get("/api/simulations")
async def list_simulations():
    with _simulations_lock:
        simulations = [
            {
                "simulation_id": sim_id,
                "status": sim["status"],
                "progress": sim["progress"],
                "network_type": sim["config"]["network"]["network_type"],
                "disease_variant": sim["config"]["disease"]["variant"],
            }
            for sim_id, sim in active_simulations.items()
        ]
    return {"simulations": simulations}


# ==================== FRONTEND SERVING ====================

STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = (STATIC_DIR / full_path).resolve()
        # Keep path traversal from escaping the static directory
        if candidate.is_file() and STATIC_DIR.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info("Starting EpiVirus API on http://0.0.0.0:%d (docs at /docs)", port)
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=False, log_level="info")
