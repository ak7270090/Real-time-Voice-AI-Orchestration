import React from 'react';
import styles from './KnowledgeBase.module.css';

function KnowledgeBase({ documents, uploading, onFileUpload, onDeleteDocument }) {
  return (
    <section className="card">
      <h2>Knowledge Base</h2>
      <div className={styles.uploadSection}>
        <label htmlFor="file-upload" className={styles.uploadButton}>
          {uploading ? 'Uploading...' : 'Upload Document (PDF/TXT)'}
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".pdf,.txt"
          onChange={onFileUpload}
          disabled={uploading}
          style={{ display: 'none' }}
        />
      </div>

      <div className={styles.documentsList}>
        <h3>Uploaded Documents ({documents.length})</h3>
        {documents.length === 0 ? (
          <p className="empty-state">No documents uploaded yet</p>
        ) : (
          <ul>
            {documents.map((doc, index) => (
              <li key={index}>
                <div className={styles.docInfo}>
                  <strong>{doc.filename}</strong>
                  <span className={styles.docMeta}>
                    {doc.chunk_count} chunks • {(doc.file_size / 1024).toFixed(1)} KB
                  </span>
                </div>
                <button
                  className={styles.deleteButton}
                  onClick={() => {
                    if (window.confirm(`Delete "${doc.filename}"? This cannot be undone.`)) {
                      onDeleteDocument(doc.filename);
                    }
                  }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

export default KnowledgeBase;
