# EpiVirus — Pandemic Simulation Platform

A full-stack, network-based epidemic simulation platform implementing the **SEIRD** compartmental model with age stratification, 5 network topologies, pharmaceutical and non-pharmaceutical interventions, and 30+ real-time charts rendered in the browser.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Simulation Model](#simulation-model)
5. [Data Flow](#data-flow)
6. [API Reference](#api-reference)
7. [Local Development](#local-development)
8. [Docker](#docker)
10. [Configuration Reference](#configuration-reference)

---

## Project Overview

EpiVirus models how infectious diseases spread through a population represented as a contact network. Each node is a person; each edge is a potential transmission route. The simulation advances one day at a time, computing probabilistic transmission events and scheduled disease state transitions.

**Key features:**

- SEIRD model with 5 infectious severity levels (asymptomatic through critical)
- 9-age-group stratification with realistic COVID-19 parameters
- 5 network topologies (hybrid multilayer, Erdos-Renyi, Watts-Strogatz, Barabasi-Albert, Stochastic Block)
- 9 intervention types with preset scenarios (no intervention, rapid response, delayed response, herd immunity)
- 3D network visualization (Three.js / WebGL) with per-node color coding and animation playback
- 30+ interactive charts (Recharts) covering SEIRD dynamics, healthcare burden, age distribution, R-effective trajectory
- REST API (FastAPI) with background simulation execution and polling

---

## Architecture

```
+------------------------------------------------------------------+
|                       BROWSER (React SPA)                        |
|                                                                  |
|  +-----------------+  +------------------+  +----------------+  |
|  | SimulationConfig|  |ComprehensiveCharts|  |   Network3D    |  |
|  |  (form inputs)  |  |  (Recharts 2D)   |  |  (Three.js 3D) |  |
|  +--------+--------+  +------------------+  +----------------+  |
|           |                    ^                      ^          |
|           | POST /api/simulation                      |          |
|           | GET  /api/simulation/{id}/status (poll)   |          |
|           | GET  /api/simulation/{id}/results         |          |
|           v                    |                      |          |
|        App.jsx (state hub, polling, result fanout)    |          |
+------------------------------------------------------------------+
                         |  HTTP / JSON
                         v
+------------------------------------------------------------------+
|                   FASTAPI BACKEND  (:8000)                       |
|                                                                  |
|  POST /api/simulation                                            |
|    |  +------------------------------------------+             |
|    |  |          BackgroundTask                  |             |
|    |  |  1. UltimateNetworkGenerator             |             |
|    |  |     -> generates NetworkX graph G        |             |
|    |  |  2. DiseaseLibrary.covid19_variant()     |             |
|    |  |     -> DiseaseParameters object          |             |
|    |  |  3. UltimateSimulator(G, disease)        |             |
|    |  |     -> seed_infections()                 |             |
|    |  |     -> attach InterventionSchedule       |             |
|    |  |     -> run(days=N)                       |             |
|    |  |  4. get_summary_stats()                  |             |
|    |  |  5. serialize -> active_simulations      |             |
|    |  +------------------------------------------+             |
|    |                                                             |
|    v                                                             |
|  returns simulation_id                                           |
|                                                                  |
|  GET /api/simulation/{id}/status -> progress %                   |
|  GET /api/simulation/{id}/results -> full JSON payload           |
+------------------------------------------------------------------+
                         |
                         v
+------------------------------------------------------------------+
|                  SIMULATION ENGINE  (Python)                     |
|                                                                  |
|  UltimateSimulator.run(days)                                     |
|  +-----------------------------------------------------------+  |
|  |  for each day:                                            |  |
|  |    1. _process_events()   <- fire scheduled state changes |  |
|  |    2. _apply_scheduled_interventions()  <- from schedule  |  |
|  |    3. _transmission_step()  <- for each I node,           |  |
|  |         for each susceptible neighbor,                    |  |
|  |         calculate P(transmission) and stochastically      |  |
|  |         call _infect_node(contact)                        |  |
|  |    4. immunity waning update for all nodes                |  |
|  |    5. _record_history()   <- append counts to history     |  |
|  |    6. _update_statistics() <- peak, R_eff, hospital       |  |
|  +-----------------------------------------------------------+  |
|                                                                  |
|  +-----------------+  +----------------+  +------------------+  |
|  | network_generator|  | disease_models |  | DiseaseProgres  |  |
|  |  (5 topologies)  |  | (variants,calc)|  |  sion (events)  |  |
|  +-----------------+  +----------------+  +------------------+  |
+------------------------------------------------------------------+
```

### File Structure

```
EpiVirus/
├── backend/                     # Python backend
│   ├── api_server.py            # FastAPI app, endpoints, background tasks
│   ├── simulator_engine.py      # UltimateSimulator (SEIRD state machine)
│   ├── disease_models.py        # DiseaseParameters, TransmissionCalculator,
│   │                            #   DiseaseProgression, InterventionSchedule
│   ├── network_generator.py     # UltimateNetworkGenerator (5 topologies)
│   ├── animation_simulator.py   # Frame-by-frame animation data
│   └── requirements.txt
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── App.jsx              # State hub, polling, result routing
│   │   └── components/
│   │       ├── ui/              # Layout primitives
│   │       │   ├── Header.jsx
│   │       │   └── LoadingSpinner.jsx
│   │       ├── config/          # All simulation input forms
│   │       │   ├── SimulationConfig.jsx
│   │       │   ├── CustomDiseaseBuilder.jsx
│   │       │   ├── AdvancedNetworkConfig.jsx
│   │       │   └── AdvancedInterventionBuilder.jsx
│   │       ├── charts/          # 2D data visualizations
│   │       │   ├── ComprehensiveCharts.jsx
│   │       │   ├── AdvancedCharts.jsx
│   │       │   └── EpidemicChart.jsx
│   │       ├── visualization/   # 3D and animation
│   │       │   ├── Network3D.jsx
│   │       │   └── AnimationTab.jsx
│   │       └── results/         # Results display and summaries
│   │           ├── SimulationResults.jsx
│   │           ├── OverviewTab.jsx
│   │           └── NetworkInfo.jsx
│   ├── vite.config.js           # Dev proxy /api -> localhost:8000
│   └── package.json
│
├── Dockerfile                   # Multi-stage (Node build + Python runtime)
└── README.md
```

---

## Tech Stack

| Layer | Technology | Version | Role |
|-------|-----------|---------|------|
| Frontend framework | React | 19.2 | SPA, state, UI |
| Build tool | Vite | 7.x | Bundling, dev proxy |
| Styling | Tailwind CSS | 4.x | Utility classes |
| 2D charts | Recharts | 3.6 | 30+ chart types |
| 3D visualization | Three.js + @react-three/fiber | 0.182 / 9.4 | WebGL network render |
| API framework | FastAPI | 0.115 | REST API, async |
| ASGI server | Uvicorn | 0.32 | HTTP server |
| Validation | Pydantic v2 | 2.10 | Request/response models |
| Graph library | NetworkX | 3.1 | Network generation and analysis |
| Numerics | NumPy / SciPy | 1.24 / 1.11 | Distributions, array ops |
| Containerization | Docker | multi-stage | Build and runtime |

---

## Simulation Model

### Compartments (SEIRD + sublevels)

```
                     +---------------------------------------+
                     |           INFECTIOUS (I)              |
                     |  Ia    Im    Is    Ih    Ic            |
S --> E -----------> |  (asymptomatic to critical)           | --> R
                     +---------------------------------------+
                                       |
                                       v
                                       D
```

| State | Label | Description |
|-------|-------|-------------|
| S | Susceptible | Not yet infected |
| E | Exposed | Infected, not yet infectious (incubation) |
| Ia | Asymptomatic | Infectious, no symptoms (~40% of cases) |
| Im | Mild | Infectious, mild symptoms (~40%) |
| Is | Severe | Infectious, severe — may hospitalize (~15%) |
| Ih | Hospitalized | In hospital, oxygen support |
| Ic | Critical | ICU / mechanical ventilation |
| R | Recovered | Immune (waning natural immunity) |
| D | Deceased | Fatal outcome |
| V | Vaccinated | Protected with reduced susceptibility |

### State Transitions

Every infection schedules time-based events on a sorted event queue:

```
_infect_node(node):
  schedule become_infectious  after incubation_days  ~ N(mean, std)
  schedule hospitalize        after hospital_day      (if severe/critical)
  schedule die   OR  recover  (mutually exclusive)
```

The event queue is processed at the start of each simulated day by `_process_events()`. Transition times are sampled once at infection time from truncated normal distributions, so the disease course is deterministic per individual after that point.

### Transmission Probability Formula

For each (infector, contact) pair where contact is in state S:

```
P = base x age x mobility x contact_type x interventions
    x masks x immunity x seasonality x environment x symptoms
```

| Factor | Formula / Values |
|--------|-----------------|
| base | R0 x 2/(avg_degree + 2) x 0.08 |
| age | susceptibility from age_stratification table |
| mobility | mean of infector + susceptible mobility scores (0-1) |
| contact_type | household 2.0, school 1.5, workplace 1.2, hub 1.8, random 0.8; multiplied by edge weight |
| interventions | lockdown isolation: x0.1; social distancing: x(1 - eff x compliance) |
| masks | both masked: (1-eff)^2; one masked: 1 - 0.3eff; no masks: 1.0 |
| immunity | 1 - current_immunity (wanes after waning_start days) |
| seasonality | 1 + amplitude x cos(2pi(day - peak)/365) |
| environment | x0.7 with improved ventilation; x0.2 on outdoor edges |
| symptoms | asymptomatic infectors: x0.3 |

Final probability clamped to [0.0, 0.99].

### Age Stratification

| Age Group | Susceptibility | Hospitalization Rate | Mortality |
|-----------|----------------|---------------------|-----------|
| 0-9 | 50% | 8% | 0.1% |
| 10-19 | 70% | 12% | 0.2% |
| 20-29 | 90% | 20% | 0.5% |
| 30-39 | 90% | 35% | 1.0% |
| 40-49 | 90% | 50% | 2.0% |
| 50-59 | 90% | 65% | 5.0% |
| 60-69 | 95% | 80% | 12% |
| 70-79 | 95% | 90% | 28% |
| 80+ | 95% | 95% | 45% |

### Disease Variants (COVID-19)

| Variant | R0 | Mortality | p_asym | p_mild | p_severe | p_critical |
|---------|-----|-----------|--------|--------|----------|------------|
| Wildtype | 2.5 | 2.0% | 40% | 40% | 15% | 5% |
| Alpha | 4.0 | 2.5% | 30% | 45% | 18% | 7% |
| Delta | 5.0 | 3.0% | 25% | 45% | 22% | 8% |
| Omicron | 9.5 | 1.0% | 35% | 50% | 12% | 3% |

All four variants have severity probabilities that sum to exactly 1.0, validated at initialization.

### Network Topologies

| Type | Algorithm | Best For |
|------|-----------|----------|
| Hybrid Multilayer | Watts-Strogatz base + household/workplace/school/random layers | Most realistic social structure |
| Erdos-Renyi | G(N,p) uniform random | Baseline with no structure |
| Watts-Strogatz | Ring lattice + rewiring | Small-world (high clustering, short paths) |
| Barabasi-Albert | Preferential attachment | Scale-free with super-spreader hubs |
| Stochastic Block | Community probability matrix | Distinct communities / schools |

### Intervention Scenarios

| Scenario | Timeline |
|----------|---------|
| no_intervention | No interventions; natural epidemic spread |
| rapid_response | Masks day 7, testing day 14, distancing day 21, vaccination day 30, travel restrictions day 45 |
| delayed_response | Masks day 30, distancing day 45, vaccination day 60, lockdown day 75, reopen day 120 |
| herd_immunity | Mass vaccination from day 0 (5%/day tapering to 2%) |
| full_lockdown | Strict lockdown + masks + travel restrictions from day 14, reopen day 45 |

---

## Data Flow

```
User submits config form
        |
        v
POST /api/simulation  -> returns { simulation_id }
        |
        v (background task)
  generate_network()        -> NetworkX graph G
  get_disease_params()      -> DiseaseParameters
  UltimateSimulator(G, dp)
    .seed_infections(n, method)
    .scheduled_interventions = InterventionSchedule(scenario)
    .run(days=N)
      |
      | for each day 0..N:
      |   _process_events()              <- become_infectious, die, recover
      |   _apply_scheduled_interventions <- fires scenario events on correct day
      |   _transmission_step()          <- P(trans) for each I-S neighbor pair
      |   DiseaseProgression.update_immunity()
      |   _record_history()             <- S,E,I,R,D,V,Ia,Im,Is,Ih,Ic,...
      |   _update_statistics()          <- peak, R_eff, hospital_bed_usage
      |
      v
  get_summary_stats()   -> attack_rate, CFR, peak_day, ...
  serialize history
  active_simulations[id] = { status:"completed", history, summary, ... }

Frontend polls GET /api/simulation/{id}/status (every 2s)
        |
        +-- status "running"  -> spinner + progress bar
        +-- status "completed"
              |
              v
        GET /api/simulation/{id}/results
              |
              v
        React distributes data to:
          OverviewTab          <- summary cards, key metrics
          ComprehensiveCharts  <- 30+ Recharts visualizations
          Network3D            <- Three.js 3D node-link diagram
          AnimationTab         <- frame-by-frame playback
```

---

## API Reference

### Base URL
- Development: `http://localhost:8000`
- Production: `https://<your-service>.onrender.com`

### Endpoints

#### `GET /api`
Returns API version and endpoint listing.

#### `GET /api/diseases`
Returns available COVID-19 variants with R0 and mortality.

#### `GET /api/networks`
Returns available network topology definitions.

#### `POST /api/simulation`
Start a new simulation. Returns immediately; simulation runs in a background task.

Request body:
```json
{
  "network": {
    "population": 1000,
    "network_type": "hybrid"
  },
  "disease": {
    "variant": "omicron"
  },
  "n_seed_infections": 10,
  "seed_method": "random",
  "simulation_days": 120,
  "intervention_scenario": "no_intervention",
  "vaccination_rate": 0.0,
  "compliance_rate": 0.8
}
```

Response:
```json
{ "simulation_id": "sim_20260607_123456", "status": "initializing" }
```

#### `GET /api/simulation/{id}/status`
Poll for progress (frontend polls every 2 seconds).

```json
{
  "status": "running",
  "current_day": 45,
  "total_days": 120,
  "progress": 37.5
}
```

#### `GET /api/simulation/{id}/results`
Fetch full results once `status == "completed"`.

Key response fields:
- `history` — per-day arrays for S, E, I, R, D, V, Ia, Im, Is, Ih, Ic, daily_deaths, daily_hospitalizations
- `summary` — attack_rate, peak_infections, peak_day, total_deaths, CFR, total_vaccinated, total_hospitalized
- `detailed_data` — daily_new_cases, severity_breakdown, age_distribution, degree_distribution, social_clustering, hospital_capacity, r_effective

#### `GET /api/simulations`
List all in-memory simulations.

#### `DELETE /api/simulation/{id}`
Remove simulation from memory.

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+

### Backend

```bash
cd EpiVirus/backend
pip install -r requirements.txt
python api_server.py
# API at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Frontend

```bash
cd EpiVirus/frontend
npm install
npm run dev
# Dev server at http://localhost:5173
# Vite automatically proxies /api/* to http://localhost:8000
```

---

## Docker

### Build

```bash
cd EpiVirus
docker build -t epivirus .
```

The multi-stage Dockerfile:

```
Stage 1: node:20-alpine
  COPY client/ && npm ci && npm run build
  Output: /app/client/dist

Stage 2: python:3.11-slim
  pip install -r requirements.txt
  COPY src/ -> /app/
  COPY dist/ -> /app/static/    (served by FastAPI catch-all)
  CMD ["python", "api_server.py"]
```

### Run locally

```bash
docker run -p 8000:8000 epivirus
# Open http://localhost:8000
```

---



### Performance Sizing

| Population | Sim Days | Min RAM | Render Plan |
|------------|----------|---------|-------------|
| up to 500 | 120 | 256 MB | Free (spins down) |
| up to 2000 | 180 | 1 GB | Starter ($7/mo) |
| up to 5000 | 180 | 2 GB | Standard ($25/mo) |
| 10000 | 365 | 4 GB | Standard+ |

> The free tier spins down after 15 minutes of inactivity. The first request after spin-down takes 30-60 seconds while the container restarts. Use a paid plan for always-on availability.

---

## Configuration Reference

### Network Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| population | 1000 | 100-10000 | Number of nodes (people) |
| network_type | hybrid | see below | Contact network topology |
| erdos_p | 0.01 | 0.001-0.1 | Edge probability (Erdos-Renyi only) |
| watts_k | 8 | 2-20 | Neighbors in ring (Watts-Strogatz only) |
| watts_p | 0.3 | 0-1 | Rewiring probability (Watts-Strogatz only) |
| barabasi_m | 3 | 1-10 | Edges per new node (Barabasi-Albert only) |

### Simulation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| n_seed_infections | 10 | Initial infected individuals |
| seed_method | random | random, hubs, mobile, geographic, age_targeted |
| simulation_days | 120 | Total days to simulate |
| vaccination_rate | 0.0 | Daily fraction of susceptibles vaccinated (0-0.05) |
| compliance_rate | 0.8 | Fraction of population complying with interventions |

---

## Simulation Correctness Notes

The following correctness properties have been verified in the code:

- **Probability normalization**: `p_asymptomatic + p_mild + p_severe + p_critical = 1.0` is asserted in `DiseaseParameters.__post_init__`
- **Exclusive outcomes**: A node is scheduled for either `die` or `recover`, never both
- **State set integrity**: Nodes are discarded from old state sets before being added to new ones
- **Daily deaths tracking**: Computed as `total_deaths - previous_total_deaths` (delta) each day, not from D set size
- **Transmission bound**: Final probability is clamped to [0.0, 0.99]
- **Intervention isolation**: The scheduler only fires events from the selected scenario; no hidden hardcoded interventions apply
- **Waning immunity**: Exponential decay after `waning_start` days for both natural (R) and vaccine (V) immunity
- **Vaccinated nodes**: State V nodes have reduced susceptibility via immunity factor and cannot be re-infected through the normal S-check in `_transmission_step`
