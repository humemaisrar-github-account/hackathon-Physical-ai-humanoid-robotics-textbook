import React from 'react';
import styles from './styles.module.css';

interface ToggleButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export const ToggleButton: React.FC<ToggleButtonProps> = ({ isOpen, onClick }) => {
  return (
    <div className={styles.toggleButton} onClick={onClick}>
      💬
    </div>
  );
};
