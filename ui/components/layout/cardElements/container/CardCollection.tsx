import React from 'react';
import styles from './CardCollection.module.scss';

interface CardCollectionProps {
  children: React.ReactNode;
}

function CardCollection({ children }:CardCollectionProps) {

  return (
    <>
      <div className={styles.cardContainer} >
          {children}
        </div>
    </>
  );
}

export default CardCollection;
