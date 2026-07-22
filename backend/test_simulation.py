#!/usr/bin/env python3
"""Regression tests for the EpiVirus simulation engine.

Run with:  python test_simulation.py
"""
import logging
import random
import sys

import numpy as np

from api_server import (CustomDiseaseParams, NetworkConfig, SimulationConfig,
                        active_simulations, build_detailed_data,
                        build_intervention_schedule, build_network_snapshot,
                        get_disease_params, run_simulation)
from disease_models import DiseaseLibrary, DiseaseProgression
from network_generator import UltimateNetworkGenerator
from simulator_engine import UltimateSimulator

logging.disable(logging.CRITICAL)

FAILURES = []


def check(condition, message):
    if condition:
        print(f"  PASS  {message}")
    else:
        print(f"  FAIL  {message}")
        FAILURES.append(message)


def build_simulator(population=300, days=60, variant="delta", scenario=None):
    generator = UltimateNetworkGenerator(population=population)
    G = generator.hybrid_multilayer()
    simulator = UltimateSimulator(G, DiseaseLibrary.covid19_variant(variant))
    simulator.seed_infections(8, method="random")
    if scenario:
        simulator.scheduled_interventions = scenario
    for _ in range(days):
        simulator.step(1)
    return simulator


def test_population_is_conserved():
    print("\nPopulation conservation")
    sim = build_simulator()
    h = sim.history
    totals = {
        h["S"][i] + h["E"][i] + h["I"][i] + h["R"][i] + h["D"][i] + h["V"][i]
        for i in range(len(h["time"]))
    }
    check(totals == {len(sim.G)},
          f"every compartment total equals the population ({totals})")

    # A node must belong to exactly one compartment
    seen = set()
    overlaps = 0
    for state_set in sim.state_sets.values():
        overlaps += len(seen & state_set)
        seen |= state_set
    check(overlaps == 0, "no node appears in two compartments at once")
    check(seen == set(sim.G.nodes()), "every node belongs to some compartment")


def test_series_are_day_aligned():
    print("\nTime series alignment")
    sim = build_simulator(days=80)
    n_days = len(sim.history["time"])

    check(len(sim.stats["r_effective"]) == n_days,
          "R-effective has one value per simulated day")
    check(len(sim.stats["hospital_bed_usage"]) == n_days,
          "hospital bed usage has one value per simulated day")
    for key in ("S", "E", "I", "R", "D", "V", "new_infections",
                "daily_deaths", "daily_hospitalizations"):
        check(len(sim.history[key]) == n_days, f"history['{key}'] has one value per day")


def test_case_counts_are_never_negative():
    print("\nCase counting")
    sim = build_simulator()
    check(min(sim.history["new_infections"]) >= 0,
          "daily new infections are never negative")
    check(min(sim.history["daily_deaths"]) >= 0,
          "daily deaths are never negative")
    check(sum(sim.history["daily_deaths"]) == sim.stats["total_deaths"],
          "daily deaths sum to the reported total")
    check(sum(sim.history["new_infections"]) == sim.stats["total_infected"],
          "daily new infections sum to the reported total")


def test_event_queue_drains():
    print("\nEvent queue")
    sim = build_simulator(days=200)
    overdue = [t for t, _, _ in sim.event_queue if t < sim.time]
    check(not overdue, "no event is left stranded in the past")
    check(len(sim.state_sets["E"]) + len(sim.state_sets["I"]) == 0 or sim.event_queue,
          "any remaining active case still has a pending event")


def test_dead_stay_dead():
    print("\nTerminal states")
    sim = build_simulator(days=120)
    check(all(sim.G.nodes[n]["state"] == "D" for n in sim.state_sets["D"]),
          "every node in the deceased set has state 'D'")
    check(all(sim.history["D"][i] <= sim.history["D"][i + 1]
              for i in range(len(sim.history["D"]) - 1)),
          "the deceased count never decreases")


def test_node_states_stay_in_the_documented_set():
    print("\nNode state vocabulary")
    sim = build_simulator()
    states = {sim.G.nodes[n]["state"] for n in sim.G.nodes()}
    check(states <= {"S", "E", "I", "R", "D", "V"},
          f"node states stay within S/E/I/R/D/V (saw {sorted(states)})")


