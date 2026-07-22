// components/charts/EpidemicCharts.jsx
//
// The complete chart suite. Every concept is plotted exactly once here - the
// previous three chart modules rendered age, degree, mobility and the SEIRD
// curves between three and six times each, in different shapes, from the same
// numbers.
import { useMemo } from 'react'
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    ComposedChart,
    Legend,
    Line,
    LineChart,
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

import {
    ACCENT,
    GRID,
    SEVERITY_RAMP,
    STATE_COLORS,
    STATE_LABELS,
    SURFACE,
    TEXT_SECONDARY,
    THRESHOLD,
} from './chartTokens'

const axisProps = {
    stroke: TEXT_SECONDARY,
    tick: { fill: TEXT_SECONDARY, fontSize: 12 },
    tickLine: false,
}

const tooltipProps = {
    contentStyle: {
        backgroundColor: '#111827',
        border: `1px solid ${GRID}`,
        borderRadius: 8,
        fontSize: 13,
    },
    labelStyle: { color: '#f9fafb', fontWeight: 600 },
    cursor: { stroke: TEXT_SECONDARY, strokeWidth: 1, strokeDasharray: '4 4' },
}

const legendProps = {
    wrapperStyle: { fontSize: 13, paddingTop: 8 },
    iconType: 'plainline',
    iconSize: 14,
}

// ---------------------------------------------------------------------------
// Shared shell
// ---------------------------------------------------------------------------

function ChartCard({ title, subtitle, note, children, height = 320 }) {
    return (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-50">{title}</h3>
            {subtitle && <p className="text-sm text-gray-400 mt-0.5 mb-3">{subtitle}</p>}
            <div style={{ width: '100%', height }} className={subtitle ? '' : 'mt-3'}>
                <ResponsiveContainer width="100%" height="100%">
                    {children}
                </ResponsiveContainer>
            </div>
            {note && <p className="text-xs text-gray-400 mt-3">{note}</p>}
        </div>
    )
}

function EmptyCard({ title, message = 'No data available for this simulation.' }) {
    return (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-50">{title}</h3>
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
                {message}
            </div>
        </div>
    )
}

const movingAverage = (values, window = 7) =>
    values.map((_, i) => {
        const slice = values.slice(Math.max(0, i - window + 1), i + 1)
        return Number((slice.reduce((a, b) => a + b, 0) / slice.length).toFixed(2))
    })

const hasSeries = (series) => Array.isArray(series) && series.length > 0

// ---------------------------------------------------------------------------
// 1. SEIRD compartments over time
// ---------------------------------------------------------------------------

export function SeirdDynamicsChart({ history }) {
    const data = useMemo(() => {
        if (!history?.S) return []
        return history.S.map((_, i) => ({
            day: history.time?.[i] ?? i,
            Susceptible: history.S[i],
            Exposed: history.E?.[i] ?? 0,
            Infectious: history.I[i],
            Recovered: history.R[i],
            Deceased: history.D?.[i] ?? 0,
            Vaccinated: history.V?.[i] ?? 0,
        }))
    }, [history])

    if (!data.length) return <EmptyCard title="SEIRD dynamics" />

    return (
        <ChartCard
            title="SEIRD dynamics"
            subtitle="How many people are in each compartment on each day"
            height={340}
        >
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} />
                {Object.entries(STATE_LABELS).map(([key, label]) => (
                    <Line
                        key={key}
                        type="monotone"
                        dataKey={label}
                        stroke={STATE_COLORS[key]}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, strokeWidth: 2, stroke: SURFACE }}
                    />
                ))}
            </LineChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 2. Population composition
// ---------------------------------------------------------------------------

