import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

const Login = () => {
  const handleSubmit = (e) => {
    e.preventDefault();
    // Navigate to dashboard
    window.location.href = '/dashboard';
  };

  return (
    <div className="login-container">
      <div className="login-header">
        <div className="login-icons">
          <i className="fas fa-heart"></i>
          <i className="fas fa-stethoscope"></i>
        </div>
        <div className="login-title">Healthcare Recommendation System</div>
      </div>
      <div className="login-card">
        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-group">
            <label htmlFor="email" className="login-label">Email</label>
            <input type="email" id="email" name="email" required className="login-input" />
          </div>
          <div className="login-group">
            <label htmlFor="password" className="login-label">Password</label>
            <input type="password" id="password" name="password" required className="login-input" />
          </div>
          <div className="login-checkbox-group">
            <input type="checkbox" id="rememberMe" name="rememberMe" className="login-checkbox" />
            <label htmlFor="rememberMe">Remember Me</label>
          </div>
          <div className="login-forgot">
            <a href="#">Forgot Password?</a>
          </div>
          <button type="submit" className="login-button">Login</button>
        </form>
        <div className="login-link">
          <Link to="/signup">Don't have an account? Sign Up</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