def test_lockdown_is_reversible():
    print("\nReversible interventions")
    generator = UltimateNetworkGenerator(population=200)
    G = generator.hybrid_multilayer()
    sim = UltimateSimulator(G, DiseaseLibrary.covid19_variant("delta"))
    sim.seed_infections(5)

    before = {n: sim.G.nodes[n]["mobility"] for n in sim.G.nodes()}
    sim.apply_intervention("lockdown", strictness=0.8, compliance=1.0, duration=10)
    during = {n: sim.G.nodes[n]["mobility"] for n in sim.G.nodes()}
    check(all(during[n] < before[n] for n in before if before[n] > 0),
          "lockdown reduces mobility while it is active")

    for _ in range(15):
        sim.step(1)
    after = {n: sim.G.nodes[n]["mobility"] for n in sim.G.nodes()}
    check(all(abs(after[n] - before[n]) < 1e-9 for n in before),
          "mobility is restored exactly when the lockdown ends")
    check("lockdown" not in sim.interventions, "the lockdown flag is cleared")


def test_lockdown_does_not_silence_the_whole_population():
    print("\nLockdown scope")
    generator = UltimateNetworkGenerator(population=200)
    G = generator.hybrid_multilayer()
    sim = UltimateSimulator(G, DiseaseLibrary.covid19_variant("delta"))
    sim.seed_infections(5)
    sim.apply_intervention("lockdown", strictness=0.9, compliance=1.0)
    isolated = sum(1 for n in sim.G.nodes() if sim.G.nodes[n].get("isolated"))
    check(isolated == 0,
          "lockdown does not mark the entire population as isolated")


def test_vaccination_is_a_daily_campaign():
    print("\nVaccination campaign")
    schedule = [{"day": 0, "type": "vaccination",
                 "params": {"rate": 0.05, "efficacy": 0.9, "priority": "random"}}]
    sim = build_simulator(population=400, days=30, scenario=schedule)
    v_series = sim.history["V"]
    check(v_series[-1] > v_series[0], "vaccinated count grows over the campaign")
    check(sum(1 for i in range(1, 20) if v_series[i] > v_series[i - 1]) > 5,
          "doses are administered on many days, not in one batch")


def test_custom_disease_parameters_change_outcomes():
    print("\nCustom disease parameters")
    lethal = get_disease_params(type("C", (), {
        "variant": "wildtype", "custom_params": None,
        "custom_r0": None, "custom_mortality": 0.9, "custom_incubation_mean": None,
    })())
    mild = get_disease_params(type("C", (), {
        "variant": "wildtype", "custom_params": None,
        "custom_r0": None, "custom_mortality": 0.0, "custom_incubation_mean": None,
    })())

    random.seed(7)
    np.random.seed(7)
    lethal_deaths = sum(
        DiseaseProgression.determine_initial_course(70, lethal)["will_die"]
        for _ in range(400)
    )
    mild_deaths = sum(
        DiseaseProgression.determine_initial_course(70, mild)["will_die"]
        for _ in range(400)
    )
    check(lethal_deaths > mild_deaths,
          f"a higher mortality rate produces more deaths ({lethal_deaths} vs {mild_deaths})")
    check(mild_deaths == 0, "a zero mortality rate produces no deaths")


def test_severity_probabilities_are_normalised():
    print("\nDisease parameter validation")
    for variant in ("wildtype", "alpha", "delta", "omicron"):
        d = DiseaseLibrary.covid19_variant(variant)
        total = d.p_asymptomatic + d.p_mild + d.p_severe + d.p_critical
        check(abs(total - 1.0) < 1e-9, f"{variant} severity probabilities sum to 1")

    from disease_models import DiseaseParameters
    weird = DiseaseParameters(p_asymptomatic=5, p_mild=5, p_severe=0, p_critical=0, R0=99)
    total = weird.p_asymptomatic + weird.p_mild + weird.p_severe + weird.p_critical
    check(abs(total - 1.0) < 1e-9, "out-of-range severity inputs are normalised, not rejected")
    check(weird.R0 == 20, "an out-of-range R0 is clamped rather than raising")


