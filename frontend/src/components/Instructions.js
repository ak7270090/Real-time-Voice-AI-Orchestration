import React from 'react';
import styles from './Instructions.module.css';

function Instructions() {
  return (
    <section className={`card ${styles.instructions}`}>
      <h2>How to Use</h2>
      <ol>
        <li><strong>Upload Documents:</strong> Add PDF or TXT files to the knowledge base</li>
        <li><strong>Configure Prompt:</strong> Customize how the agent behaves</li>
        <li><strong>Connect:</strong> Click "Connect to Agent" to start voice conversation</li>
        <li><strong>Talk:</strong> Ask questions about your uploaded documents</li>
        <li><strong>Listen:</strong> The agent will retrieve relevant info and respond</li>
      </ol>
    </section>
  );
}

export default Instructions;
