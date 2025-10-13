import React from 'react';
import { useParams } from 'react-router-dom';

const AlertDetail = () => {
  const { id } = useParams();

  return (
    <div className="alert-detail">
      <h1>Alert Detail: {id}</h1>
      <p>Detailed alert view will be implemented here.</p>
    </div>
  );
};

export default AlertDetail;
