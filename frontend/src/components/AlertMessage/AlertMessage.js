import React from 'react';
import styles from './AlertMessage.module.css';

function AlertMessage({ error, success }) {
  return (
    <>
      {error && <div className={`${styles.alert} ${styles.error}`}>{error}</div>}
      {success && <div className={`${styles.alert} ${styles.success}`}>{success}</div>}
    </>
  );
}

export default AlertMessage;