def test_custom_interventions_reach_the_schedule():
    print("\nIntervention schedule")
    config = SimulationConfig(
        intervention_scenario="no_intervention",
        custom_interventions=[{"day": 5, "type": "mask_mandate",
                               "params": {"efficacy": 0.8, "compliance": 0.9}}],
    )
    schedule = build_intervention_schedule(config)
    check(any(e["type"] == "mask_mandate" and e["day"] == 5 for e in schedule),
          "a custom intervention reaches the simulator schedule")

    config = SimulationConfig(intervention_scenario="rapid_response", compliance_rate=0.33)
    schedule = build_intervention_schedule(config)
    compliances = [e["params"]["compliance"] for e in schedule if "compliance" in e["params"]]
    check(compliances and all(abs(c - 0.33) < 1e-9 for c in compliances),
          "the compliance slider is applied to every preset intervention")


def test_network_snapshot_tracks_real_nodes():
    print("\n3D network snapshot")
    sim = build_simulator(population=300, days=40)
    snapshot = build_network_snapshot(sim)

    check(len(snapshot["nodes"]) > 0, "the snapshot contains nodes")
    check(all(len(f) == len(snapshot["nodes"]) for f in snapshot["frames"]),
          "every frame has one state per node")
    check(all(0 <= a < len(snapshot["nodes"]) and 0 <= b < len(snapshot["nodes"])
              for a, b in snapshot["edges"]),
          "every edge references a node index that exists")

    # A given node must follow a legal trajectory, never bouncing back to S
    regressions = 0
    for node_index in range(len(snapshot["nodes"])):
        trajectory = [f[node_index] for f in snapshot["frames"]]
        for previous, current in zip(trajectory, trajectory[1:]):
            if previous in ("R", "D") and current == "S":
                regressions += 1
    check(regressions == 0,
          "no node ever returns to susceptible after recovering or dying")


def test_full_api_pipeline():
    print("\nEnd-to-end API pipeline")
    config = SimulationConfig(
        network={"population": 250, "network_type": "barabasi_albert", "barabasi_m": 2},
        disease={"variant": "omicron", "custom_params": {"r0": 6.0, "mortality_rate": 0.05}},
        n_seed_infections=5,
        simulation_days=45,
        intervention_scenario="rapid_response",
        vaccination_rate=0.02,
    )
    active_simulations["test"] = {
        "status": "initializing", "current_day": 0, "total_days": 45,
        "progress": 0, "config": config.model_dump(),
    }
    run_simulation("test", config)
    sim = active_simulations["test"]

    check(sim["status"] == "completed", f"simulation completes ({sim.get('error')})")
    if sim["status"] != "completed":
        return

    detailed = sim["detailed_data"]
    n_days = len(sim["history"]["time"])
    check(n_days == 45, "the history covers every requested day")
    check(len(detailed["r_effective"]) == n_days, "R-effective is day-aligned in the payload")
    check(len(detailed["daily_new_cases"]) == n_days, "daily new cases are day-aligned")
    check(min(detailed["daily_new_cases"]) >= 0, "daily new cases are never negative")
    check(sum(detailed["age_distribution"]["counts"]) == sim["summary"]["total_infected"],
          "the age histogram accounts for every infected individual")
    check(len(detailed["severity_breakdown"]["critical"]) == n_days,
          "the severity breakdown covers every day")
    check("network_snapshot" in sim, "a 3D network snapshot is produced")


