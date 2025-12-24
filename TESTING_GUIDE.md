# Testing Guide - EpiVirus Epidemic Simulation Fixes

## Quick Start

### 1. Backend Test (Python)
```bash
cd EpiVirus
python test_fixes.py
```

**Expected Output:**
- ✅ 'daily_deaths' key found in history
- ✅ 'daily_hospitalizations' key found in history  
- Deaths should be > 0 (not all zeros)
- CFR (Case Fatality Rate) between 1-5%
- Hospitalization Rate between 4-10%

### 2. Start API Server
```bash
cd src
python api_server.py
# Server runs on http://localhost:8000
```

**Test endpoints:**
```bash
# Get available diseases
curl http://localhost:8000/api/diseases

# Create a simulation
curl -X POST http://localhost:8000/api/simulation \
  -H "Content-Type: application/json" \
  -d '{
    "network": {"population": 500, "network_type": "hybrid"},
    "disease": {"variant": "omicron"},
    "n_seed_infections": 10,
    "simulation_days": 60
  }'

# Check simulation results (replace sim_id with actual ID)
curl http://localhost:8000/api/simulation/{sim_id}/results
```

### 3. Frontend Test (React)
```bash
cd client
npm install
npm run dev
```

**Then:**
1. Open http://localhost:5173 in browser
2. Configure simulation (or use defaults)
3. Click "Run Simulation"
4. Scroll down to see:
   - ✅ Disease Dynamics chart (S, I, R, D)
   - ✅ Epidemic Curve (new daily cases)
   - ✅ **Daily Deaths Chart** (NEW - red bars)
   - ✅ **Daily Hospitalizations Chart** (NEW - purple bars)
   - Both charts show 7-day moving average

## What Was Fixed

### Death Tracking
| Issue | Before | After |
|-------|--------|-------|
| Daily deaths displayed | Always 0 | Actual values |
| Death probability | 0.01x-10x multipliers | 0.05x-8x (realistic) |
| Age-based mortality | Unrealistic | COVID-19 IFR data |
| Hospitalization rates | 15% overall, 5% ICU | 25% overall, 8% ICU |

### Disease Parameters Updated
- **Mortality rates**: Increased 15-50x for elderly (70+)
- **Hospitalization rates**: Increased for severe/critical cases
- **Age stratification**: Now matches real COVID-19 data

### API Response
API now includes in `/api/simulation/{id}/results`:
```json
{
  "detailed_data": {
    "daily_deaths": [0, 0, 1, 2, 1, 0, ...],
    "daily_hospitalizations": [0, 1, 3, 5, 4, 2, ...],
    "daily_new_cases": [10, 15, 20, 25, ...],
    "severity_breakdown": {...}
  }
}
```

### Frontend Visualization
Two new charts added to the Results view:
1. **Daily Deaths Chart**
   - Red bar chart with 7-day moving average
   - Shows deaths per day
   
2. **Daily Hospitalizations Chart**
   - Purple bar chart with 7-day moving average
   - Shows current hospitalized patients

## Validation Checklist

After running a full simulation, verify:

- [ ] **Deaths > 0**: Check that total_deaths is not zero
- [ ] **Daily deaths vary**: Days should show 0-N deaths (not constant)
- [ ] **Peak death lag**: Deaths should peak 1-2 weeks after infections peak
- [ ] **Age correlation**: Older age groups show higher death rates in progression debug output
- [ ] **CFR reasonable**: Case Fatality Rate should be 1-3% (realistic COVID)
- [ ] **Hospitalization rate**: 4-10% of infected (realistic COVID)
- [ ] **Frontend displays**: Both new charts visible and populated with data
- [ ] **7-day average smooth**: Moving average line should smooth out day-to-day noise
- [ ] **No negative values**: All daily death/hosp values should be >= 0

## Expected Metrics

### Realistic COVID-19 Epidemic (60 days, 1000 population, Omicron)
- **Attack rate**: 30-50% (60-100% infected after 120 days)
- **CFR**: 1-2% overall
- **CFR by age**: 0.001% (ages 0-9) → 45% (80+)
- **Hospitalization**: 4-8% of infected
- **Peak death**: Usually 1-3 weeks after peak infections
- **Peak hospitalized**: Usually concurrent with peak infections

### If You See Different Results
- **Deaths always 0**: Check if `daily_deaths` array is being recorded
- **CFR too high (>10%)**: Mortality multipliers might be wrong
- **CFR too low (<0.1%)**: Check age stratification params
- **No deaths in elderly**: Check if age-based mortality is applied

## Files to Check

### Backend
- `src/disease_models.py` - Disease parameters
- `src/simulator_engine.py` - Death tracking logic
- `src/api_server.py` - API response generation

### Frontend
- `client/src/components/ComprehensiveCharts.jsx` - Chart components
- `client/src/App.jsx` - Integration into main view

### Test
- `test_fixes.py` - Standalone test script

## Troubleshooting

### Deaths still showing 0
1. Check `_record_history()` is calculating daily_deaths
2. Verify `daily_deaths_count` is incremented in `_execute_event('die')`
3. Ensure API is returning `daily_deaths` in response

### Charts not showing
1. Verify `DailyDeathsChart` and `HospitalizationChart` are imported in App.jsx
2. Check that `simulationResults.detailed_data.daily_deaths` exists
3. Open browser console (F12) for JavaScript errors

### Unrealistic rates
1. Check `age_stratification` parameters in `disease_models.py`
2. Verify mortality multipliers in `determine_initial_course()`
3. Run `test_fixes.py` to check if issue is backend or frontend

---

**Last Updated**: December 24, 2025  
**Version**: 2.0  
**Status**: ✅ Fully Implemented & Tested
