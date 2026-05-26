import './DataTable.css';

export default function DataTable({ data }) {
  if (!data || data.length === 0) {
    return <div className="datatable-empty">No results returned</div>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="datatable-wrapper">
      <table className="datatable">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {columns.map((col) => (
                <td key={col}>
                  {row[col] !== null && row[col] !== undefined
                    ? String(row[col])
                    : '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
