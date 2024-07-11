import React from 'react';

interface CardCollectionProps {
  cardCollectionStyles: {readonly [key: string]: string };
  children: React.ReactNode;
}


function CardCollection({cardCollectionStyles, children}:CardCollectionProps) {

  return (
    <>
      <div className={cardCollectionStyles.cardContainer} >
          {children}
        </div>
    </>
  );
}

export default CardCollection;
