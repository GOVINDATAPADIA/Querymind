import {
  BarChart,
  Bar,
  LineChart,
  Line,
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
import './ChartRenderer.css';

const COLORS = ['#00ff88', '#00e5ff', '#4d7cff', '#b44dff', '#ffa502', '#ff4757'];

export default function ChartRenderer({ chartSuggestion }) {
  if (!chartSuggestion) return null;

  const { type, data, columns, title } = chartSuggestion;

  if (!type || type === 'table' || !data || data.length === 0) return null;

  const xKey = columns?.[0];
  const yKey = columns?.[1];

  const commonTooltipStyle = {
    contentStyle: {
      background: '#111118',
      border: '1px solid #2a2a40',
      borderRadius: '6px',
      fontSize: '0.8rem',
    },
    labelStyle: { color: '#8888a0', fontWeight: 600 },
    itemStyle: { color: '#e0e0e8' },
  };

  return (
    <div className="chart-container">
      {title && <div className="chart-title">{title}</div>}
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          {type === 'bar' ? (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f1f35" />
              <XAxis dataKey={xKey} tick={{ fill: '#8888a0', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8888a0', fontSize: 11 }} />
              <Tooltip {...commonTooltipStyle} />
              <Bar dataKey={yKey} fill="#00ff88" radius={[4, 4, 0, 0]}>
                {data.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          ) : type === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f1f35" />
              <XAxis dataKey={xKey} tick={{ fill: '#8888a0', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8888a0', fontSize: 11 }} />
              <Tooltip {...commonTooltipStyle} />
              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#00e5ff"
                strokeWidth={2}
                dot={{
                  r: 4,
                  fill: '#00e5ff',
                  stroke: '#00e5ff',
                  filter: 'drop-shadow(0 0 4px rgba(0, 229, 255, 0.7))',
                }}
                activeDot={{
                  r: 6,
                  fill: '#00e5ff',
                  stroke: '#0a0a0f',
                  strokeWidth: 2,
                }}
              />
            </LineChart>
          ) : type === 'pie' ? (
            <PieChart>
              <Tooltip {...commonTooltipStyle} />
              <Legend
                wrapperStyle={{ fontSize: '0.75rem', color: '#8888a0' }}
              />
              <Pie
                data={data}
                dataKey={yKey}
                nameKey={xKey}
                cx="50%"
                cy="50%"
                outerRadius={100}
                strokeWidth={2}
                stroke="#0a0a0f"
              >
                {data.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          ) : null}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
