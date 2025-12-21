# 🦠 EpiVirus - Advanced Pandemic Simulation Platform

<div align="center">

**A comprehensive, full-stack epidemic modeling and visualization platform for simulating disease spread across complex social networks**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 19.2](https://img.shields.io/badge/React-19.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-system-architecture) • [Documentation](#-documentation) • [API](#-api-reference)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Installation](#-detailed-installation)
- [Usage Guide](#-usage-guide)
- [Visualization Suite](#-visualization-suite)
- [Disease Models](#-disease-models)
- [Network Topologies](#-network-topologies)
- [Intervention Strategies](#-intervention-strategies)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Performance](#-performance)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**EpiVirus** is a sophisticated epidemiological modeling platform that combines cutting-edge computational epidemiology with modern web technologies. It enables researchers, public health officials, and educators to:

- 🔬 **Simulate** disease spread across realistic social networks (households, schools, workplaces)
- 📊 **Visualize** epidemic dynamics through 18+ interactive charts and 3D network animations
- 🎛️ **Experiment** with intervention strategies (lockdowns, vaccination, testing, contact tracing)
- 📈 **Analyze** outcomes across multiple disease variants and network structures
- 🚀 **Deploy** simulations via dual interfaces: modern React SPA or Python Streamlit dashboard

### Why EpiVirus?

Unlike simplified SIR models, EpiVirus implements:
- **SEIRD compartmental models** with age stratification and severity levels
- **Realistic network topologies** (scale-free, small-world, multilayer social graphs)
- **Intervention dynamics** with compliance modeling and temporal scheduling
- **Real-time 3D visualization** using Three.js with force-directed network layouts
- **Production-ready REST API** for integration with existing public health systems

---

## ✨ Key Features

### 🧬 Advanced Epidemiological Modeling
- **SEIRD+ Compartmental Model**: Susceptible → Exposed → Infectious → Recovered/Deceased with 5 severity levels
- **Age-Stratified Parameters**: Different transmission, hospitalization, and mortality rates by age group (9 bins: 0-9, 10-19, ..., 80+)
- **Multiple Disease Variants**: Pre-configured COVID-19 variants with accurate parameters
  - **Wildtype**: R₀ = 2.5, Mortality = 2.0%
  - **Alpha (B.1.1.7)**: R₀ = 4.0, Mortality = 2.5%
  - **Delta (B.1.617.2)**: R₀ = 6.0, Mortality = 3.0%
  - **Omicron (B.1.1.529)**: R₀ = 10.0, Mortality = 1.0%
- **Custom Disease Builder**: Define your own disease parameters
- **Time-Varying Reproduction Number**: R(t) calculation with mobility and intervention adjustments

### 🕸️ Network-Based Transmission
- **5 Network Topologies**:
  1. **Hybrid Multilayer**: Realistic social structure with households, schools, workplaces, community layers
  2. **Erdős-Rényi**: Random graphs with configurable connection probability
  3. **Watts-Strogatz**: Small-world networks with high clustering coefficient
  4. **Barabási-Albert**: Scale-free networks with power-law degree distribution
  5. **Stochastic Block Model**: Community-structured networks
- **Network Attributes**: Age, mobility, household size, workplace, comorbidities
- **Edge Types**: Household (strong), workplace (medium), school (medium), community (weak)
- **Configurable Parameters**: Population size (100-10,000), connection probabilities, clustering

### 💉 Intervention System
- **Pharmaceutical Interventions**:
  - Vaccination campaigns with age prioritization
  - Antiviral treatments with efficacy modeling
  - Waning immunity tracking over time
- **Non-Pharmaceutical Interventions (NPIs)**:
  - Lockdowns (partial/full) with compliance rates
  - Social distancing with mobility reduction
  - Mask mandates with source control modeling
  - School/workplace closures
  - Travel restrictions
  - Contact tracing with isolation
- **Pre-configured Scenarios**:
  - No intervention (baseline)
  - Rapid response (early lockdown + vaccination)
  - Delayed response (late intervention)
  - Herd immunity (natural spread)
- **Custom Intervention Builder**: Design multi-stage intervention strategies

### 📊 Comprehensive Visualization Suite (18+ Charts)

#### 2D Analytics Dashboard
1. **SEIR Dynamics Chart**: Multi-line time series of compartment populations
2. **Daily New Infections**: Bar chart with 7-day moving average
3. **Stacked Area Chart**: Population states over time
4. **Severity Breakdown**: 5-level stacked chart (asymptomatic → critical)
5. **Cumulative Statistics**: Total infections, recoveries, deaths
6. **Attack Rate Progression**: Epidemic impact over time
7. **R-Effective Chart**: Time-varying reproduction number with R=1 threshold
8. **Healthcare System Load**: Hospital bed utilization vs. capacity
9. **Age Distribution (Pie)**: Infections by age group
10. **Age Distribution (Bar)**: Age histogram with demographics
11. **Degree Distribution**: Network connectivity analysis
12. **Active vs Recovered**: Comparative bar charts
13. **Infection Rate Indicator**: Weekly trend with color-coded status (🔴🟠🟡🟢)
14-18. **Custom SVG Charts**: High-performance custom renderings

#### 3D Interactive Network Visualization
- **WebGL-Powered 3D Graph**: Three.js + React Three Fiber rendering
- **Force-Directed Layout**: Real-time physics-based node positioning
- **Color-Coded States**: 
  - Blue = Susceptible
  - Yellow = Exposed
  - Red = Infectious (pulsing animation)
  - Green = Recovered
  - Black = Deceased
- **Animation Playback Controls**:
  - ▶️ Play/Pause disease spread over time
  - 🎚️ Timeline scrubber to jump to any day
  - ⚡ Speed controls (0.5x, 1x, 2x, 4x)
  - ⏮️ Reset to initial state
- **Orbital Camera**: Rotate, zoom, pan with mouse/touch controls
- **Real-time Statistics Overlay**: Live count of S, E, I, R, D populations

### 🖥️ Dual Frontend Options

#### Option 1: React SPA (Recommended)
- **Modern Tech Stack**: React 19.2, Vite 7.2, Tailwind CSS 4.1
- **Component Architecture**: 16 custom components with responsive design
- **Chart Libraries**: 
  - Recharts 3.6 (professional charting library)
  - Custom SVG renderers for performance
- **3D Engine**: Three.js 0.182 + @react-three/fiber + @react-three/drei
- **Real-time Updates**: Polling every 2 seconds during simulation
- **Tab-Based Navigation**: Overview, Simulation Config, 2D Charts, 3D Network
- **Modern UI**: Purple gradient theme with glassmorphism effects

#### Option 2: Streamlit Dashboard
- **Python-Native**: No JavaScript required
- **Plotly Interactive Charts**: Zoom, pan, export to PNG
- **Auto-Refresh**: Real-time progress tracking
- **CSV Export**: Download simulation results
- **Rapid Prototyping**: Perfect for Jupyter Notebook workflows
- **Minimal Setup**: Single command to launch

### 🚀 Backend API (Python + FastAPI)
- **RESTful Architecture**: 10+ endpoints for full simulation lifecycle
- **Background Tasks**: Asynchronous simulation execution
- **Pydantic Validation**: Type-safe request/response models
- **CORS Enabled**: Ready for cross-origin requests
- **In-Memory Storage**: Fast simulation state management
- **Error Handling**: Comprehensive exception handling with detailed logs
- **Auto-Generated Docs**: Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│  ┌────────────────────────┐      ┌─────────────────────────────┐ │
│  │   React Frontend       │      │   Streamlit Dashboard       │ │
│  │   localhost:5173       │  OR  │   localhost:8501            │ │
│  │  ✓ 18+ Charts          │      │  ✓ Plotly Charts            │ │
│  │  ✓ 3D Network          │      │  ✓ Auto-refresh             │ │
│  │  ✓ Real-time updates   │      │  ✓ CSV export               │ │
│  └────────────┬───────────┘      └──────────────┬──────────────┘ │
└───────────────┼──────────────────────────────────┼────────────────┘
                │                                  │
                │         HTTP/REST API            │
                └──────────────┬───────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Python)                        │
│                      localhost:8000                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  api_server.py - RESTful API Server                        │  │
│  │  ├─ POST   /api/simulation          (Start simulation)     │  │
│  │  ├─ GET    /api/simulation/{id}     (Get status)           │  │
│  │  ├─ GET    /api/simulation/{id}/results  (Get data)        │  │
│  │  ├─ GET    /api/diseases             (List variants)       │  │
│  │  ├─ GET    /api/networks             (List topologies)     │  │
│  │  ├─ GET    /api/simulations          (List all)            │  │
│  │  └─ DELETE /api/simulation/{id}      (Cleanup)             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               │                                   │
│                               ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         SIMULATION ENGINE (Core Logic)                     │  │
│  │                                                             │  │
│  │  simulator_engine.py - UltimateSimulator                   │  │
│  │  ├─ SEIRD state machine with age stratification           │  │
│  │  ├─ Intervention system (lockdowns, vaccination, etc.)    │  │
│  │  ├─ R(t) calculation with mobility adjustment             │  │
│  │  ├─ Hospital capacity tracking                            │  │
│  │  ├─ Contact tracing and isolation                         │  │
│  │  └─ Event queue for scheduled interventions               │  │
│  │                                                             │  │
│  │  disease_models.py - DiseaseLibrary                        │  │
│  │  ├─ COVID-19 variants (Wildtype, Alpha, Delta, Omicron)   │  │
│  │  ├─ Age-stratified parameters (9 age groups)              │  │
│  │  ├─ Severity probabilities (5 levels)                     │  │
│  │  └─ Vaccine efficacy modeling with waning                 │  │
│  │                                                             │  │
│  │  network_generator.py - UltimateNetworkGenerator           │  │
│  │  ├─ Hybrid multilayer (households + workplaces + schools) │  │
│  │  ├─ Erdős-Rényi (random graphs)                          │  │
│  │  ├─ Watts-Strogatz (small-world)                         │  │
│  │  ├─ Barabási-Albert (scale-free)                         │  │
│  │  ├─ Stochastic Block (communities)                       │  │
│  │  └─ Node attributes (age, mobility, comorbidities)       │  │
│  │                                                             │  │
│  │  animation_simulator.py - 3D visualization data           │  │
│  │  └─ Frame-by-frame state snapshots for animation          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               │                                   │
│                               ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           DATA PROCESSING & ANALYTICS                      │  │
│  │  ├─ Daily new cases (from cumulative susceptible drop)    │  │
│  │  ├─ Severity breakdown (5 categories)                     │  │
│  │  ├─ Age distribution histograms (9 bins)                  │  │
│  │  ├─ Degree distribution (network topology)                │  │
│  │  ├─ R-effective time series                               │  │
│  │  ├─ Hospital capacity utilization                         │  │
│  │  ├─ Attack rate calculation                               │  │
│  │  └─ Peak detection (infections, deaths, hospitalizations) │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow Sequence

1. **User Configuration** → Frontend collects simulation parameters
2. **API Request** → POST to `/api/simulation` with JSON payload
3. **Background Task** → FastAPI launches async simulation task
4. **Network Generation** → Build social network with specified topology
5. **Initialization** → Seed infections, assign node attributes
6. **Time-Step Loop** → For each day (t=0 to t=simulation_days):
   - Calculate transmission probabilities (network-based)
   - Update disease states (S→E→I→R/D transitions)
   - Apply interventions (if scheduled)
   - Collect statistics (new cases, hospitalizations, etc.)
   - Store daily snapshot for visualization
7. **Post-Processing** → Calculate derived metrics (R(t), attack rate, peaks)
8. **Result Storage** → Save to in-memory dict with simulation_id
9. **Client Polling** → Frontend polls `/api/simulation/{id}/status` every 2s
10. **Result Retrieval** → On completion, fetch `/api/simulation/{id}/results`
11. **Visualization** → Render 18+ charts + 3D network animation

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core runtime |
| **FastAPI** | 0.115.5 | REST API framework |
| **Uvicorn** | 0.32.1 | ASGI server |
| **Pydantic** | 2.10.3 | Data validation |
| **NetworkX** | 3.1 | Graph algorithms |
| **NumPy** | 1.24.3 | Numerical computing |
| **Pandas** | 2.0.3 | Data manipulation |
| **SciPy** | 1.11.2 | Scientific computing |
| **Matplotlib** | 3.7.2 | Static visualizations |
| **TQDM** | 4.66.1 | Progress bars |

### Frontend (React)
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI framework |
| **Vite** | 7.2.4 | Build tool & dev server |
| **Tailwind CSS** | 4.1.18 | Utility-first styling |
| **Recharts** | 3.6.0 | Chart library |
| **Three.js** | 0.182.0 | 3D graphics engine |
| **@react-three/fiber** | 9.4.2 | React renderer for Three.js |
| **@react-three/drei** | 10.7.7 | Three.js helpers |
| **ESLint** | 9.39.1 | Code linting |

### Frontend (Streamlit)
| Technology | Version | Purpose |
|------------|---------|---------|
| **Streamlit** | Latest | Python web framework |
| **Plotly** | Latest | Interactive charts |

---

## 🚀 Quick Start

### Prerequisites
- **Python** 3.8 or higher
- **Node.js** 18 or higher
- **npm** or **yarn**
- **Git** (for cloning repository)

### 30-Second Setup (Windows)

```powershell
# Clone repository
git clone https://github.com/yourusername/EpiVirus.git
cd EpiVirus

# Run complete setup script (installs dependencies + starts servers)
.\start_complete.ps1

# Wait ~10 seconds, then visit:
# React App: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### 1. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

#### 2. Frontend Setup (React)

```bash
# Navigate to client directory
cd client

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

React app will be available at: **http://localhost:5173**

#### 3. Alternative: Streamlit Frontend

```bash
# From project root
pip install streamlit plotly

# Start Streamlit app
streamlit run streamlit_app.py
```

Streamlit app will be available at: **http://localhost:8501**

---

## 📦 Detailed Installation

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for dependencies
- **CPU**: Multi-core recommended for large simulations (10,000+ nodes)

### Backend Installation

```bash
# Clone repository
git clone https://github.com/yourusername/EpiVirus.git
cd EpiVirus/server

# Create isolated Python environment
python -m venv venv

# Activate environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, networkx, numpy; print('✓ All dependencies installed')"

# Run server
uvicorn api_server:app --reload
```

### Frontend Installation (React)

```bash
cd client

# Install dependencies
npm install

# Verify installation
npm list --depth=0

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Frontend Installation (Streamlit)

```bash
# Install Streamlit
pip install streamlit plotly requests pandas

# Run app
streamlit run streamlit_app.py

# Run with custom port
streamlit run streamlit_app.py --server.port 8502
```

---

## 📖 Usage Guide

### Running Your First Simulation

1. **Start Backend**: 
   ```bash
   cd server
   uvicorn api_server:app --reload
   ```

2. **Start Frontend**: 
   ```bash
   cd client
   npm run dev
   ```

3. **Open Browser**: Navigate to http://localhost:5173

4. **Configure Simulation** (Left Panel):
   - **Disease**: Select "COVID-19 (Delta)"
   - **Network**: Choose "Hybrid Multilayer"
   - **Population**: 1000 nodes
   - **Simulation Days**: 180
   - **Seed Infections**: 10
   - **Intervention**: "Rapid Response"
   - **Vaccination Rate**: 0.5% per day

5. **Run Simulation**: Click "Run Simulation" button

6. **Monitor Progress**: Watch real-time progress bar (updates every 2 seconds)

7. **View Results**:
   - **Overview Tab**: Summary cards (peak infections, attack rate, total deaths)
   - **2D Charts Tab**: Scroll through 18+ visualizations
   - **3D Network Tab**: Interactive 3D graph with animation controls

### Advanced Configuration

#### Custom Disease Parameters
```json
POST /api/simulation
{
  "disease": {
    "variant": "custom",
    "custom_r0": 5.5,
    "custom_mortality": 0.015,
    "custom_incubation_mean": 4.5
  },
  "network": {
    "population": 2000,
    "network_type": "barabasi_albert",
    "barabasi_m": 5
  },
  "simulation_days": 200
}
```

#### Network Topology Tuning
```json
{
  "network": {
    "population": 5000,
    "network_type": "watts_strogatz",
    "watts_k": 12,
    "watts_p": 0.25
  }
}
```

---

## 📊 Visualization Suite

### 2D Charts (18 Total)

#### Epidemic Dynamics
1. **SEIR Dynamics Chart**: Line chart showing S, E, I, R, D populations over time
2. **Stacked Area Chart**: Filled area chart of compartment distribution
3. **Daily New Infections**: Bar + line combo with 7-day moving average
4. **Daily New Cases (Custom SVG)**: High-performance custom rendering

#### Healthcare & Severity
5. **Severity Breakdown Chart**: 5-level stacked area
   - Asymptomatic (light blue)
   - Mild (yellow)
   - Severe (orange)
   - Hospitalized (red)
   - Critical (dark red)
6. **Healthcare System Chart**: Hospital bed utilization vs. capacity
7. **Active vs Recovered**: Grouped bar comparison

#### Cumulative Metrics
8. **Cumulative Statistics Chart**: Running totals
9. **Attack Rate Chart**: Percentage of population ever infected

#### Demographics
10. **Age Distribution (Pie)**: Infections by 9 age groups
11. **Age Distribution (Bar)**: Age histogram
12. **Age Distribution (Custom SVG)**: Alternative rendering

#### Network Analysis
13. **Degree Distribution (Recharts)**: Network connectivity
14. **Degree Distribution (Custom SVG)**: Alternative histogram

#### Advanced Metrics
15. **R-Effective Chart**: Time-varying reproduction number
16. **Infection Rate Indicator**: Weekly trend with color-coded status
    - 🔴 Red: >100 cases/week (critical)
    - 🟠 Orange: 50-100 cases/week (high)
    - 🟡 Yellow: 10-50 cases/week (moderate)
    - 🟢 Green: <10 cases/week (low)

### 3D Network Visualization

**Features**:
- 100-200 node network rendered in WebGL
- Physics-based force-directed layout
- Real-time disease spread animation
- Color-coded nodes by state
- Pulsing animation for infected nodes
- Orbital camera controls (rotate, zoom, pan)
- Animation controls (play, pause, speed, timeline)
- Statistics overlay

**Controls**:
| Action | How To |
|--------|--------|
| **Rotate** | Left click + drag |
| **Zoom** | Scroll wheel |
| **Pan** | Right click + drag |
| **Play Animation** | Click ▶️ button |
| **Jump to Day** | Drag timeline slider |
| **Speed Control** | Select 0.5x / 1x / 2x / 4x |
| **Reset View** | Click ⏮️ button |

---

## 🧬 Disease Models

### COVID-19 Variants

| Variant | R₀ | Incubation (days) | Mortality | Notes |
|---------|-----|-------------------|-----------|-------|
| **Wildtype** | 2.5 | 5.2 ± 2.8 | 2.0% | Original strain (Wuhan) |
| **Alpha (B.1.1.7)** | 4.0 | 5.0 ± 2.5 | 2.5% | ~60% more transmissible |
| **Delta (B.1.617.2)** | 6.0 | 4.5 ± 2.0 | 3.0% | ~100% more transmissible |
| **Omicron (B.1.1.529)** | 10.0 | 3.5 ± 1.5 | 1.0% | Highly transmissible, lower severity |

### Severity Classification

| Level | Name | Description | Hospitalization | ICU | Mortality |
|-------|------|-------------|-----------------|-----|-----------|
| **Ia** | Asymptomatic | No symptoms | No | No | 0.01% |
| **Im** | Mild | Fever, cough, home care | No | No | 0.1% |
| **Is** | Severe | Pneumonia, hospital admission | Yes | No | 2% |
| **Ih** | Hospitalized | Oxygen support, hospitalized | Yes | Sometimes | 10% |
| **Ic** | Critical | Mechanical ventilation, ICU | Yes | Yes | 30% |

### Age-Stratified Parameters

| Age Group | Susceptibility | Hospitalization | Mortality | % of Population |
|-----------|----------------|-----------------|-----------|-----------------|
| **0-9** | 50% | 0.5% | 0.01% | 12% |
| **10-19** | 70% | 1% | 0.02% | 13% |
| **20-29** | 90% | 2% | 0.1% | 14% |
| **30-39** | 90% | 3% | 0.3% | 14% |
| **40-49** | 90% | 5% | 1% | 13% |
| **50-59** | 90% | 8% | 3% | 13% |
| **60-69** | 90% | 15% | 8% | 11% |
| **70-79** | 90% | 25% | 15% | 7% |
| **80+** | 90% | 35% | 25% | 3% |

---

## 🕸️ Network Topologies

### 1. Hybrid Multilayer Network (Recommended)
**Description**: Most realistic social structure combining multiple layers

**Layers**:
- **Household**: High-contact, 2-5 people per household
- **Workplace**: Medium-contact, 10-50 people per workplace
- **School**: Medium-contact, age-segregated, 20-100 students per school
- **Community**: Weak-contact, random neighborhood connections

**Parameters**:
- `population`: 100-10,000
- No additional parameters

**Use Case**: Most realistic simulations for policy evaluation

---

### 2. Erdős-Rényi (Random Graph)
**Description**: Each edge exists with independent probability `p`

**Parameters**:
- `population`: 100-10,000
- `erdos_p`: Edge probability (default: 0.01)

**Properties**:
- Mean degree: `p × (N-1)`
- Low clustering coefficient
- Binomial degree distribution

**Use Case**: Baseline comparisons, theoretical studies

---

### 3. Watts-Strogatz (Small-World)
**Description**: High clustering + short path lengths

**Parameters**:
- `population`: 100-10,000
- `watts_k`: Number of nearest neighbors (default: 8, must be even)
- `watts_p`: Rewiring probability (default: 0.3)

**Properties**:
- High clustering (when p is small)
- Short average path length
- Models "six degrees of separation"

**Use Case**: Social networks with tight-knit clusters

---

### 4. Barabási-Albert (Scale-Free)
**Description**: Preferential attachment → power-law degree distribution

**Parameters**:
- `population`: 100-10,000
- `barabasi_m`: Edges to attach from new node (default: 3)

**Properties**:
- Power-law degree distribution: P(k) ~ k^(-γ)
- Hub nodes with very high connectivity
- Robust to random failures, vulnerable to targeted attacks

**Use Case**: Modeling super-spreader events

---

### 5. Stochastic Block Model (Community Structure)
**Description**: Network with distinct communities

**Parameters**:
- `population`: 100-10,000
- `block_intra`: Within-community edge probability (default: 0.15)
- `block_inter`: Between-community edge probability (default: 0.01)

**Properties**:
- Modular structure (4 equal-sized communities by default)
- High intra-community connectivity
- Low inter-community connectivity

**Use Case**: Geographic regions, school districts, demographic groups

---

## 💉 Intervention Strategies

### Pre-configured Scenarios

#### 1. No Intervention (Baseline)
- No lockdowns
- No vaccination
- No NPIs
- **Use Case**: Baseline comparison, natural epidemic progression

#### 2. Rapid Response
- **Lockdown**: Day 30-60 (80% mobility reduction, 80% compliance)
- **Vaccination**: Starts day 60 (0.5% per day)
- **Outcome**: Flattens curve early, reduces peak infections

#### 3. Delayed Response
- **Lockdown**: Day 60-90 (late intervention)
- **Vaccination**: Starts day 90
- **Outcome**: Higher peak infections, more deaths

#### 4. Herd Immunity
- No interventions
- Natural spread until R(t) < 1
- **Outcome**: High attack rate (60-80%), high mortality

### Custom Interventions

#### Lockdown Configuration
```json
{
  "intervention_scenario": "custom",
  "interventions": [
    {
      "type": "lockdown",
      "start_day": 40,
      "end_day": 80,
      "mobility_reduction": 0.7,
      "compliance_rate": 0.85
    }
  ]
}
```

#### Vaccination Campaign
```json
{
  "vaccination_rate": 0.01,
  "vaccine_efficacy": {
    "infection": 0.7,
    "severity": 0.9,
    "transmission": 0.6
  },
  "age_priority": [80, 70, 60, 50, 40, 30, 20, 10, 0]
}
```

#### Mask Mandate
```json
{
  "type": "mask_mandate",
  "start_day": 10,
  "end_day": 180,
  "compliance": 0.9,
  "efficacy": 0.5
}
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Get API Information
```http
GET /
```

**Response**:
```json
{
  "name": "EpiVirus Pandemic Simulation API",
  "version": "1.0.0",
  "status": "running"
}
```

---

#### 2. List Available Diseases
```http
GET /api/diseases
```

**Response**:
```json
{
  "diseases": [
    {
      "variant": "wildtype",
      "name": "COVID-19 (Wildtype)",
      "R0": 2.5,
      "mortality": 0.02
    },
    {
      "variant": "delta",
      "name": "COVID-19 (Delta)",
      "R0": 6.0,
      "mortality": 0.03
    }
  ]
}
```

---

#### 3. List Available Network Types
```http
GET /api/networks
```

**Response**:
```json
{
  "networks": [
    {
      "type": "hybrid",
      "name": "Hybrid Multilayer",
      "description": "Realistic social structure",
      "parameters": []
    },
    {
      "type": "erdos_renyi",
      "name": "Erdős-Rényi",
      "description": "Random graph",
      "parameters": ["erdos_p"]
    }
  ]
}
```

---

#### 4. Start a New Simulation
```http
POST /api/simulation
Content-Type: application/json
```

**Request Body**:
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
  "simulation_days": 180,
  "intervention_scenario": "rapid_response",
  "vaccination_rate": 0.005,
  "compliance_rate": 0.8,
  "animate": true,
  "animation_step": 2
}
```

**Response**:
```json
{
  "simulation_id": "sim_20251221_143025",
  "status": "running",
  "message": "Simulation started successfully"
}
```

---

#### 5. Get Simulation Status
```http
GET /api/simulation/{simulation_id}/status
```

**Response (Running)**:
```json
{
  "simulation_id": "sim_20251221_143025",
  "status": "running",
  "current_day": 45,
  "total_days": 180,
  "progress": 0.25
}
```

**Response (Completed)**:
```json
{
  "simulation_id": "sim_20251221_143025",
  "status": "completed",
  "current_day": 180,
  "total_days": 180,
  "progress": 1.0
}
```

---

#### 6. Get Simulation Results
```http
GET /api/simulation/{simulation_id}/results
```

**Response**:
```json
{
  "simulation_id": "sim_20251221_143025",
  "status": "completed",
  "history": {
    "S": [990, 988, 985, ...],
    "E": [5, 8, 12, ...],
    "I": [5, 4, 3, ...],
    "R": [0, 0, 0, ...],
    "D": [0, 0, 0, ...]
  },
  "detailed_data": {
    "daily_new_cases": [10, 3, 5, ...],
    "severity": {
      "asymptomatic": [4, 3, 2, ...],
      "mild": [3, 2, 1, ...],
      "severe": [2, 1, 1, ...],
      "hospitalized": [1, 1, 0, ...],
      "critical": [0, 0, 0, ...]
    },
    "age_distribution": {
      "0-9": 5,
      "10-19": 8,
      ...
    },
    "degree_distribution": {
      "0-5": 10,
      "6-10": 50,
      ...
    },
    "r_effective": [2.5, 2.3, 2.1, ...],
    "hospital_capacity": [0.1, 0.2, 0.3, ...]
  },
  "summary": {
    "total_infected": 450,
    "total_recovered": 400,
    "total_deaths": 15,
    "peak_infections": 120,
    "peak_day": 45,
    "attack_rate": 0.45,
    "final_size": 0.47
  },
  "network_info": {
    "nodes": 1000,
    "edges": 3456,
    "average_degree": 6.9,
    "clustering_coefficient": 0.32
  }
}
```

---

#### 7. List All Simulations
```http
GET /api/simulations
```

**Response**:
```json
{
  "simulations": [
    {
      "simulation_id": "sim_20251221_143025",
      "status": "completed",
      "created_at": "2025-12-21T14:30:25"
    },
    {
      "simulation_id": "sim_20251221_120000",
      "status": "running",
      "created_at": "2025-12-21T12:00:00"
    }
  ]
}
```

---

#### 8. Delete a Simulation
```http
DELETE /api/simulation/{simulation_id}
```

**Response**:
```json
{
  "message": "Simulation deleted successfully",
  "simulation_id": "sim_20251221_143025"
}
```

---

## 📁 Project Structure

```
EpiVirus-main/
├── 📁 server/                          # Python backend
│   ├── api_server.py                   # FastAPI REST API server
│   ├── requirements.txt                # Python dependencies
│   ├── README.md                       # Backend documentation
│   ├── kaggle.py                       # Kaggle dataset integration
│   ├── test_3d_plot.html              # 3D visualization test
│   ├── 📁 src/                        # Core simulation modules
│   │   ├── simulator_engine.py        # UltimateSimulator class (SEIRD model)
│   │   ├── disease_models.py          # DiseaseLibrary + parameters
│   │   ├── network_generator.py       # UltimateNetworkGenerator (5 topologies)
│   │   ├── animation_simulator.py     # 3D visualization data generator
│   │   ├── main_dashboard.py          # Dashboard utilities
│   │   └── visualization_3d.py        # 3D plotting functions
│   └── 📁 parameter_sweeps/           # Saved simulation sweeps
│       └── sweep_20251219_220853/     # Example parameter sweep
│           ├── results.csv
│           ├── optimal_strategy_minimize_deaths.json
│           └── REPORT.md
│
├── 📁 client/                          # React frontend
│   ├── package.json                    # Node.js dependencies
│   ├── vite.config.js                  # Vite configuration
│   ├── eslint.config.js                # ESLint configuration
│   ├── index.html                      # Entry HTML
│   ├── README.md                       # Frontend documentation
│   ├── 📁 public/                     # Static assets
│   └── 📁 src/                        # React source code
│       ├── App.jsx                     # Main app component
│       ├── main.jsx                    # React entry point
│       ├── index.css                   # Global styles
│       ├── App.css                     # App-specific styles
│       ├── 📁 components/             # React components (16 total)
│       │   ├── Header.jsx              # App header
│       │   ├── SimulationConfig.jsx    # Configuration panel
│       │   ├── SimulationResults.jsx   # Results display
│       │   ├── NetworkInfo.jsx         # Network statistics
│       │   ├── EpidemicChart.jsx       # Basic SEIR chart
│       │   ├── LoadingSpinner.jsx      # Loading animation
│       │   ├── OverviewTab.jsx         # Overview dashboard
│       │   ├── AnimationTab.jsx        # Animation controls
│       │   ├── ComprehensiveCharts.jsx # 12 Recharts components
│       │   ├── AdvancedCharts.jsx      # 5 custom SVG charts
│       │   ├── Network3D.jsx           # 3D network visualization
│       │   ├── CustomDiseaseBuilder.jsx        # Custom disease UI
│       │   ├── AdvancedNetworkConfig.jsx       # Advanced network config
│       │   └── AdvancedInterventionBuilder.jsx # Intervention builder
│       └── 📁 assets/                 # Images, icons
│
├── streamlit_app.py                    # Streamlit frontend (alternative)
├── start.ps1                           # PowerShell: Start backend only
├── start_streamlit.ps1                 # PowerShell: Start backend + Streamlit
├── start_complete.ps1                  # PowerShell: Full setup (backend + React)
├── README.md                           # 👈 This file (main documentation)
├── ARCHITECTURE.md                     # System architecture details
├── IMPLEMENTATION_SUMMARY.md           # Development summary
├── QUICK_START.md                      # Quick start guide
├── INTEGRATION_GUIDE.md                # Integration guide
└── BACKEND_FRONTEND_MATCHING.md        # API matching documentation
```

---

## 🔧 Development

### Backend Development

#### Running Tests
```bash
cd server
pytest tests/ -v
```

#### Running with Hot Reload
```bash
uvicorn api_server:app --reload --log-level debug
```

#### Adding a New Disease Variant
Edit `server/src/disease_models.py`:
```python
variants["new_variant"] = DiseaseParameters(
    name="COVID-19 (New Variant)",
    R0=7.5,
    p_asymptomatic=0.3,
    p_mild=0.4,
    p_severe=0.2,
    p_critical=0.1,
    mortality_rate=0.025
)
```

### Frontend Development (React)

#### Running Tests
```bash
cd client
npm test
```

#### Building for Production
```bash
npm run build
# Output: dist/ folder
```

#### Linting
```bash
npm run lint
```

#### Adding a New Chart Component
Create `client/src/components/MyNewChart.jsx`:
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export function MyNewChart({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="day" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="metric" stroke="#8884d8" />
    </LineChart>
  );
}
```

---

## ⚡ Performance

### Simulation Performance

| Population | Network Type | Simulation Days | Avg Time | Memory |
|------------|--------------|-----------------|----------|--------|
| 100 | Hybrid | 180 | 2s | 50MB |
| 500 | Hybrid | 180 | 5s | 100MB |
| 1,000 | Hybrid | 180 | 10s | 200MB |
| 5,000 | Hybrid | 180 | 50s | 800MB |
| 10,000 | Hybrid | 180 | 2min | 1.5GB |

### Optimization Techniques

1. **Network Generation**: 
   - Cached neighbor lookups
   - Sparse adjacency lists (NetworkX)
   - O(N + E) complexity

2. **Simulation Loop**:
   - Set-based state tracking (O(1) lookups)
   - Vectorized NumPy operations
   - Event-driven intervention system

3. **3D Visualization**:
   - WebGL rendering (GPU-accelerated)
   - Force-directed layout caching
   - Downsampling for large networks (100-200 nodes displayed)

4. **Frontend**:
   - React.memo for chart components
   - Debounced polling (2s intervals)
   - Lazy loading for 3D assets

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-new-feature`
3. **Make changes** with clear commit messages
4. **Add tests** for new functionality
5. **Run linting**: `npm run lint` (frontend) or `flake8` (backend)
6. **Submit a pull request**

### Code Style

- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Follow Airbnb style guide, use ES6+
- **Comments**: Document complex algorithms and public APIs

### Areas for Contribution

- [ ] Additional disease models (influenza, measles, etc.)
- [ ] More network topologies (spatial, temporal)
- [ ] Advanced interventions (testing, quarantine, contact tracing)
- [ ] Performance optimizations for large networks (>10,000 nodes)
- [ ] Machine learning for parameter estimation
- [ ] Export results to PDF/Excel
- [ ] Real-time collaboration features
- [ ] Mobile app (React Native)

---

## 🧮 Algorithms & Data Structures

### Core Algorithms

#### 1. Network Generation Algorithms

##### Erdős-Rényi Random Graph (G(n,p) Model)
```
Algorithm: ER_Graph(n, p)
Input: n nodes, edge probability p
Output: Random graph G

Time Complexity: O(n²)
Space Complexity: O(n + e) where e = expected edges

1. Initialize empty graph G with n nodes
2. For each pair (i, j) where i < j:
   a. Generate random number r ∈ [0,1]
   b. If r < p:
      - Add edge (i, j) to G
3. Return G

Properties:
- Expected edges: p × n(n-1)/2
- Degree distribution: Binomial (approximates Poisson for large n)
- Low clustering coefficient
```

##### Watts-Strogatz Small-World Network
```
Algorithm: WS_Graph(n, k, p)
Input: n nodes, k nearest neighbors, rewiring probability p
Output: Small-world graph G

Time Complexity: O(nk)
Space Complexity: O(n + nk)

1. Create ring lattice:
   For i = 0 to n-1:
      For j = 1 to k/2:
         Add edge (i, (i+j) mod n)

2. Rewire edges with probability p:
   For each edge (i, j):
      Generate random r ∈ [0,1]
      If r < p:
         Remove edge (i, j)
         Select random node v (not i, not neighbor of i)
         Add edge (i, v)

3. Return G

Properties:
- High clustering coefficient (from lattice)
- Short average path length (from random rewiring)
- "Six degrees of separation" phenomenon
```

##### Barabási-Albert Scale-Free Network (Preferential Attachment)
```
Algorithm: BA_Graph(n, m)
Input: n nodes, m edges per new node
Output: Scale-free graph G

Time Complexity: O(n × m)
Space Complexity: O(n + nm)

1. Initialize G with m₀ fully connected nodes
2. For i = m₀ to n-1:
   a. Create new node i
   b. Select m target nodes with probability proportional to degree:
      P(connect to j) = degree(j) / Σ(degree(k))
   c. Add edges from i to selected targets
3. Return G

Properties:
- Power-law degree distribution: P(k) ~ k^(-γ) where γ ≈ 3
- Hub nodes with very high degree
- "Rich get richer" dynamics
- Robust to random failures, vulnerable to targeted attacks
```

##### Hybrid Multilayer Network
```
Algorithm: HybridMultilayer(n)
Input: population size n
Output: Multilayer social network G

Time Complexity: O(n + e_total)
Space Complexity: O(n + e_total)

1. Base Layer - Small World:
   G = WS_Graph(n, k=6, p=0.2)

2. Household Layer:
   household_size ~ Poisson(λ=3)
   For each household:
      Create complete subgraph K_size
      Set edge_type = "household"
      Set edge_weight = 1.0 (strong)

3. Workplace Layer:
   workplace_size ~ Uniform(10, 50)
   adults = nodes where age ≥ 18 and age < 65
   Partition adults into workplaces
   For each workplace:
      Create ER_Graph(size, p=0.3)
      Set edge_type = "workplace"
      Set edge_weight = 0.6 (medium)

4. School Layer:
   school_size ~ Uniform(50, 200)
   children = nodes where age < 18
   Partition by age groups (K-5, 6-8, 9-12)
   For each school:
      Create grade-based clusters
      Add inter-grade edges (p=0.1)
      Set edge_type = "school"
      Set edge_weight = 0.7 (medium-strong)

5. Community Layer:
   For each node i:
      Select 5-10 random neighbors within distance d
      Add weak community edges
      Set edge_type = "community"
      Set edge_weight = 0.3 (weak)

6. Return G with multiple edge types

Network Statistics:
- Average degree: 8-12
- Clustering coefficient: 0.3-0.4
- Average path length: 4-6
- Modular structure with overlapping communities
```

---

#### 2. Disease Spread Simulation (SEIRD Model)

##### Discrete-Time SEIRD Simulation
```
Algorithm: SEIRD_Simulation(G, disease_params, T)
Input: 
  - G: Social network graph
  - disease_params: Disease parameters (R0, incubation, mortality, etc.)
  - T: Simulation days

Output: Time series of states {S(t), E(t), I(t), R(t), D(t)}

Time Complexity: O(T × (N + E)) per timestep
Space Complexity: O(T × N) for history

Data Structures:
- state_sets: Dict[str, Set[int]] - Fast O(1) state lookups
- transition_queue: Deque[Tuple[int, str, int]] - Scheduled state changes
- infection_tree: Dict[int, List[int]] - Contact tracing graph
- history: Dict[str, List[int]] - Time series data

Algorithm:
1. Initialization:
   states = {node: 'S' for node in G.nodes()}
   state_sets = {'S': set(G.nodes()), 'E': set(), 'I': set(), 'R': set(), 'D': set()}
   
2. Seed Infections:
   Select seed_nodes (random or by degree)
   For each seed in seed_nodes:
      states[seed] = 'E'
      state_sets['S'].remove(seed)
      state_sets['E'].add(seed)
      Schedule transition E→I at day + incubation_period

3. Main Loop (t = 0 to T-1):
   
   a. Process Transmission (Infectious → Susceptible):
      For each node i in state_sets['I']:
         For each neighbor j of i:
            If states[j] == 'S':
               # Calculate transmission probability
               p_transmit = calculate_transmission_probability(
                  i, j, G, disease_params, interventions[t]
               )
               
               If random() < p_transmit:
                  # Successful infection
                  states[j] = 'E'
                  state_sets['S'].remove(j)
                  state_sets['E'].add(j)
                  infection_tree[j] = i
                  
                  # Schedule E→I transition
                  incubation = sample_incubation_period(disease_params)
                  Schedule transition at day t + incubation
   
   b. Process State Transitions (from transition_queue):
      For each (node, new_state, scheduled_day) in queue:
         If scheduled_day == t:
            old_state = states[node]
            states[node] = new_state
            state_sets[old_state].remove(node)
            state_sets[new_state].add(node)
            
            If new_state == 'I':
               # Determine severity
               severity = assign_severity(node, disease_params)
               
               # Schedule I→R or I→D transition
               duration = sample_infectious_period(disease_params)
               
               If random() < mortality_rate[severity]:
                  Schedule (node, 'D', t + duration)
               Else:
                  Schedule (node, 'R', t + duration)
   
   c. Apply Interventions:
      If interventions[t] contains 'lockdown':
         Reduce mobility by lockdown_factor
         Reduce edge weights proportionally
      
      If interventions[t] contains 'vaccination':
         Select vaccination_rate × N nodes (priority by age)
         For each vaccinated node:
            states[node] = 'V'
            Reduce susceptibility by vaccine_efficacy
   
   d. Record Statistics:
      history['S'].append(len(state_sets['S']))
      history['E'].append(len(state_sets['E']))
      history['I'].append(len(state_sets['I']))
      history['R'].append(len(state_sets['R']))
      history['D'].append(len(state_sets['D']))
      
      Calculate R_effective(t)
      Calculate hospital_capacity_used(t)
   
   e. Check Termination:
      If len(state_sets['E']) + len(state_sets['I']) == 0:
         Break  # No more infectious individuals

4. Return history

Transmission Probability Calculation:
P(i→j at time t) = β × base_transmission × age_factor × 
                   intervention_factor × edge_weight × 
                   (1 - vaccine_protection)

where:
- β = R0 / (mean_degree × infectious_period)
- base_transmission = disease-specific constant
- age_factor = susceptibility[age_j]
- intervention_factor = (1 - mask_efficacy) × (1 - distancing_effect)
- edge_weight = strength of connection (household=1.0, work=0.6, etc.)
- vaccine_protection = vaccine_efficacy × (1 - waning_factor)
```

##### Severity Assignment Algorithm
```
Algorithm: AssignSeverity(node, disease_params)
Input: node ID, disease parameters
Output: Severity level (Ia, Im, Is, Ih, Ic)

Time Complexity: O(1)

1. Get node age: age = G.nodes[node]['age']
2. Get age-stratified probabilities from disease_params
3. Get comorbidity factor: comorbidity = G.nodes[node]['comorbidity']

4. Adjust probabilities:
   p_asymptomatic_adj = p_asymptomatic × (2.0 if age < 20 else 1.0)
   p_critical_adj = p_critical × (1.0 + comorbidity_factor)

5. Sample from categorical distribution:
   r = random()
   cumulative = 0
   
   For severity in [Ia, Im, Is, Ih, Ic]:
      cumulative += adjusted_probability[severity]
      If r < cumulative:
         Return severity

6. Return Im (default if sampling fails)

Severity Progression:
- Asymptomatic (Ia): No symptoms, lower transmission (0.5×)
- Mild (Im): Home care, normal transmission
- Severe (Is): May need hospitalization, higher transmission
- Hospitalized (Ih): Requires hospital bed, isolated (no transmission)
- Critical (Ic): ICU, mechanical ventilation, isolated
```

---

#### 3. Graph Algorithms for Network Analysis

##### Degree Distribution Calculation
```
Algorithm: ComputeDegreeDistribution(G)
Input: Graph G
Output: Histogram of degree distribution

Time Complexity: O(N + D_max) where D_max = maximum degree
Space Complexity: O(D_max)

1. Initialize degree_counts = {}
2. For each node v in G:
   degree = G.degree(v)
   degree_counts[degree] = degree_counts.get(degree, 0) + 1

3. Create bins for histogram:
   bins = [0-5, 6-10, 11-15, 16-20, 21+]
   
4. Aggregate into bins:
   histogram = {bin: 0 for bin in bins}
   For degree, count in degree_counts:
      bin = find_bin(degree)
      histogram[bin] += count

5. Return histogram

Uses: 
- Identify super-spreaders (high-degree nodes)
- Detect scale-free vs. random network structure
- Network vulnerability analysis
```

##### Clustering Coefficient
```
Algorithm: LocalClusteringCoefficient(G, v)
Input: Graph G, node v
Output: Clustering coefficient C_v

Time Complexity: O(d²) where d = degree(v)
Space Complexity: O(d)

1. neighbors = G.neighbors(v)
2. k = len(neighbors)
3. If k < 2: return 0

4. Count triangles:
   triangles = 0
   For each pair (n1, n2) in neighbors:
      If G.has_edge(n1, n2):
         triangles += 1

5. max_possible_edges = k × (k - 1) / 2
6. C_v = triangles / max_possible_edges
7. Return C_v

Global Clustering:
C = (1/N) × Σ C_v for all v

Uses:
- Measure network cohesion
- Detect community structure
- Compare with theoretical models (Watts-Strogatz has high C)
```

##### R-Effective (Time-Varying Reproduction Number)
```
Algorithm: ComputeREffective(infection_times, recovery_times, t, window=7)
Input: 
  - infection_times: Dict[node_id, day_infected]
  - recovery_times: Dict[node_id, day_recovered]
  - t: Current day
  - window: Time window for calculation

Output: R_eff(t)

Time Complexity: O(N)
Space Complexity: O(1)

Mathematical Definition:
R_eff(t) = Average number of secondary infections caused by 
           individuals infected in time window [t-w, t]

1. Get newly infected in window:
   primary_cases = [v for v in nodes 
                    if t - window ≤ infection_times[v] < t]

2. Count secondary infections:
   total_secondary = 0
   For each v in primary_cases:
      # Count how many they infected
      secondary = count_infections_caused_by(v, infection_tree)
      total_secondary += secondary

3. R_eff(t) = total_secondary / len(primary_cases)
4. Return R_eff(t)

Epidemic Control:
- R_eff > 1: Epidemic growing
- R_eff = 1: Endemic equilibrium
- R_eff < 1: Epidemic declining

Uses:
- Real-time epidemic monitoring
- Evaluate intervention effectiveness
- Predict epidemic trajectory
```

---

#### 4. Intervention Algorithms

##### Contact Tracing with BFS
```
Algorithm: ContactTracing(G, infected_node, depth=2)
Input: Graph G, infected node, trace depth
Output: Set of nodes to quarantine

Time Complexity: O(V + E) for BFS
Space Complexity: O(V)

1. Initialize:
   to_quarantine = set()
   queue = deque([(infected_node, 0)])
   visited = set([infected_node])

2. BFS Traversal:
   While queue not empty:
      current, level = queue.popleft()
      to_quarantine.add(current)
      
      If level < depth:
         For neighbor in G.neighbors(current):
            If neighbor not in visited:
               visited.add(neighbor)
               queue.append((neighbor, level + 1))

3. Return to_quarantine

Enhanced Contact Tracing:
- Weight by edge type (household > workplace > community)
- Consider temporal interactions (time of last contact)
- Probability-based tracing (trace if P(transmission) > threshold)
```

##### Vaccination Priority Queue
```
Algorithm: VaccinationPriority(G, vaccine_doses, strategy)
Input: Graph G, available doses, prioritization strategy
Output: List of nodes to vaccinate

Time Complexity: O(N log N) for sorting
Space Complexity: O(N)

Strategies:
1. Age-Based (elderly first):
   priority_queue = sorted(nodes, key=lambda v: age(v), reverse=True)

2. Degree-Based (hubs first):
   priority_queue = sorted(nodes, key=lambda v: degree(v), reverse=True)

3. Betweenness Centrality (bridges first):
   betweenness = compute_betweenness_centrality(G)
   priority_queue = sorted(nodes, key=lambda v: betweenness[v], reverse=True)

4. Risk-Based (comorbidities + age):
   risk_score = lambda v: age(v) × 0.5 + comorbidity(v) × 0.5
   priority_queue = sorted(nodes, key=risk_score, reverse=True)

Algorithm:
1. Build priority queue based on strategy
2. vaccinated = []
3. For i = 0 to vaccine_doses:
   node = priority_queue[i]
   vaccinated.append(node)
   Apply vaccine effects to node

4. Return vaccinated

Vaccine Effects:
- Reduce susceptibility by vaccine_efficacy['infection']
- Reduce severity if breakthrough infection occurs
- Reduce transmission if infected
- Model waning immunity over time
```

---

### Data Structures

#### 1. State Sets (Disjoint Sets)
```python
state_sets = {
    'S': set(),  # Susceptible
    'E': set(),  # Exposed
    'I': set(),  # Infectious
    'R': set(),  # Recovered
    'D': set()   # Deceased
}

Operations:
- Membership test: O(1)
- Add node: O(1)
- Remove node: O(1)
- Iterate infectious: O(|I|) not O(N)

Benefit: Fast iteration over only infectious individuals instead of all nodes
```

#### 2. Priority Queue (Event Scheduler)
```python
from collections import deque
from heapq import heappush, heappop

transition_queue = []  # Min-heap by time

# Schedule transition
heappush(transition_queue, (day, node_id, new_state))

# Process transitions at current day
while transition_queue and transition_queue[0][0] == current_day:
    day, node, state = heappop(transition_queue)
    process_transition(node, state)

Time Complexity:
- Insert: O(log K) where K = queue size
- Extract min: O(log K)
- Peek: O(1)

Benefit: Efficient event-driven simulation without checking all nodes every timestep
```

#### 3. Adjacency List (NetworkX Graph)
```python
# Sparse graph representation
G = nx.Graph()

# Internally stored as:
{
    node_id: {
        neighbor_id: edge_data,
        ...
    },
    ...
}

Operations:
- Check edge existence: O(1) average
- Get neighbors: O(1)
- Iterate neighbors: O(degree)
- Add edge: O(1)
- Remove edge: O(1)

Space Complexity: O(N + E)

Benefit: Efficient for sparse graphs (E << N²)
```

#### 4. Infection Tree (Directed Acyclic Graph)
```python
infection_tree = {
    infected_node: infector_node,
    ...
}

# Reconstruct infection chains
def get_infection_chain(node):
    chain = [node]
    while node in infection_tree:
        node = infection_tree[node]
        chain.append(node)
    return chain

Uses:
- Contact tracing
- Identify super-spreaders
- Track infection sources
- Visualize transmission pathways
```

#### 5. Time Series Cache
```python
history = {
    'S': deque(maxlen=max_days),  # Circular buffer
    'E': deque(maxlen=max_days),
    'I': deque(maxlen=max_days),
    'R': deque(maxlen=max_days),
    'D': deque(maxlen=max_days)
}

# Append new data point: O(1)
history['I'].append(current_infected)

# Access last 7 days: O(7) = O(1)
last_week = list(history['I'])[-7:]

Benefit: Constant-time sliding window operations
```

---

### Optimization Techniques

#### 1. Neighbor Caching
```python
# Pre-compute and cache neighbor lists
neighbor_cache = {
    node: list(G.neighbors(node)) 
    for node in G.nodes()
}

# Access: O(1) lookup, O(degree) iteration
# Trade-off: O(E) memory for O(1) access time
```

#### 2. Vectorized Operations (NumPy)
```python
import numpy as np

# Instead of:
for i in range(n):
    result[i] = some_calculation(data[i])

# Use:
result = np.vectorize(some_calculation)(data)

Speedup: 10-100× faster due to:
- C-level loops
- SIMD instructions
- Memory locality
```

#### 3. Lazy Evaluation
```python
# Don't compute R_eff every day, only when requested
@cached_property
def r_effective_series(self):
    if not self._r_eff_cache:
        self._r_eff_cache = self._compute_r_effective()
    return self._r_eff_cache

Benefit: Avoid expensive computations unless needed
```

#### 4. Early Termination
```python
# Stop simulation if no more infections
if len(state_sets['E']) + len(state_sets['I']) == 0:
    break

Benefit: For fast-dying epidemics, save computation on empty days
```

---

### Computational Complexity Analysis

#### Simulation Overall Complexity

**Time Complexity**: `O(T × (N + E_active))`
- T: Simulation days
- N: Number of nodes
- E_active: Edges incident to infectious nodes (typically << E)

**Space Complexity**: `O(T × N + E)`
- T × N: Time series storage
- E: Network edges

#### Network Generation Complexity

| Network Type | Time | Space | Notes |
|--------------|------|-------|-------|
| Erdős-Rényi | O(N²) | O(N + E) | Check all pairs |
| Watts-Strogatz | O(NK) | O(N + NK) | Ring + rewiring |
| Barabási-Albert | O(NM) | O(N + NM) | Preferential attachment |
| Hybrid | O(N + E) | O(N + E) | Multiple layers |
| Stochastic Block | O(N²) worst | O(N + E) | Depends on block sizes |

#### Graph Algorithm Complexity

| Algorithm | Time | Space | Purpose |
|-----------|------|-------|---------|
| Degree Distribution | O(N) | O(D_max) | Network analysis |
| Clustering Coefficient | O(N × d²) | O(N) | Measure transitivity |
| Betweenness Centrality | O(N × E) | O(N + E) | Find bridges |
| Shortest Paths (BFS) | O(N + E) | O(N) | Contact tracing |
| Connected Components | O(N + E) | O(N) | Network fragmentation |

---

### Mathematical Models

#### 1. SEIR Differential Equations (Continuous)
```
dS/dt = -β × S × I / N
dE/dt = β × S × I / N - σ × E
dI/dt = σ × E - γ × I
dR/dt = γ × I

where:
- β = transmission rate (R0 × γ)
- σ = 1 / incubation_period (E→I rate)
- γ = 1 / infectious_period (I→R rate)
- N = total population
```

#### 2. Network-Based Transmission (Discrete)
```
P(i infects j at time t) = 1 - exp(-λ_ij × Δt)

where:
λ_ij = β × w_ij × susceptibility_j × infectivity_i

- w_ij = edge weight (0.3 to 1.0)
- susceptibility_j = age-based factor × (1 - vaccine_protection)
- infectivity_i = severity_factor × (1 - interventions)
```

#### 3. Effective Reproduction Number
```
R_eff(t) = R0 × S(t)/N × (1 - intervention_effect)

where:
- R0 = basic reproduction number
- S(t)/N = fraction still susceptible
- intervention_effect = Σ(1 - efficacy_i) for all interventions
```

#### 4. Attack Rate (Final Epidemic Size)
```
AR = 1 - S(∞)/N = fraction ever infected

For basic SIR: AR ≈ 1 - exp(-R0 × AR)
(implicit equation, solved numerically)
```

---

## 🎓 Advanced Features & Techniques

### 1. Age-Stratified Modeling

**Implementation**:
- 9 age groups (0-9, 10-19, ..., 80+)
- Age-specific parameters:
  - Susceptibility: Children 50% less susceptible
  - Hospitalization: Exponential increase with age
  - Mortality: 80+ has 250× higher mortality than 0-9
  - Contact patterns: Age-assortative mixing (schools, nursing homes)

**Algorithm**: WAIFW Matrix (Who Acquires Infection From Whom)
```
C_ij = contact rate between age group i and j
β_ij = transmission rate from j to i

Infection probability for age group i from group j:
λ_i = Σ_j (β_ij × C_ij × I_j / N_j)
```

### 2. Household Structure

**Implementation**:
- Household sizes: Poisson(λ=3)
- Complete graph (K_n) within household
- Strong edge weights (1.0) → High transmission
- Multi-generational households (grandparents, parents, children)

**Impact**:
- Clusters infections within families
- Early epidemic seeding in households
- Difficult to break transmission chains with NPIs

### 3. Intervention Compliance Modeling

**Stochastic Compliance**:
```python
for node in population:
    if random() < compliance_rate:
        apply_intervention(node)
    else:
        # Non-compliant: continue normal behavior
        pass
```

**Factors Affecting Compliance**:
- Age (elderly more compliant)
- Education level
- Risk perception
- Intervention fatigue (decreases over time)
- Social norms (neighbors' behavior)

### 4. Waning Immunity

**Exponential Decay Model**:
```
immunity(t) = initial_immunity × exp(-λ × t)

where:
- λ = waning rate (0.003 per day for COVID-19 vaccines)
- t = days since vaccination/infection
```

**Implementation**:
```python
for vaccinated_node in state_sets['V']:
    days_since_vaccination = current_day - vaccination_day[node]
    if days_since_vaccination > waning_start:
        protection = initial_protection × exp(-waning_rate × 
                     (days_since_vaccination - waning_start))
        if protection < 0.5:
            # Vulnerable again
            move_to_susceptible(node)
```

### 5. Hospital Capacity Constraints

**Queueing Model**:
```python
hospital_beds = 1000
icu_beds = 100

hospitalized_patients = len(state_sets['Ih'])
critical_patients = len(state_sets['Ic'])

if hospitalized_patients > hospital_beds:
    overflow = hospitalized_patients - hospital_beds
    # Increased mortality for overflow patients
    mortality_multiplier = 1.0 + 0.5 × (overflow / hospital_beds)

if critical_patients > icu_beds:
    # Triage: only sickest get ICU
    mortality_multiplier = 2.0  # Double mortality without ICU
```

### 6. Mobility Reduction

**Mobility Network Adjustment**:
```python
baseline_contacts = {
    'household': 1.0,   # Always 1.0 (can't reduce household)
    'workplace': 0.6,
    'school': 0.7,
    'community': 0.3
}

lockdown_factors = {
    'household': 1.0,
    'workplace': 0.2,   # 80% reduction (WFH)
    'school': 0.0,      # Complete closure
    'community': 0.1    # 90% reduction
}

effective_contacts = {
    layer: baseline_contacts[layer] × lockdown_factors[layer]
    for layer in ['household', 'workplace', 'school', 'community']
}
```

### 7. Asynchronous Updates (Event-Driven)

**Instead of synchronous updates (all nodes at once)**:
```python
# Event queue with priorities
events = PriorityQueue()

# Schedule events
events.put((day=5, event='E→I', node=123))
events.put((day=15, event='I→R', node=123))

# Process events in chronological order
while not events.empty():
    day, event, node = events.get()
    if day > current_day:
        current_day = day
    process_event(event, node)
```

**Benefit**: More realistic (individuals don't all transition at midnight)

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 EpiVirus Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/EpiVirus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/EpiVirus/discussions)
- **Email**: support@epivirus.io
- **Documentation**: [Full Docs](https://epivirus.io/docs)

---

## 🙏 Acknowledgments

- **NetworkX** for powerful graph algorithms
- **FastAPI** for modern Python web framework
- **React** and **Vite** for blazing-fast frontend development
- **Three.js** for stunning 3D visualizations
- **Recharts** for professional charting library
- **Tailwind CSS** for beautiful, responsive design
- Epidemiological parameters from published literature (WHO, CDC, peer-reviewed journals)

---

## 📚 References

1. **COVID-19 Parameters**:
   - Wildtype: Ferretti et al. (2020). *Science*. doi:10.1126/science.abb6936
   - Alpha: Davies et al. (2021). *Science*. doi:10.1126/science.abg3055
   - Delta: Liu & Rocklöv (2021). *J Travel Med*. doi:10.1093/jtm/taab124
   - Omicron: Garrett et al. (2022). *Cell*. doi:10.1016/j.cell.2022.01.001

2. **Network Epidemiology**:
   - Pastor-Satorras et al. (2015). *Rev Mod Phys*. doi:10.1103/RevModPhys.87.925
   - Newman (2018). *Networks*. Oxford University Press.

3. **Intervention Modeling**:
   - Ferguson et al. (2020). *Imperial College COVID-19 Response Team*. Report 9.

---

<div align="center">

**Built with ❤️ for epidemiologists, researchers, and public health professionals**

⭐ **Star this repo** if you find it useful!

[Report Bug](https://github.com/yourusername/EpiVirus/issues) • [Request Feature](https://github.com/yourusername/EpiVirus/issues) • [Documentation](https://epivirus.io/docs)

</div>
