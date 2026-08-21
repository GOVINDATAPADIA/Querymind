import { useState, useMemo } from 'react';
import { Download, ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, FileSpreadsheet } from 'lucide-react';
import './DataTable.css';

const PAGE_SIZE = 10;

export default function DataTable({ data }) {
  const [sortCol, setSortCol] = useState(null);
  const [sortDir, setSortDir] = useState('asc'); // 'asc' | 'desc'
  const [currentPage, setCurrentPage] = useState(1);

  const columns = useMemo(() => {
    if (!data || data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  // Sort logic
  const sortedData = useMemo(() => {
    if (!data) return [];
    if (!sortCol) return data;

    return [...data].sort((a, b) => {
      const valA = a[sortCol];
      const valB = b[sortCol];

      if (valA === null || valA === undefined) return 1;
      if (valB === null || valB === undefined) return -1;

      // Numeric comparison
      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortDir === 'asc' ? valA - valB : valB - valA;
      }

      // String comparison
      const strA = String(valA).toLowerCase();
      const strB = String(valB).toLowerCase();
      return sortDir === 'asc' ? strA.localeCompare(strB) : strB.localeCompare(strA);
    });
  }, [data, sortCol, sortDir]);

  // Pagination logic
  const totalPages = Math.ceil(sortedData.length / PAGE_SIZE);
  const paginatedData = useMemo(() => {
    if (sortedData.length <= PAGE_SIZE) return sortedData;
    const start = (currentPage - 1) * PAGE_SIZE;
    return sortedData.slice(start, start + PAGE_SIZE);
  }, [sortedData, currentPage]);

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortCol(col);
      setSortDir('asc');
    }
  };

  // Export to CSV
  const handleExportCSV = () => {
    if (!data || data.length === 0) return;

    const headers = columns.join(',');
    const rows = sortedData.map((row) =>
      columns
        .map((col) => {
          const val = row[col] === null || row[col] === undefined ? '' : String(row[col]);
          // Escape quotes and commas
          return `"${val.replace(/"/g, '""')}"`;
        })
        .join(',')
    );

    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `querymind_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!data || data.length === 0) {
    return <div className="datatable-empty">No results returned</div>;
  }

  return (
    <div className="datatable-container">
      <div className="datatable-header-bar">
        <div className="datatable-info">
          <FileSpreadsheet size={14} className="datatable-info-icon" />
          <span>{data.length} {data.length === 1 ? 'row' : 'rows'} returned</span>
        </div>
        <button className="datatable-export-btn" onClick={handleExportCSV} title="Download CSV">
          <Download size={13} /> Export CSV
        </button>
      </div>

      <div className="datatable-wrapper">
        <table className="datatable">
          <thead>
            <tr>
              <th className="datatable-th-index">#</th>
              {columns.map((col) => {
                const isSorted = sortCol === col;
                return (
                  <th
                    key={col}
                    onClick={() => handleSort(col)}
                    className={`datatable-th ${isSorted ? 'datatable-th--sorted' : ''}`}
                  >
                    <div className="datatable-th-content">
                      <span>{col}</span>
                      <span className="datatable-sort-icon">
                        {isSorted ? (
                          sortDir === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />
                        ) : (
                          <ArrowUpDown size={11} className="datatable-sort-idle" />
                        )}
                      </span>
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, rowIdx) => {
              const globalIdx = (currentPage - 1) * PAGE_SIZE + rowIdx + 1;
              return (
                <tr key={rowIdx}>
                  <td className="datatable-td-index">{globalIdx}</td>
                  {columns.map((col) => {
                    const val = row[col];
                    const isNum = typeof val === 'number';
                    return (
                      <td key={col} className={isNum ? 'datatable-td-num' : ''}>
                        {val !== null && val !== undefined ? String(val) : <span className="datatable-null">—</span>}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="datatable-pagination">
          <span className="datatable-page-text">
            Page {currentPage} of {totalPages}
          </span>
          <div className="datatable-pagination-btns">
            <button
              className="datatable-page-btn"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={14} /> Previous
            </button>
            <button
              className="datatable-page-btn"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
