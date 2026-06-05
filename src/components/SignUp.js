import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

const SignUp = () => {
  const handleSubmit = (e) => {
    e.preventDefault();
    // Navigate to login after signup
    window.location.href = '/login';
  };

  return (
    <div className="signup-container">
      <div className="signup-header">
        <div className="signup-icons">
          <i className="fas fa-heart"></i>
          <i className="fas fa-stethoscope"></i>
        </div>
        <div className="signup-title">Healthcare Recommendation System</div>
      </div>
      <div className="signup-card">
        <form onSubmit={handleSubmit}>
          <div className="signup-group">
            <label htmlFor="fullName" className="signup-label">Full Name</label>
            <input type="text" id="fullName" name="fullName" required className="signup-input" />
          </div>
          <div className="signup-group">
            <label htmlFor="email" className="signup-label">Email</label>
            <input type="email" id="email" name="email" required className="signup-input" />
          </div>
          <div className="signup-group">
            <label htmlFor="password" className="signup-label">Password</label>
            <input type="password" id="password" name="password" required className="signup-input" />
          </div>
          <button type="submit" className="signup-button">Sign Up</button>
        </form>
        <div className="signup-link">
          <Link to="/login">Already have an account? Log In</Link>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
