#!/usr/bin/env python3
"""
Quick test to verify death tracking and hospitalization fixes are working
"""

import sys
sys.path.append('./src')

from network_generator import UltimateNetworkGenerator
from disease_models import DiseaseLibrary
from simulator_engine import UltimateSimulator

def test_death_tracking():
    """Test that daily deaths are being tracked"""
    print("=" * 60)
    print("🧪 TESTING DEATH TRACKING & HOSPITALIZATION FIXES")
    print("=" * 60)
    
    # 1. Create network
    print("\n1️⃣  Creating network with 500 nodes...")
    generator = UltimateNetworkGenerator(population=500)
    G = generator.hybrid_multilayer()
    print(f"   ✅ Network created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 2. Create disease with updated parameters
    print("\n2️⃣  Loading COVID-19 Omicron with new parameters...")
    disease = DiseaseLibrary.covid19_variant('omicron')
    print(f"   R0: {disease.R0}")
    print(f"   Mortality rate: {disease.mortality_rate * 100:.1f}%")
    print(f"   Hospitalization rate: {disease.hospitalization_rate * 100:.1f}%")
    print(f"   ✅ Disease parameters loaded")
    
    # 3. Initialize simulator
    print("\n3️⃣  Initializing simulator...")
    simulator = UltimateSimulator(G, disease)
    print(f"   ✅ Simulator initialized")
    
    # 4. Seed infections
    print("\n4️⃣  Seeding 10 infections...")
    simulator.seed_infections(n_infections=10, method='random')
    print(f"   ✅ Infections seeded")
    
    # 5. Run simulation for 30 days
    print("\n5️⃣  Running simulation for 30 days...")
    history = simulator.run(days=30, show_progress=True)
    
    # 6. Check results
    print("\n6️⃣  RESULTS VERIFICATION")
    print("   " + "=" * 56)
    
    # Check if daily_deaths is in history
    if 'daily_deaths' in history:
        print(f"   ✅ 'daily_deaths' key found in history")
        daily_deaths = history['daily_deaths']
        total_deaths_recorded = sum(daily_deaths)
        print(f"      Total daily deaths recorded: {total_deaths_recorded}")
        print(f"      Days with deaths: {sum(1 for d in daily_deaths if d > 0)}")
        print(f"      Max daily deaths: {max(daily_deaths) if daily_deaths else 0}")
        print(f"      Daily deaths sample (first 10 days): {daily_deaths[:10]}")
    else:
        print(f"   ❌ 'daily_deaths' key NOT found in history!")
        print(f"      Available keys: {list(history.keys())}")
    
    # Check if daily_hospitalizations is in history
    if 'daily_hospitalizations' in history:
        print(f"\n   ✅ 'daily_hospitalizations' key found in history")
        daily_hosp = history['daily_hospitalizations']
        print(f"      Max hospitalized: {max(daily_hosp) if daily_hosp else 0}")
        print(f"      Daily hospitalizations sample (first 10 days): {daily_hosp[:10]}")
    else:
        print(f"\n   ❌ 'daily_hospitalizations' key NOT found in history!")
    
    # Check final statistics
    print(f"\n   📊 FINAL STATISTICS")
    print(f"      Total infected: {simulator.stats['total_infected']}")
    print(f"      Total recovered: {simulator.stats['total_recovered']}")
    print(f"      Total deaths: {simulator.stats['total_deaths']}")
    print(f"      Total hospitalized: {simulator.stats['total_hospitalized']}")
    print(f"      Peak infections: {simulator.stats['peak_infections']} (day {simulator.stats['peak_day']})")
    
    # Check case fatality rate
    if simulator.stats['total_infected'] > 0:
        cfr = (simulator.stats['total_deaths'] / simulator.stats['total_infected']) * 100
        print(f"      Case Fatality Rate: {cfr:.2f}%")
    
    # Check hospitalization rate
    if simulator.stats['total_infected'] > 0:
        hosp_rate = (simulator.stats['total_hospitalized'] / simulator.stats['total_infected']) * 100
        print(f"      Hospitalization Rate: {hosp_rate:.2f}%")
    
    print("\n" + "=" * 60)
    if 'daily_deaths' in history and sum(history['daily_deaths']) > 0:
        print("✅ ALL TESTS PASSED - Death tracking is working!")
    else:
        print("❌ TEST FAILED - Daily deaths still not tracked")
    print("=" * 60)

if __name__ == "__main__":
    test_death_tracking()
