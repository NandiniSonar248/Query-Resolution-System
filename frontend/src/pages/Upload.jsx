import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { uploadApi } from '../api';
import AppLayout from '../components/AppLayout';

const ALLOWED = ['application/pdf', 'text/plain', 'text/csv',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
const ALLOWED_EXT = ['.pdf', '.txt', '.csv', '.docx'];

function FileIcon({ type }) {
  const icons = { pdf: '📄', txt: '📝', csv: '📊', docx: '📘' };
  const ext = type?.split('/').pop()?.split('.').pop() || 'pdf';
  return <span style={{ fontSize: '1.5rem' }}>{icons[ext] || '📄'}</span>;
}

function StatusBadge({ status }) {
  const map = {
    ready:      { label: 'Uploaded',      cls: 'badge-high' },
    processing: { label: 'Uploading & Indexing', cls: 'badge-medium' },
    error:      { label: 'Error',      cls: 'badge-low' },
    pending:    { label: 'Pending',    cls: 'badge-primary' },
  };
  const { label, cls } = map[status] || { label: status, cls: 'badge-primary' };
  return <span className={`badge ${cls}`}>{label}</span>;
}

export default function Upload() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = useCallback(async () => {
    try {
      const { data } = await uploadApi.list();
      setDocuments(data.documents);
    } catch (err) {
      console.error(err);
    }
  }, []);

  // Fetch immediately on mount
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Poll if any document is processing
  useEffect(() => {
    const isProcessing = documents.some(doc => doc.status === 'processing');
    if (!isProcessing) return;
    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000);
    return () => clearInterval(interval);
  }, [documents, fetchDocuments]);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    for (const file of acceptedFiles) {
      const toastId = toast.loading(`Uploading ${file.name}…`);
      try {
        await uploadApi.upload(file);
        toast.success(`✓ ${file.name} — upload complete, processing in background.`, { id: toastId });
        await fetchDocuments();
      } catch (err) {
        const msg = err.response?.data?.detail || 'Upload failed';
        toast.error(`✗ ${file.name}: ${msg}`, { id: toastId });
      }
    }
    setUploading(false);
  }, [fetchDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 50 * 1024 * 1024,
  });

  const handleDelete = async (docId, filename) => {
    try {
      await uploadApi.remove(docId);
      setDocuments((d) => d.filter((x) => x.id !== docId));
      toast.success(`Removed ${filename}`);
    } catch {
      toast.error('Delete failed');
    }
  };

  return (
    <AppLayout>
      <div className="page-content animate-fade-in" style={{ maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
        <header style={{ marginBottom: 'var(--space-8)' }}>
          <h1 style={{ margin: 0, fontSize: '2rem' }}>Knowledge Base</h1>
          <p style={{ marginTop: 'var(--space-2)', color: 'var(--color-text-muted)' }}>
            Upload documents to build your AI's knowledge base. Supported: PDF, DOCX, TXT, CSV.
          </p>
        </header>

        {/* Drop zone */}
        <div
          {...getRootProps()}
          className="upload-dropzone card-glass"
          style={{
            borderColor: isDragActive ? 'var(--color-primary)' : 'var(--color-border)',
            background: isDragActive ? 'var(--color-primary-glow)' : 'var(--color-bg-surface)',
            padding: 'var(--space-12)',
            textAlign: 'center',
            cursor: 'pointer',
            borderStyle: 'dashed',
            borderWidth: '2px',
            marginBottom: 'var(--space-8)'
          }}
        >
          <input {...getInputProps()} />
          <div style={{ fontSize: '3rem', marginBottom: 'var(--space-4)' }}>
            {uploading ? '⏳' : isDragActive ? '📂' : '☁️'}
          </div>
          <h3 style={{ marginBottom: 'var(--space-2)' }}>{isDragActive ? 'Drop to upload' : 'Drop files here'}</h3>
          <p className="text-sm text-muted">or click to browse • {ALLOWED_EXT.join(', ')} • max 50 MB</p>
          
          {(uploading || documents.some(doc => doc.status === 'processing')) && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
              <span className="spinner" />
              <span className="text-sm" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>Uploading & indexing chunks…</span>
            </div>
          )}
        </div>

        {/* Document list */}
        {documents.length > 0 && (
          <div className="animate-fade-in-up">
            <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1.1rem', color: 'var(--color-text-primary)' }}>
              {documents.length} document{documents.length !== 1 ? 's' : ''} stored
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {documents.map((doc) => (
                <div key={doc.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', padding: 'var(--space-4)' }}>
                  <FileIcon type={doc.file_type} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{doc.filename}</div>
                    <div className="text-sm text-muted" style={{ marginTop: '4px' }}>
                      {doc.chunk_count} chunks • Indexed {new Date(doc.upload_date).toLocaleDateString()}
                    </div>
                  </div>
                  <StatusBadge status={doc.status} />
                  <button
                    className="btn btn-ghost btn-icon"
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    title="Remove document"
                    style={{ color: 'var(--color-danger)' }}
                  >
                    🗑
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {documents.length === 0 && !uploading && (
          <div className="card" style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
            <p className="text-muted">No documents yet. Upload your first knowledge base above to start asking questions.</p>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
