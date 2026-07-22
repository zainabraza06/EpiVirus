// components/charts/chartTokens.js
//
// Shared visual tokens. These live outside the chart components so that both
// the charts and the 3D network view colour a compartment identically, and so
// the chart module exports components only.

// Chart surface, matched to the card background the charts sit on.
export const SURFACE = '#1f2937'
export const GRID = '#374151'
export const TEXT_SECONDARY = '#9ca3af'

// Categorical palette for the SEIRD compartments, validated as a set against
// the dark surface: every hue sits in the L 0.48-0.67 lightness band, clears
// the 0.10 chroma floor and 3:1 contrast, and the worst adjacent pair
// separates by dE 8.4 under colour-vision deficiency and 19.2 under normal
// vision. Re-validate the whole set if any one value changes.
export const STATE_COLORS = {
    S: '#199e70', // Susceptible - green
    E: '#c98500', // Exposed - amber
    I: '#e0446f', // Infectious - crimson
    R: '#3987e5', // Recovered - blue
    D: '#a8632b', // Deceased - umber
    V: '#9085e9', // Vaccinated - violet
}

export const STATE_LABELS = {
    S: 'Susceptible',
    E: 'Exposed',
    I: 'Infectious',
    R: 'Recovered',
    D: 'Deceased',
    V: 'Vaccinated',
}

export const STATE_ORDER = ['S', 'E', 'I', 'R', 'D', 'V']

// Severity is an ordered magnitude, so it gets a single-hue sequential ramp
// rather than five unrelated categorical hues.
export const SEVERITY_RAMP = {
    asymptomatic: '#f7bfcd',
    mild: '#ee8ba7',
    severe: '#e0446f',
    hospitalized: '#a92a51',
    critical: '#6f1a35',
}

// Single-series charts need no legend, so they all share one accent.
export const ACCENT = '#3987e5'
export const THRESHOLD = '#e0446f'
