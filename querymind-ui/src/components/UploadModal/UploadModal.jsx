import { useState, useRef, useCallback } from 'react';
import { UploadCloud, FileSpreadsheet, X, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import './UploadModal.css';

export default function UploadModal({ isOpen, onClose, onUploadSuccess, apiBase }) {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successData, setSuccessData] = useState(null);
  const fileInputRef = useRef(null);

  const resetState = useCallback(() => {
    setFile(null);
    setTableName('');
    setIsDragging(false);
    setIsUploading(false);
    setError(null);
    setSuccessData(null);
  }, []);

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    const name = selectedFile.name;
    const ext = name.split('.').pop().toLowerCase();
    if (!['csv', 'tsv', 'xlsx', 'xls', 'txt'].includes(ext)) {
      setError('Please select a valid CSV (.csv, .tsv) or Excel (.xlsx, .xls) file.');
      return;
    }

    if (selectedFile.size > 15 * 1024 * 1024) {
      setError('File size exceeds the 15MB limit.');
      return;
    }

    setError(null);
    setFile(selectedFile);

    // Auto-generate clean table name from filename
    const cleanName = name
      .replace(/\.(csv|tsv|xlsx|xls|txt)$/i, '')
      .toLowerCase()
      .replace(/[\s\-\.]+/g, '_')
      .replace(/[^\w]/g, '')
      .replace(/^(\d)/, 'tbl_$1')
      .slice(0, 40);

    setTableName(cleanName);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || isUploading) return;

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    if (tableName.trim()) {
      formData.append('table_name', tableName.trim());
    }

    try {
      const response = await fetch(`${apiBase}/upload-csv`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.error || data.error || `HTTP ${response.status}: Upload failed`);
      }

      setSuccessData(data);
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
    } catch (err) {
      setError(err.message || 'An error occurred while uploading your dataset.');
    } finally {
      setIsUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="upload-modal-backdrop" onClick={handleClose}>
      <div className="upload-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="upload-modal-header">
          <div className="upload-modal-title">
            <UploadCloud size={20} className="upload-modal-icon" />
            <span>Upload Dataset (CSV / Excel)</span>
          </div>
          <button className="upload-modal-close" onClick={handleClose}>
            <X size={16} />
          </button>
        </div>

        <div className="upload-modal-body">
          {successData ? (
            <div className="upload-success-view">
              <CheckCircle2 size={48} className="upload-success-icon" />
              <h3>Dataset Imported Successfully!</h3>
              <p className="upload-success-desc">
                Created table <span className="upload-highlight">{successData.table_name}</span> with{' '}
                <strong>{successData.row_count.toLocaleString()}</strong> rows and{' '}
                <strong>{successData.column_count}</strong> columns.
              </p>

              {successData.columns && (
                <div className="upload-columns-preview">
                  <span className="upload-columns-title">Imported Columns:</span>
                  <div className="upload-columns-tags">
                    {successData.columns.map((c) => (
                      <span key={c.name} className="upload-column-tag">
                        {c.name} <small>{c.type}</small>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <button className="upload-action-btn upload-action-btn--primary" onClick={handleClose}>
                <Sparkles size={14} /> Start Querying Dataset
              </button>
            </div>
          ) : (
            <>
              <p className="upload-instructions">
                Upload your CSV, TSV, or Excel spreadsheet. QueryMind will automatically create a PostgreSQL table and allow you to ask questions about your data in natural language.
              </p>

              {/* Drag and Drop Zone */}
              <div
                className={`upload-dropzone ${isDragging ? 'upload-dropzone--active' : ''} ${
                  file ? 'upload-dropzone--has-file' : ''
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                  accept=".csv,.tsv,.xlsx,.xls,.txt"
                  style={{ display: 'none' }}
                />

                {file ? (
                  <div className="upload-file-details">
                    <FileSpreadsheet size={36} className="upload-file-icon" />
                    <div className="upload-file-meta">
                      <span className="upload-file-name">{file.name}</span>
                      <span className="upload-file-size">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                      </span>
                    </div>
                    <span className="upload-change-file">Click to choose another file</span>
                  </div>
                ) : (
                  <div className="upload-dropzone-prompt">
                    <UploadCloud size={40} className="upload-dropzone-icon" />
                    <span className="upload-dropzone-title">
                      Drag & Drop your dataset here, or <em>browse</em>
                    </span>
                    <span className="upload-dropzone-hint">
                      Supports .csv, .tsv, .xlsx, .xls (Up to 15MB)
                    </span>
                  </div>
                )}
              </div>

              {/* Table Name Input */}
              {file && (
                <div className="upload-table-name-field">
                  <label htmlFor="targetTableName">Database Table Name:</label>
                  <input
                    id="targetTableName"
                    type="text"
                    value={tableName}
                    onChange={(e) => setTableName(e.target.value.toLowerCase().replace(/[\s\-]+/g, '_'))}
                    placeholder="e.g. sales_transactions_2024"
                    disabled={isUploading}
                  />
                  <small>Only lowercase letters, numbers, and underscores.</small>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="upload-error-banner">
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              {/* Actions */}
              <div className="upload-modal-actions">
                <button className="upload-btn upload-btn--secondary" onClick={handleClose} disabled={isUploading}>
                  Cancel
                </button>
                <button
                  className="upload-btn upload-btn--primary"
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                >
                  {isUploading ? (
                    <>
                      <Loader2 size={15} className="upload-spinner" /> Ingesting Data...
                    </>
                  ) : (
                    <>
                      <UploadCloud size={15} /> Upload & Create Table
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
