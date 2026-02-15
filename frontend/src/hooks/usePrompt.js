import { useState, useEffect, useCallback } from 'react';
import api from '../services/apiClient';

function usePrompt({ setError, setSuccess }) {
  const [systemPrompt, setSystemPrompt] = useState('');

  useEffect(() => {
    const loadPrompt = async () => {
      try {
        const response = await api.get('/prompt');
        setSystemPrompt(response.data.system_prompt);
      } catch (err) {
        console.error('Error loading prompt:', err);
        setError('Failed to load system prompt');
      }
    };
    loadPrompt();
  }, [setError]);

  const handleUpdatePrompt = useCallback(async () => {
    try {
      await api.post('/prompt', { system_prompt: systemPrompt });
      setSuccess('Prompt updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating prompt:', err);
      setError('Failed to update prompt');
    }
  }, [systemPrompt, setError, setSuccess]);

  return { systemPrompt, setSystemPrompt, handleUpdatePrompt };
}

export default usePrompt;
