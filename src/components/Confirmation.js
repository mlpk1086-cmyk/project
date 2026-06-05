import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

const Confirmation = () => {
  return (
    <div className="confirmation-container">
      <div className="confirmation-header">
        <div className="confirmation-icons">
          <i className="fas fa-heart"></i>
          <i className="fas fa-stethoscope"></i>
        </div>
        <div className="confirmation-title">Healthcare Recommendation System</div>
      </div>
      <div className="confirmation-card">
        <div className="confirmation-success-icon">
          <i className="fas fa-check-circle"></i>
        </div>
        <div className="confirmation-success-title">Health Data Submitted Successfully!</div>
        <div className="confirmation-success-text">
          Abnormal health patterns have been detected. Personalized recommendations will be generated based on your data.
        </div>
        <Link to="/recommendations" className="confirmation-button">View Recommendations</Link>
      </div>
    </div>
  );
};

export default Confirmation;