export function PopulationCompositionChart({ history }) {
    const data = useMemo(() => {
        if (!history?.S) return []
        return history.S.map((_, i) => ({
            day: history.time?.[i] ?? i,
            Susceptible: history.S[i],
            Exposed: history.E?.[i] ?? 0,
            Infectious: history.I[i],
            Recovered: history.R[i],
            Vaccinated: history.V?.[i] ?? 0,
            Deceased: history.D?.[i] ?? 0,
        }))
    }, [history])

    if (!data.length) return <EmptyCard title="Population composition" />

    // Stacking every compartment - the previous version stacked only four of
    // six, so the total silently fell short of the population.
    const order = ['Susceptible', 'Exposed', 'Infectious', 'Recovered', 'Vaccinated', 'Deceased']
    const keyOf = { Susceptible: 'S', Exposed: 'E', Infectious: 'I', Recovered: 'R', Vaccinated: 'V', Deceased: 'D' }

    return (
        <ChartCard
            title="Population composition"
            subtitle="Every compartment stacked - the total is the full population"
            height={340}
        >
            <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} iconType="square" />
                {order.map((label) => (
                    <Area
                        key={label}
                        type="monotone"
                        dataKey={label}
                        stackId="population"
                        fill={STATE_COLORS[keyOf[label]]}
                        fillOpacity={0.85}
                        // A 2px stroke in the surface colour separates
                        // neighbouring bands instead of letting them bleed
                        stroke={SURFACE}
                        strokeWidth={2}
                    />
                ))}
            </AreaChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 3. Epidemic curve
// ---------------------------------------------------------------------------

export function EpidemicCurveChart({ dailyNewCases, time }) {
    const { data, peakDay } = useMemo(() => {
        if (!hasSeries(dailyNewCases)) return { data: [], peakDay: 0 }
        const average = movingAverage(dailyNewCases)
        const peakIndex = dailyNewCases.indexOf(Math.max(...dailyNewCases))
        return {
            data: dailyNewCases.map((cases, i) => ({
                day: time?.[i] ?? i,
                'New cases': cases,
                '7-day average': average[i],
            })),
            peakDay: time?.[peakIndex] ?? peakIndex,
        }
    }, [dailyNewCases, time])

    if (!data.length) return <EmptyCard title="Epidemic curve" />

    return (
        <ChartCard
            title="Epidemic curve"
            subtitle="New infections recorded each day"
            note={`Peak incidence on day ${peakDay}.`}
        >
            <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} />
                <Bar dataKey="New cases" fill={STATE_COLORS.I} fillOpacity={0.55} radius={[4, 4, 0, 0]} />
                <Line
                    type="monotone"
                    dataKey="7-day average"
                    stroke={STATE_COLORS.I}
                    strokeWidth={2}
                    dot={false}
                />
                <ReferenceLine
                    x={peakDay}
                    stroke={TEXT_SECONDARY}
                    strokeDasharray="4 4"
                    label={{ value: `Peak · day ${peakDay}`, fill: TEXT_SECONDARY, fontSize: 11, position: 'top' }}
                />
            </ComposedChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 4. Healthcare burden
// ---------------------------------------------------------------------------

export function HealthcareBurdenChart({ severity, capacity, time }) {
    const data = useMemo(() => {
        if (!severity?.hospitalized) return []
        return severity.hospitalized.map((_, i) => ({
            day: time?.[i] ?? i,
            Asymptomatic: severity.asymptomatic?.[i] ?? 0,
            Mild: severity.mild?.[i] ?? 0,
            Severe: severity.severe?.[i] ?? 0,
            Hospitalised: severity.hospitalized[i],
            Critical: severity.critical?.[i] ?? 0,
        }))
    }, [severity, time])

    if (!data.length) return <EmptyCard title="Healthcare burden" />

    const bands = [
        ['Asymptomatic', SEVERITY_RAMP.asymptomatic],
        ['Mild', SEVERITY_RAMP.mild],
        ['Severe', SEVERITY_RAMP.severe],
        ['Hospitalised', SEVERITY_RAMP.hospitalized],
        ['Critical', SEVERITY_RAMP.critical],
    ]

    return (
        <ChartCard
            title="Healthcare burden"
            subtitle="Active cases by severity, against hospital bed capacity"
            note="Bands run light to dark with increasing severity."
            height={340}
        >
            <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} iconType="square" />
                {bands.map(([label, color]) => (
                    <Area
                        key={label}
                        type="monotone"
                        dataKey={label}
                        stackId="severity"
                        fill={color}
                        fillOpacity={0.9}
                        stroke={SURFACE}
                        strokeWidth={2}
                    />
                ))}
                {capacity > 0 && (
                    <ReferenceLine
                        y={capacity}
                        stroke={THRESHOLD}
                        strokeWidth={2}
                        strokeDasharray="6 4"
                        label={{
                            value: `Bed capacity (${capacity})`,
                            fill: THRESHOLD,
                            fontSize: 11,
                            position: 'insideTopRight',
                        }}
                    />
                )}
            </ComposedChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 5. Daily deaths
// ---------------------------------------------------------------------------

export function DailyDeathsChart({ dailyDeaths, time }) {
    const data = useMemo(() => {
        if (!hasSeries(dailyDeaths)) return []
        const average = movingAverage(dailyDeaths)
        return dailyDeaths.map((deaths, i) => ({
            day: time?.[i] ?? i,
            Deaths: deaths,
            '7-day average': average[i],
        }))
    }, [dailyDeaths, time])

    if (!data.length) return <EmptyCard title="Daily deaths" />

    const total = dailyDeaths.reduce((a, b) => a + b, 0)

    return (
        <ChartCard
            title="Daily deaths"
            subtitle="Deaths recorded each day"
            note={total === 0 ? 'No deaths occurred in this simulation.' : `${total} deaths in total.`}
        >
            <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} allowDecimals={false} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} />
                <Bar dataKey="Deaths" fill={STATE_COLORS.D} fillOpacity={0.6} radius={[4, 4, 0, 0]} />
                <Line
                    type="monotone"
                    dataKey="7-day average"
                    stroke={STATE_COLORS.D}
                    strokeWidth={2}
                    dot={false}
                />
            </ComposedChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 6. Effective reproduction number
// ---------------------------------------------------------------------------

export function REffectiveChart({ rEffective, time }) {
    const data = useMemo(() => {
        if (!hasSeries(rEffective)) return []
        return rEffective.map((value, i) => ({
            day: time?.[i] ?? i,
            'R effective': value,
        }))
    }, [rEffective, time])

    if (!data.length) {
        return (
            <EmptyCard
                title="Effective reproduction number"
                message="R-effective needs at least two generation intervals of history."
            />
        )
    }

    return (
        <ChartCard
            title="Effective reproduction number"
            subtitle="Average secondary infections per case, estimated over one generation interval"
            note="Above the R = 1 line the epidemic is growing; below it, shrinking."
        >
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                {/* A real reference line - the old chart passed `y={1}` to a
                    <Line> series, which Recharts silently ignored. */}
                <ReferenceLine
                    y={1}
                    stroke={THRESHOLD}
                    strokeWidth={2}
                    strokeDasharray="6 4"
                    label={{ value: 'R = 1', fill: THRESHOLD, fontSize: 11, position: 'insideTopRight' }}
                />
                <Line
                    type="monotone"
                    dataKey="R effective"
                    stroke={ACCENT}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 2, stroke: SURFACE }}
                />
            </LineChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 7. Cumulative outcomes
// ---------------------------------------------------------------------------

export function CumulativeOutcomesChart({ history, cumulativeCases }) {
    const data = useMemo(() => {
        if (!history?.S) return []
        return history.S.map((_, i) => ({
            day: history.time?.[i] ?? i,
            'Total infected': cumulativeCases?.[i] ?? 0,
            'Total recovered': history.R[i],
            'Total deaths': history.D?.[i] ?? 0,
        }))
    }, [history, cumulativeCases])

    if (!data.length) return <EmptyCard title="Cumulative outcomes" />

    return (
        <ChartCard
            title="Cumulative outcomes"
            subtitle="Running totals across the whole simulation"
        >
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="day" {...axisProps} />
                <YAxis {...axisProps} width={56} />
                <Tooltip {...tooltipProps} />
                <Legend {...legendProps} />
                <Line type="monotone" dataKey="Total infected" stroke={STATE_COLORS.I} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Total recovered" stroke={STATE_COLORS.R} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Total deaths" stroke={STATE_COLORS.D} strokeWidth={2} dot={false} />
            </LineChart>
        </ChartCard>
    )
}

// ---------------------------------------------------------------------------
// 8-10. Network and demographic distributions (single series each)
// ---------------------------------------------------------------------------

function HistogramCard({ title, subtitle, note, distribution, xLabel, formatBin = (b) => b }) {
    const data = useMemo(() => {
        if (!distribution?.counts) return []
        return distribution.counts.map((count, i) => ({
            bin: formatBin(distribution.bins[i], distribution.bins[i + 1]),
            count,
        }))
    }, [distribution, formatBin])

    if (!data.length) return <EmptyCard title={title} />

    return (
        <ChartCard title={title} subtitle={subtitle} note={note} height={280}>
            <BarChart data={data} margin={{ top: 8, right: 16, bottom: 16, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis
                    dataKey="bin"
                    {...axisProps}
                    label={{ value: xLabel, fill: TEXT_SECONDARY, fontSize: 12, position: 'insideBottom', offset: -10 }}
                />
                <YAxis {...axisProps} width={56} allowDecimals={false} />
                <Tooltip {...tooltipProps} cursor={{ fill: '#ffffff10' }} />
                {/* One series, so no legend - the title names it */}
                <Bar dataKey="count" name="People" fill={ACCENT} radius={[4, 4, 0, 0]} />
            </BarChart>
        </ChartCard>
    )
}

export function AgeDistributionChart({ ageDistribution }) {
    return (
        <HistogramCard
            title="Age distribution of infections"
            subtitle="Everyone who was infected at any point, by age band"
            distribution={ageDistribution}
            xLabel="Age"
            formatBin={(lo, hi) => (hi === undefined ? `${lo}+` : `${lo}-${hi - 1}`)}
        />
    )
}

export function DegreeDistributionChart({ degreeDistribution }) {
    return (
        <HistogramCard
            title="Contact degree distribution"
            subtitle="How many contacts each person has in the network"
            distribution={degreeDistribution}
            xLabel="Contacts"
            formatBin={(lo) => Math.round(lo)}
        />
    )
}

export function MobilityDistributionChart({ mobilityDistribution }) {
    return (
        <HistogramCard
            title="Mobility distribution"
            subtitle="How much of the population moves around, on a 0-1 scale"
            distribution={mobilityDistribution}
            xLabel="Mobility score"
            formatBin={(lo) => Number(lo).toFixed(1)}
        />
    )
}

export function SocialClusteringChart({ clustering }) {
    const data = useMemo(() => {
        if (!clustering?.age_groups) return []
        return clustering.age_groups.map((group, i) => ({
            group,
            Clustering: clustering.clustering[i],
        }))
    }, [clustering])

    if (!data.length) return <EmptyCard title="Social clustering by age" />

    return (
        <ChartCard
            title="Social clustering by age"
            subtitle="How tightly knit each age group's contacts are"
            note="A clustering coefficient of 1 means everyone in the group shares all their contacts."
            height={280}
        >
            <RadarChart data={data} margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
                <PolarGrid stroke={GRID} />
                <PolarAngleAxis dataKey="group" tick={{ fill: TEXT_SECONDARY, fontSize: 12 }} />
                <PolarRadiusAxis
                    angle={90}
                    domain={[0, 1]}
                    tick={{ fill: TEXT_SECONDARY, fontSize: 11 }}
                    axisLine={false}
                />
                <Tooltip {...tooltipProps} cursor={false} />
                <Radar
                    name="Clustering coefficient"
                    dataKey="Clustering"
                    stroke={ACCENT}
                    strokeWidth={2}
                    fill={ACCENT}
                    fillOpacity={0.35}
                />
            </RadarChart>
        </ChartCard>
    )
}
