# parameter_sweeper.py
import numpy as np
import pandas as pd
import itertools
from typing import Dict, List, Tuple, Any, Optional
import multiprocessing as mp
from tqdm import tqdm
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import project modules
from network_generator import UltimateNetworkGenerator
from disease_models import DiseaseLibrary, DiseaseParameters
from simulator_engine import UltimateSimulator

class ParameterSweeper:
    """
    Comprehensive parameter exploration for pandemic simulation
    """
    
    def __init__(self, base_config=None):
        """
        Initialize parameter sweeper with base configuration
        """
        self.base_config = base_config or self._get_default_config()
        self.results = []
        self.simulation_cache = {}
        self.results_df = pd.DataFrame()  # Initialize empty DataFrame
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"parameter_sweeps/sweep_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🔬 Parameter Sweeper initialized")
        print(f"📁 Output directory: {self.output_dir}")
    
    def _get_default_config(self):
        """Get default configuration for simulations"""
        return {
            'population': 1000,
            'network_type': 'hybrid',
            'disease_variant': 'omicron',
            'simulation_days': 120,
            'n_seed_infections': 10,
            'seed_method': 'random',
            'intervention_scenario': 'no_intervention'
        }
    
    def define_parameter_grid(self, exploration_type='basic'):
        """
        Define parameter grids for different types of exploration
        """
        parameter_grids = {
            'basic': {
                'n_seed_infections': [5, 10]
            },
            
            'test': {
                'n_seed_infections': [5]
            }
        }
        
        return parameter_grids.get(exploration_type, parameter_grids['basic'])
    
    def run_single_simulation(self, params, simulation_id=0, save_output=False):
        """
        Run a single simulation with given parameters
        """
        try:
            import time
            start_time = time.time()
            
            # Extract parameters with defaults
            population = params.get('population', self.base_config['population'])
            network_type = params.get('network_type', self.base_config['network_type'])
            disease_variant = params.get('disease_variant', self.base_config['disease_variant'])
            simulation_days = params.get('simulation_days', self.base_config['simulation_days'])
            n_seed_infections = params.get('n_seed_infections', self.base_config['n_seed_infections'])
            
            print(f"🚀 Running simulation {simulation_id}:")
            print(f"   Population: {population}, Disease: {disease_variant}")
            print(f"   Seed infections: {n_seed_infections}")
            
            # 1. GENERATE NETWORK
            generator = UltimateNetworkGenerator(population=population)
            G = generator.hybrid_multilayer()
            
            # 2. CONFIGURE DISEASE
            disease = DiseaseLibrary.covid19_variant(disease_variant)
            
            # 3. RUN SIMULATION
            simulator = UltimateSimulator(G, disease)
            simulator.seed_infections(n_seed_infections)
            
            # Run the simulation - this returns history
            history = simulator.run(days=simulation_days, show_progress=False)
            
            # 4. EXTRACT RESULTS FROM HISTORY - ONLY USE HISTORY, NOT SIMULATOR ATTRIBUTES
            if not history or not isinstance(history, dict):
                raise ValueError("Simulation did not return valid history")
            
            # Extract final values from history
            final_susceptible = history['S'][-1] if 'S' in history and history['S'] else 0
            final_infectious = history['I'][-1] if 'I' in history and history['I'] else 0
            final_recovered = history['R'][-1] if 'R' in history and history['R'] else 0
            final_deaths = history['D'][-1] if 'D' in history and history['D'] else 0
            
            # Calculate derived statistics
            total_infected = population - final_susceptible - final_deaths
            attack_rate = total_infected / population if population > 0 else 0
            case_fatality_rate = final_deaths / total_infected if total_infected > 0 else 0
            
            # Get peak infections
            peak_infections = max(history['I']) if 'I' in history and history['I'] else 0
            
            # Create stats dictionary
            stats = {
                'final_susceptible': final_susceptible,
                'final_infectious': final_infectious,
                'final_recovered': final_recovered,
                'final_deaths': final_deaths,
                'total_infected': total_infected,
                'total_deaths': final_deaths,
                'attack_rate': attack_rate,
                'case_fatality_rate': case_fatality_rate,
                'peak_infections': peak_infections
            }
            
            # Calculate additional metrics from history
            additional_metrics = {}
            if 'I' in history and history['I']:
                # Time to peak
                if peak_infections > 0:
                    peak_day = history['I'].index(peak_infections)
                    additional_metrics['days_to_peak'] = peak_day
                
                # Growth rate (last 7 days)
                if len(history['I']) > 7:
                    recent = history['I'][-7:]
                    if recent[0] > 0:
                        growth_rate = (recent[-1] - recent[0]) / recent[0]
                        additional_metrics['growth_rate_7day'] = growth_rate
            
            # Combine all results
            result = {
                'simulation_id': simulation_id,
                'parameters': params,
                'stats': stats,
                'network_metrics': {'num_nodes': population},
                'additional_metrics': additional_metrics,
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Simulation {simulation_id} completed in {result['execution_time']:.1f}s")
            print(f"   Results: S={final_susceptible}, I={final_infectious}, R={final_recovered}, D={final_deaths}")
            print(f"   Attack rate: {attack_rate:.2%}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in simulation {simulation_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'simulation_id': simulation_id,
                'parameters': params,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_parameter_sweep(self, parameter_grid, n_parallel=1, save_all_outputs=False):
        """
        Run batch of simulations across parameter grid
        """
        # Generate all parameter combinations
        if isinstance(parameter_grid, dict):
            param_names = list(parameter_grid.keys())
            param_values = list(parameter_grid.values())
            
            combinations = list(itertools.product(*param_values))
            param_combinations = []
            for combo in combinations:
                param_dict = {}
                for i, name in enumerate(param_names):
                    param_dict[name] = combo[i]
                param_combinations.append(param_dict)
        else:
            param_combinations = parameter_grid
        
        print(f"📊 Starting parameter sweep with {len(param_combinations)} simulations")
        
        # Run simulations
        results = []
        for i, params in enumerate(param_combinations):
            result = self.run_single_simulation(params, i, save_output=False)
            results.append(result)
        
        # Process results
        self.results = results
        self._process_results()
        
        return results
    
    def _process_results(self):
        """Process and analyze results"""
        if not self.results:
            print("⚠️  No results to process")
            return
        
        print(f"📈 Processing {len(self.results)} simulation results...")
        
        # Convert to DataFrame
        rows = []
        successful_count = 0
        
        for result in self.results:
            if 'error' in result:
                continue
            
            row = {}
            
            # Add parameters
            for key, value in result['parameters'].items():
                row[f'param_{key}'] = value
            
            # Add statistics
            if 'stats' in result:
                for key, value in result['stats'].items():
                    row[f'stat_{key}'] = value
            
            # Add additional metrics
            for key, value in result.get('additional_metrics', {}).items():
                row[f'metric_{key}'] = value
            
            # Add execution info
            row['simulation_id'] = result['simulation_id']
            row['execution_time'] = result.get('execution_time', 0)
            
            rows.append(row)
            successful_count += 1
        
        if rows:
            df = pd.DataFrame(rows)
            self.results_df = df
            print(f"📊 Created DataFrame with {successful_count} successful simulations")
            
            # Save results
            csv_path = f"{self.output_dir}/results.csv"
            df.to_csv(csv_path, index=False)
            print(f"💾 Results saved to {csv_path}")
        else:
            print("⚠️  No successful simulations to process")
            self.results_df = pd.DataFrame()
    
    def find_optimal_interventions(self, objective='minimize_deaths'):
        """
        Find optimal intervention strategies
        """
        print(f"🎯 Finding optimal interventions (objective: {objective})...")
        
        # Check if we have results
        if self.results_df.empty:
            print("⚠️  No simulation results available")
            successful = len([r for r in self.results if 'error' not in r])
            print(f"   Total simulations: {len(self.results)}, Successful: {successful}")
            return None
        
        print(f"   Available results: {len(self.results_df)} simulations")
        
        # Define objective column
        objective_col = None
        if objective == 'minimize_deaths' and 'stat_total_deaths' in self.results_df.columns:
            objective_col = 'stat_total_deaths'
        elif objective == 'minimize_cases' and 'stat_total_infected' in self.results_df.columns:
            objective_col = 'stat_total_infected'
        elif objective == 'minimize_peak' and 'stat_peak_infections' in self.results_df.columns:
            objective_col = 'stat_peak_infections'
        
        if not objective_col:
            print(f"⚠️  Could not find appropriate column for objective: {objective}")
            print(f"   Available stat columns: {[c for c in self.results_df.columns if c.startswith('stat_')]}")
            return None
        
        # Find optimal
        try:
            optimal_idx = self.results_df[objective_col].idxmin()
            optimal_result = self.results_df.loc[optimal_idx]
            
            print(f"✅ Found optimal strategy:")
            print(f"   Simulation ID: {optimal_result['simulation_id']}")
            print(f"   {objective_col}: {optimal_result[objective_col]:.4f}")
            
            # Extract parameters
            optimal_params = {}
            for col in optimal_result.index:
                if col.startswith('param_'):
                    optimal_params[col] = optimal_result[col]
            
            # Save optimal strategy
            optimal_strategy = {
                'objective': objective,
                'objective_value': float(optimal_result[objective_col]),
                'simulation_id': int(optimal_result['simulation_id']),
                'parameters': optimal_params
            }
            
            with open(f"{self.output_dir}/optimal_strategy_{objective}.json", 'w') as f:
                json.dump(optimal_strategy, f, indent=2, default=str)
            
            return optimal_strategy
            
        except Exception as e:
            print(f"❌ Error finding optimal interventions: {str(e)}")
            return None
    
    def generate_report(self):
        """Generate comprehensive report of parameter sweep"""
        print("📋 Generating parameter sweep report...")
        
        successful = len([r for r in self.results if 'error' not in r])
        failed = len([r for r in self.results if 'error' in r])
        
        report_content = f"""
        # Parameter Sweep Analysis Report
        
        ## Overview
        - **Total simulations**: {len(self.results)}
        - **Successful**: {successful}
        - **Failed**: {failed}
        - **Output directory**: {self.output_dir}
        
        ## Results Summary
        """
        
        if not self.results_df.empty:
            report_content += f"""
        - **Successful simulations analyzed**: {len(self.results_df)}
        
        ### Key Statistics
        """
            
            if 'stat_attack_rate' in self.results_df.columns:
                ar_mean = self.results_df['stat_attack_rate'].mean()
                ar_min = self.results_df['stat_attack_rate'].min()
                ar_max = self.results_df['stat_attack_rate'].max()
                report_content += f"""
        **Attack Rate**:
        - Mean: {ar_mean:.2%}
        - Range: {ar_min:.2%} to {ar_max:.2%}
        """
            
            if 'stat_total_deaths' in self.results_df.columns:
                td_mean = self.results_df['stat_total_deaths'].mean()
                td_min = self.results_df['stat_total_deaths'].min()
                td_max = self.results_df['stat_total_deaths'].max()
                report_content += f"""
        **Total Deaths**:
        - Mean: {td_mean:.0f}
        - Range: {td_min:.0f} to {td_max:.0f}
        """
        else:
            report_content += "\n⚠️ No successful simulations to report statistics."
        
        report_content += f"""
        
        ## Files Generated
        
        ### Data Files
        1. `results.csv` - Complete simulation results
        
        ### Optimization
        1. `optimal_strategy_*.json` - Optimal intervention strategies
        
        ---
        
        *Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """
        
        # Write report
        report_path = f"{self.output_dir}/REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"📋 Report saved to {report_path}")
        
        return report_content

def run_simple_test():
    """
    Simple test function to run a few simulations
    """
    print("=" * 60)
    print("🧪 SIMPLE PARAMETER SWEEP TEST")
    print("=" * 60)
    
    # Create sweeper
    sweeper = ParameterSweeper()
    
    # Define very simple parameter grid
    param_grid = {
        'n_seed_infections': [5, 10]
    }
    
    print(f"📊 Parameter grid: {param_grid}")
    
    # Run sweep
    print(f"\n⚡ Running parameter sweep...")
    results = sweeper.run_parameter_sweep(param_grid, n_parallel=1)
    
    # Generate report
    print(f"\n📋 Generating report...")
    sweeper.generate_report()
    
    # Find optimal interventions
    if not sweeper.results_df.empty:
        print(f"\n🎯 Finding optimal interventions...")
        optimal = sweeper.find_optimal_interventions(objective='minimize_deaths')
    else:
        print(f"\n⚠️  No successful simulations to analyze")
    
    print(f"\n✅ Test complete!")
    print(f"📁 Results saved to: {sweeper.output_dir}")
    
    return sweeper

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Run simple test
    print("Starting parameter sweeper test...")
    sweeper = run_simple_test()
    
    print("\n✅ Parameter sweeper test complete!")
    print(f"📁 Check results in: {sweeper.output_dir}")