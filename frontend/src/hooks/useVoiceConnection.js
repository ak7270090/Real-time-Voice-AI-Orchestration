import { useState, useCallback } from 'react';
import api from '../services/apiClient';

function useVoiceConnection({ setError }) {
  const [token, setToken] = useState('');
  const [livekitUrl, setLivekitUrl] = useState('');
  const [connected, setConnected] = useState(false);

  const handleConnect = useCallback(async () => {
    try {
      setError('');
      const roomName = `voice-agent-room-${Date.now()}`;
      const response = await api.post('/generate-token', {
        room_name: roomName,
        participant_name: `User-${Date.now()}`,
      });

      setToken(response.data.token);
      setLivekitUrl(response.data.url);
      setConnected(true);
    } catch (err) {
      console.error('Error connecting:', err);
      const detail = err.response?.data?.detail;
      setError(detail || 'Failed to connect to voice agent. Please check your connection and try again.');
    }
  }, [setError]);

  const handleDisconnect = useCallback(() => {
    setToken('');
    setLivekitUrl('');
    setConnected(false);
  }, []);

  return { token, livekitUrl, connected, handleConnect, handleDisconnect };
}

export default useVoiceConnection;
