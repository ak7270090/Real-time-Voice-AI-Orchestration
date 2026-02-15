import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  useVoiceAssistant,
  useLocalParticipant,
  useTrackTranscription,
} from '@livekit/components-react';
import { Track } from 'livekit-client';
import api from '../../services/apiClient';
import styles from './VoiceAssistantUI.module.css';

const STATE_LABELS = {
  disconnected: 'Disconnected',
  connecting: 'Connecting...',
  initializing: 'Initializing...',
  idle: 'Idle',
  listening: 'Listening...',
  thinking: 'Thinking...',
  speaking: 'Speaking...',
};

const STATE_STYLE_MAP = {
  listening: styles.listening,
  thinking: styles.thinking,
  speaking: styles.speaking,
  idle: styles.idle,
  initializing: styles.initializing,
  connecting: styles.connecting,
  'pre-connect-buffering': styles.preConnectBuffering,
  disconnected: styles.disconnected,
};

function VoiceAssistantUI({ documents }) {
  const { localParticipant, isMicrophoneEnabled } = useLocalParticipant();
  const { state: agentState, audioTrack, agentTranscriptions } = useVoiceAssistant();

  const localMicTrack = localParticipant.getTrackPublication(Track.Source.Microphone);
  const localTrackRef = localMicTrack
    ? { participant: localParticipant, publication: localMicTrack, source: Track.Source.Microphone }
    : undefined;
  const { segments: userSegments } = useTrackTranscription(localTrackRef);

  const [ragSources, setRagSources] = useState([]);
  const [ragLoading, setRagLoading] = useState(false);
  const lastQueriedRef = useRef('');

  const transcriptRef = useRef([]);
  const [transcript, setTranscript] = useState([]);

  useEffect(() => {
    if (userSegments.length === 0) return;
    const latest = userSegments[userSegments.length - 1];
    const existing = transcriptRef.current;
    const idx = existing.findIndex((e) => e.id === `user-${latest.id}`);
    const entry = { id: `user-${latest.id}`, role: 'user', text: latest.text, final: latest.final };
    if (idx >= 0) {
      existing[idx] = entry;
    } else {
      existing.push(entry);
    }
    setTranscript([...existing]);

    if (latest.final && latest.text && latest.text !== lastQueriedRef.current) {
      lastQueriedRef.current = latest.text;
      setRagLoading(true);
      api.post('/query', { query: latest.text })
        .then((res) => setRagSources(res.data.results || []))
        .catch(() => setRagSources([]))
        .finally(() => setRagLoading(false));
    }
  }, [userSegments]);

  useEffect(() => {
    if (agentTranscriptions.length === 0) return;
    const latest = agentTranscriptions[agentTranscriptions.length - 1];
    const existing = transcriptRef.current;
    const idx = existing.findIndex((e) => e.id === `agent-${latest.id}`);
    const entry = { id: `agent-${latest.id}`, role: 'agent', text: latest.text, final: latest.final };
    if (idx >= 0) {
      existing[idx] = entry;
    } else {
      existing.push(entry);
    }
    setTranscript([...existing]);
  }, [agentTranscriptions]);

  const transcriptEndRef = useRef(null);
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const toggleMic = useCallback(async () => {
    await localParticipant.setMicrophoneEnabled(!isMicrophoneEnabled);
  }, [localParticipant, isMicrophoneEnabled]);

  return (
    <div className={styles.voiceAssistant}>
      <div className={styles.voiceControls}>
        <div className={`${styles.statusIndicator} ${STATE_STYLE_MAP[agentState] || ''}`}>
          {STATE_LABELS[agentState] || agentState}
        </div>

        <button
          className={`${styles.micButton} ${isMicrophoneEnabled ? styles.micOn : styles.micOff}`}
          onClick={toggleMic}
        >
          {isMicrophoneEnabled ? 'Mute Mic' : 'Unmute Mic'}
        </button>
      </div>

      <div className={styles.transcriptPanel}>
        <h3>Live Transcript</h3>
        <div className={styles.transcriptLog}>
          {transcript.length === 0 ? (
            <p className={styles.emptyState}>Start speaking to see the transcript...</p>
          ) : (
            transcript.map((entry) => (
              <div
                key={entry.id}
                className={`${styles.transcriptEntry} ${entry.role === 'user' ? styles.user : styles.agent} ${entry.final ? '' : styles.partial}`}
              >
                <span className={styles.transcriptRole}>{entry.role === 'user' ? 'You' : 'Agent'}</span>
                <span className={styles.transcriptText}>{entry.text}</span>
              </div>
            ))
          )}
          <div ref={transcriptEndRef} />
        </div>
      </div>

      <div className={styles.ragPanel}>
        <h3>RAG Sources Used</h3>
        {ragLoading ? (
          <p className={styles.emptyState}>Retrieving sources...</p>
        ) : ragSources.length === 0 ? (
          <p className={styles.emptyState}>No sources retrieved yet</p>
        ) : (
          <ul className={styles.ragSourcesList}>
            {ragSources.map((src, i) => (
              <li key={i} className={styles.ragSourceItem}>
                <div className={styles.ragSourceHeader}>
                  <span className={styles.ragSourceName}>{src.metadata?.source || 'Unknown'}</span>
                  <span className={styles.ragSourceScore}>
                    {(100 / (1 + src.similarity_score)).toFixed(0)}% match
                  </span>
                </div>
                <p className={styles.ragSourceContent}>{src.content}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      {(!documents || documents.length === 0) && (
        <p className={styles.warningText} style={{ marginTop: 12 }}>
          Upload documents first to get better answers!
        </p>
      )}
    </div>
  );
}

export default VoiceAssistantUI;
