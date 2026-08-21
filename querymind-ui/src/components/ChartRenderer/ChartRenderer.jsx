import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieIcon } from 'lucide-react';
import './ChartRenderer.css';

const NEON_COLORS = [
  '#00ff88', // Neon Green
  '#00e5ff', // Neon Cyan
  '#b44dff', // Neon Purple
  '#ff9f43', // Neon Orange
  '#4d7cff', // Neon Blue
  '#ff4757', // Neon Red
  '#ff6b9d', // Neon Pink
  '#feca57', // Neon Yellow
];

function formatValue(value) {
  if (typeof value === 'number') {
    if (Math.abs(value) >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    if (Math.abs(value) >= 1_000) {
      return `$${(value / 1_000).toFixed(1)}k`;
    }
    return Number.isInteger(value) ? value : value.toFixed(2);
  }
  return value;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="custom-chart-tooltip">
      <div className="custom-chart-tooltip-label">{label}</div>
      {payload.map((entry, index) => (
        <div key={index} className="custom-chart-tooltip-item">
          <span className="custom-chart-tooltip-dot" style={{ backgroundColor: entry.color || entry.fill }} />
          <span className="custom-chart-tooltip-name">{entry.name}:</span>
          <span className="custom-chart-tooltip-val">
            {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function ChartRenderer({ chartSuggestion }) {
  if (!chartSuggestion) return null;

  const { type, data, columns, title, y_series, x, y } = chartSuggestion;

  if (!type || type === 'table' || !data || data.length === 0) return null;

  const xKey = x || columns?.[0];
  const yKey = y || columns?.[1];

  const getChartIcon = () => {
    switch (type) {
      case 'line':
      case 'area':
        return <TrendingUp size={15} className="chart-title-icon" />;
      case 'pie':
        return <PieIcon size={15} className="chart-title-icon" />;
      default:
        return <BarChart3 size={15} className="chart-title-icon" />;
    }
  };

  return (
    <div className="chart-container">
      {title && (
        <div className="chart-title">
          {getChartIcon()}
          <span>{title}</span>
        </div>
      )}

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={280}>
          {type === 'area' ? (
            <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <defs>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00e5ff" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#00e5ff" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c1c36" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
              />
              <YAxis
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
                tickFormatter={formatValue}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey={yKey}
                stroke="#00e5ff"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#areaGradient)"
              />
            </AreaChart>
          ) : type === 'line' ? (
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c1c36" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
              />
              <YAxis
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
                tickFormatter={formatValue}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#00e5ff"
                strokeWidth={2.5}
                dot={{ fill: '#00e5ff', stroke: '#06060b', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#00e5ff', strokeWidth: 2, fill: '#fff' }}
              />
            </LineChart>
          ) : type === 'pie' ? (
            <PieChart>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => <span style={{ color: '#8b8ba8', fontSize: 12 }}>{value}</span>}
              />
              <Pie
                data={data}
                dataKey={yKey}
                nameKey={xKey}
                cx="50%"
                cy="50%"
                outerRadius={90}
                innerRadius={50}
                paddingAngle={4}
                stroke="#0d0d14"
                strokeWidth={2}
              >
                {data.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={NEON_COLORS[index % NEON_COLORS.length]}
                  />
                ))}
              </Pie>
            </PieChart>
          ) : (
            /* Bar Chart (Default) */
            <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00ff88" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#00cc6a" stopOpacity={0.4} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c1c36" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
              />
              <YAxis
                tick={{ fill: '#8b8ba8', fontSize: 11 }}
                stroke="#2a2a46"
                tickLine={false}
                tickFormatter={formatValue}
              />
              <Tooltip content={<CustomTooltip />} />
              {y_series && y_series.length > 0 ? (
                y_series.map((seriesKey, idx) => (
                  <Bar
                    key={seriesKey}
                    dataKey={seriesKey}
                    fill={NEON_COLORS[idx % NEON_COLORS.length]}
                    radius={[4, 4, 0, 0]}
                  />
                ))
              ) : (
                <Bar dataKey={yKey} fill="url(#barGradient)" radius={[4, 4, 0, 0]}>
                  {data.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={NEON_COLORS[index % NEON_COLORS.length]}
                    />
                  ))}
                </Bar>
              )}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