def test_every_frontend_control_reaches_the_backend():
    """No control in the UI may be decorative.

    Each of these was a real defect: sliders that changed nothing because the
    field name never reached a request model or an engine handler.
    """
    print("\nFrontend/backend contract")
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    fe = root / "frontend" / "src" / "components" / "config"
    if not fe.exists():
        print("  SKIP  frontend sources not present")
        return

    config_jsx = (fe / "SimulationConfig.jsx").read_text(encoding="utf-8")
    disease_jsx = (fe / "CustomDiseaseBuilder.jsx").read_text(encoding="utf-8")
    network_jsx = (fe / "AdvancedNetworkConfig.jsx").read_text(encoding="utf-8")
    interventions_jsx = (fe / "AdvancedInterventionBuilder.jsx").read_text(encoding="utf-8")

    # 1. Every disease-builder slider is mapped onto a request field
    sliders = set(re.findall(r"handleChange\('(\w+)'", disease_jsx))
    mapper = config_jsx[config_jsx.index("function toCustomDiseaseParams"):
                        config_jsx.index("export default function")]
    mapped = set(re.findall(r"builderParams\.(\w+)", mapper))
    check(sliders <= mapped,
          f"every custom-disease slider is sent to the API (orphaned: {sorted(sliders - mapped)})")

    # 2. Every field the mapper produces is accepted by CustomDiseaseParams
    produced = set(re.findall(r"^\s+(\w+): builderParams", mapper, re.M))
    accepted = set(CustomDiseaseParams.model_fields)
    check(produced <= accepted,
          f"every mapped disease field is a real request field (unknown: {sorted(produced - accepted)})")

    # 3. Every advanced-network control is a real NetworkConfig field
    network_controls = set(re.findall(r"key: '(\w+)'", network_jsx))
    check(network_controls <= set(NetworkConfig.model_fields),
          "every advanced-network control is a NetworkConfig field "
          f"(unknown: {sorted(network_controls - set(NetworkConfig.model_fields))})")

    # 4. Every intervention the UI offers has an engine handler, and every
    #    parameter it sends is a real keyword argument of that handler
    import inspect
    from simulator_engine import UltimateSimulator

    types_block = interventions_jsx[interventions_jsx.index("const interventionTypes"):
                                    interventions_jsx.index("const addIntervention")]
    ui_types = set(re.findall(r"^\s+(\w+): \{ label", types_block, re.M))

    simulator = UltimateSimulator.__new__(UltimateSimulator)
    handler_names = dict(re.findall(r"'(\w+)': self\.(_apply_\w+),",
                                    inspect.getsource(UltimateSimulator.apply_intervention)))
    check(ui_types <= set(handler_names),
          f"every UI intervention has a handler (missing: {sorted(ui_types - set(handler_names))})")

    defaults_block = interventions_jsx[interventions_jsx.index("function getDefaultParams"):]
    for ui_type in sorted(ui_types):
        match = re.search(rf"{ui_type}: \{{([^}}]*)\}}", defaults_block)
        if not match or ui_type not in handler_names:
            continue
        sent = set(re.findall(r"(\w+):", match.group(1)))
        accepted_args = set(
            inspect.signature(getattr(UltimateSimulator, handler_names[ui_type])).parameters
        ) - {"self"}
        check(sent <= accepted_args,
              f"{ui_type} sends only parameters its handler accepts "
              f"(unknown: {sorted(sent - accepted_args)})")

    # 5. Every vaccination priority the UI offers changes the dose order
    priorities = set(re.findall(r'<option value="(\w+)">', interventions_jsx))
    vaccination_source = inspect.getsource(UltimateSimulator._vaccinate_daily)
    known = set(re.findall(r"'(\w+)'", vaccination_source))
    unhandled = {p for p in priorities if p not in known and p != "random"}
    check(not unhandled,
          f"every vaccination priority is handled by the engine (unhandled: {sorted(unhandled)})")


def test_transmission_scale_changes_transmission():
    print("\nTransmission scale")
    from disease_models import DiseaseParameters, TransmissionCalculator

    generator = UltimateNetworkGenerator(population=120)
    G = generator.erdos_renyi(p=0.05)
    u, v = list(G.edges())[0]

    probabilities = []
    for scale in (0.02, 0.2):
        disease = DiseaseParameters(transmission_scale=scale)
        probabilities.append(
            TransmissionCalculator.calculate_transmission_probability(
                infector=u, susceptible=v, G=G, disease=disease, interventions={}, current_day=0
            )
        )

    check(probabilities[1] > probabilities[0],
          f"a higher transmission scale raises the per-contact probability "
          f"({probabilities[0]:.4f} -> {probabilities[1]:.4f})")


def main():
    tests = [
        test_population_is_conserved,
        test_series_are_day_aligned,
        test_case_counts_are_never_negative,
        test_event_queue_drains,
        test_dead_stay_dead,
        test_node_states_stay_in_the_documented_set,
        test_lockdown_is_reversible,
        test_lockdown_does_not_silence_the_whole_population,
        test_vaccination_is_a_daily_campaign,
        test_custom_disease_parameters_change_outcomes,
        test_severity_probabilities_are_normalised,
        test_custom_interventions_reach_the_schedule,
        test_network_snapshot_tracks_real_nodes,
        test_transmission_scale_changes_transmission,
        test_every_frontend_control_reaches_the_backend,
        test_full_api_pipeline,
    ]

    random.seed(42)
    np.random.seed(42)

    print("EpiVirus simulation regression tests")
    for test in tests:
        test()

    print("\n" + "=" * 60)
    if FAILURES:
        print(f"{len(FAILURES)} check(s) FAILED:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
