import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { uploadApi } from '../api'

const ALLOWED = ['application/pdf', 'text/plain', 'text/csv',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
const ALLOWED_EXT = ['.pdf', '.txt', '.csv', '.docx']

function FileIcon({ type }) {
  const icons = { pdf: '📄', txt: '📝', csv: '📊', docx: '📘' }
  const ext = type?.split('/').pop()?.split('.').pop() || 'pdf'
  return <span style={{ fontSize: '1.5rem' }}>{icons[ext] || '📄'}</span>
}

function StatusBadge({ status }) {
  const map = {
    ready:      { label: 'Ready',      cls: 'badge-high' },
    processing: { label: 'Processing', cls: 'badge-medium' },
    error:      { label: 'Error',      cls: 'badge-low' },
    pending:    { label: 'Pending',    cls: 'badge-primary' },
  }
  const { label, cls } = map[status] || { label: status, cls: 'badge-primary' }
  return <span className={`badge ${cls}`}>{label}</span>
}

export default function Upload() {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)

  // Fetch existing documents on mount
  useState(() => {
    uploadApi.list().then((r) => setDocuments(r.data.documents)).catch(() => {})
  })

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    setUploading(true)
    for (const file of acceptedFiles) {
      const toastId = toast.loading(`Uploading ${file.name}…`)
      try {
        const { data } = await uploadApi.upload(file)
        toast.success(`✓ ${file.name} — ${data.chunk_count} chunks indexed`, { id: toastId })
        // Refresh list
        const list = await uploadApi.list()
        setDocuments(list.data.documents)
      } catch (err) {
        const msg = err.response?.data?.detail || 'Upload failed'
        toast.error(`✗ ${file.name}: ${msg}`, { id: toastId })
      }
    }
    setUploading(false)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 50 * 1024 * 1024,
  })

  const handleDelete = async (docId, filename) => {
    try {
      await uploadApi.remove(docId)
      setDocuments((d) => d.filter((x) => x.id !== docId))
      toast.success(`Removed ${filename}`)
    } catch {
      toast.error('Delete failed')
    }
  }

  return (
    <div className="page-content animate-fade-in">
      <h1 style={{ marginBottom: 'var(--space-2)' }}>Knowledge Base</h1>
      <p style={{ marginBottom: 'var(--space-8)', color: 'var(--color-text-muted)' }}>
        Upload documents to build your knowledge base. Supported: PDF, DOCX, TXT, CSV.
      </p>

      {/* Drop zone */}
      <div
        id="upload-dropzone"
        {...getRootProps()}
        className="upload-dropzone"
        style={{
          borderColor: isDragActive ? 'var(--color-primary)' : 'var(--color-border)',
          background: isDragActive ? 'var(--color-primary-glow)' : 'var(--color-bg-surface)',
        }}
      >
        <input {...getInputProps()} id="upload-file-input" />
        <div className="upload-icon">{uploading ? '⏳' : isDragActive ? '📂' : '☁️'}</div>
        <h3>{isDragActive ? 'Drop to upload' : 'Drop files here'}</h3>
        <p className="text-sm text-muted">or click to browse • {ALLOWED_EXT.join(', ')} • max 50 MB</p>
        {uploading && (
          <div className="flex items-center gap-2 mt-4">
            <span className="spinner" />
            <span className="text-sm" style={{ color: 'var(--color-primary)' }}>Processing…</span>
          </div>
        )}
      </div>

      {/* Document list */}
      {documents.length > 0 && (
        <div className="mt-6">
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1rem', color: 'var(--color-text-secondary)' }}>
            {documents.length} document{documents.length !== 1 ? 's' : ''} in knowledge base
          </h3>
          <div className="doc-list">
            {documents.map((doc) => (
              <div key={doc.id} className="doc-item">
                <FileIcon type={doc.file_type} />
                <div className="doc-info">
                  <span className="font-semibold">{doc.filename}</span>
                  <span className="text-sm text-muted">
                    {doc.chunk_count} chunks • {new Date(doc.upload_date).toLocaleDateString()}
                  </span>
                </div>
                <StatusBadge status={doc.status} />
                <button
                  id={`delete-doc-${doc.id}`}
                  className="btn btn-ghost btn-sm"
                  onClick={() => handleDelete(doc.id, doc.filename)}
                  title="Remove document"
                >
                  🗑
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {documents.length === 0 && !uploading && (
        <div className="empty-state mt-6">
          <p>No documents yet. Upload your first knowledge base above.</p>
        </div>
      )}

      <style>{`
        .upload-dropzone {
          border: 2px dashed;
          border-radius: var(--radius-lg);
          padding: var(--space-12);
          text-align: center;
          cursor: pointer;
          transition: all var(--transition-normal);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: var(--space-3);
        }
        .upload-dropzone:hover {
          border-color: var(--color-primary);
          background: var(--color-primary-glow);
        }
        .upload-icon { font-size: 3rem; margin-bottom: var(--space-2); }
        .doc-list { display: flex; flex-direction: column; gap: var(--space-3); }
        .doc-item {
          display: flex;
          align-items: center;
          gap: var(--space-4);
          padding: var(--space-4);
          background: var(--color-bg-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          transition: border-color var(--transition-fast);
        }
        .doc-item:hover { border-color: var(--color-border-subtle); }
        .doc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
        .empty-state { text-align: center; color: var(--color-text-muted); padding: var(--space-8); }
      `}</style>
    </div>
  )
}
