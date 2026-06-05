import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SignUp from './components/SignUp';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Confirmation from './components/Confirmation';
import PersonalizedRecommendations from './components/PersonalizedRecommendation';
import HealthReport from './components/HealthReport';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<SignUp />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/confirmation" element={<Confirmation />} />
          <Route path="/recommendations" element={<PersonalizedRecommendations />} />
          <Route path="/report" element={<HealthReport />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
