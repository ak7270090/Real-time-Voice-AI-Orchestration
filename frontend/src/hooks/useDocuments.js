import { useState, useEffect, useCallback } from 'react';
import api from '../services/apiClient';

function useDocuments({ setError, setSuccess }) {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const response = await api.get('/documents');
      setDocuments(response.data);
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileUpload = useCallback(async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
      setError('Only PDF and TXT files are supported');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/upload-document', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setSuccess(`Document uploaded: ${response.data.chunks_created} chunks created`);
      setTimeout(() => setSuccess(''), 3000);
      await loadDocuments();
    } catch (err) {
      console.error('Error uploading document:', err);
      const detail = err.response?.data?.detail;
      setError(detail || 'Failed to upload document. Please check your connection and try again.');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  }, [loadDocuments, setError, setSuccess]);

  const handleDeleteDocument = useCallback(async (filename) => {
    try {
      setError('');
      await api.delete(`/documents/${encodeURIComponent(filename)}`);
      setSuccess(`Document "${filename}" deleted`);
      setTimeout(() => setSuccess(''), 3000);
      await loadDocuments();
    } catch (err) {
      console.error('Error deleting document:', err);
      const detail = err.response?.data?.detail;
      setError(detail || 'Failed to delete document. Please try again.');
    }
  }, [loadDocuments, setError, setSuccess]);

  return { documents, uploading, handleFileUpload, handleDeleteDocument };
}

export default useDocuments;
