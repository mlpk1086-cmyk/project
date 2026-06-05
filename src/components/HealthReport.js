import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Pie, Bar, Doughnut } from 'react-chartjs-2';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import '../App.css';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
  ArcElement, RadialLinearScale, PointElement, LineElement, Filler
);

const HealthReport = () => {
  const [healthData, setHealthData] = useState({});
  const [risks, setRisks] = useState({});
  const [overallScore, setOverallScore] = useState(0);
  const [showPDFPreview, setShowPDFPreview] = useState(false);
  const reportRef = useRef(null);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem('healthData') || '{}');
    const riskData = JSON.parse(localStorage.getItem('risks') || '{}');
    setHealthData(data);
    setRisks(riskData);

    // Calculate overall health score (0-100)
    const calculateScore = () => {
      let score = 100;
      const riskWeights = { high: 30, moderate: 15, low: 0 };
      Object.values(riskData).forEach(risk => {
        score -= riskWeights[risk?.toLowerCase()] || 0;
      });
      const bmi = parseFloat(data.bmi);
      if (bmi > 30) score -= 20;
      else if (bmi > 25) score -= 10;
      return Math.max(0, Math.round(score));
    };
    setOverallScore(calculateScore());
  }, []);

  // Risk score for charts (0-100, higher risk = higher number)
  const getRiskScore = (risk) => {
    const scores = { high: 90, moderate: 60, low: 20, normal: 10 };
    return scores[risk?.toLowerCase()] || 10;
  };

  // Parameter ranges and comparisons
  const parameters = [
    {
      name: 'BMI',
      value: parseFloat(healthData.bmi) || 0,
      normal: [18.5, 24.9],
      unit: '',
      risk: risks.diabetes === 'High' ? 'high' : 'low'
    },
    {
      name: 'Hemoglobin (g/dL)',
      value: parseFloat(healthData.hemoglobinGdl || healthData.hemoglobin) || 0,
      normal: healthData.gender === 'female' ? [12, 16] : [13.5, 17.5],
      unit: 'g/dL',
      risk: risks.anemia === 'High' ? 'high' : 'low'
    },
    {
      name: 'Vitamin D (ng/mL)',
      value: parseFloat(healthData.serumVitaminDNgml) || 0,
      normal: [30, 100],
      unit: 'ng/mL',
      risk: risks.vitamind === 'High' ? 'high' : 'low'
    },
    {
      name: 'Fasting Blood Sugar (mg/dL)',
      value: parseFloat(healthData.fastingBloodSugar) || 0,
      normal: [70, 99],
      unit: 'mg/dL',
      risk: risks.diabetes === 'High' ? 'high' : 'low'
    }
  ];

  // Chart data
  const riskPieData = {
    labels: Object.keys(risks).map(key => key.charAt(0).toUpperCase() + key.slice(1).replace('d', ' D')),
    datasets: [{
      data: Object.values(risks).map(getRiskScore),
      backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'].slice(0, Object.keys(risks).length),
      borderWidth: 2
    }]
  };

  const bmiBarData = {
    labels: ['Your BMI'],
    datasets: [{
      label: 'BMI',
      data: [healthData.bmi || 0],
      backgroundColor: 'rgba(75, 192, 192, 0.6)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 2
    }]
  };



  const downloadPDF = async () => {
    const element = reportRef.current;
    const canvas = await html2canvas(element, { scale: 2 });
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgWidth = 210;
    const pageHeight = 295;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save('health-report.pdf');
  };

  const getRiskColor = (risk) => {
    const colors = { high: '#FF4444', moderate: '#FFAA00', low: '#44FF44', normal: '#44AAFF' };
    return colors[risk?.toLowerCase()] || '#666';
  };

  return (
    <div className="advanced-health-report">
      <style>{`
        .advanced-health-report { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .report-header { text-align: center; color: white; margin-bottom: 30px; }
        .overall-score { font-size: 4rem; font-weight: bold; background: rgba(255,255,255,0.2); padding: 20px; border-radius: 20px; margin: 20px 0; backdrop-filter: blur(10px); }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric-card { background: rgba(255,255,255,0.95); padding: 25px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .metric-title { font-size: 1.5rem; margin-bottom: 15px; color: #333; }
        .risk-gauge { width: 120px; height: 120px; margin: 0 auto; }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; margin: 40px 0; }
        .chart-container { background: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .param-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .param-table th, .param-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .param-table th { background: #f8f9fa; font-weight: 600; }
        .status-normal { color: #28a745; font-weight: bold; }
        .status-high { color: #dc3545; font-weight: bold; }
        .action-buttons { text-align: center; margin: 40px 0; }
        .pdf-btn { background: #28a745; color: white; border: none; padding: 15px 30px; font-size: 1.1rem; border-radius: 50px; cursor: pointer; margin: 0 10px; transition: all 0.3s; }
        .pdf-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(40,167,69,0.3); }
        .risk-card { padding: 20px; border-radius: 15px; text-align: center; color: white; font-weight: bold; font-size: 1.2rem; }
        .risk-high { background: linear-gradient(135deg, #FF6B6B, #FF8E8E); }
        .risk-moderate { background: linear-gradient(135deg, #FFA726, #FFB74D); }
        .risk-low { background: linear-gradient(135deg, #4CAF50, #81C784); }
        @media (max-width: 768px) { .metrics-grid, .charts-grid { grid-template-columns: 1fr; } }
      `}</style>

      <div ref={reportRef}>
        <div className="report-header">
          <div style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
            <i className="fas fa-heartbeat"></i> Health Risk Report
          </div>
          <div style={{ fontSize: '1.2rem', opacity: 0.9 }}>Diabetes & Heart Assessment</div>
        </div>

        {/* Overall Health Score */}
        <div className="metric-card" style={{ textAlign: 'center' }}>
          <div className="metric-title">Overall Health Score</div>
          <div className="overall-score" style={{ color: overallScore > 70 ? '#4CAF50' : overallScore > 40 ? '#FF9800' : '#F44336' }}>
            {overallScore}/100
          </div>
          <div style={{ color: '#666', fontSize: '1.1rem' }}>
            {overallScore > 80 ? 'Excellent' : overallScore > 60 ? 'Good' : overallScore > 40 ? 'Fair' : 'Needs Attention'}
          </div>
        </div>

        {/* Diabetes & Heart Risk Cards Only */}
        <div className="metrics-grid">
          {[
            risks.diabetes && { title: 'Diabetes Risk', risk: risks.diabetes, color: getRiskColor(risks.diabetes) },
            risks.heart && { title: 'Heart Risk', risk: risks.heart, color: getRiskColor(risks.heart) }
          ].filter(Boolean).map((item, idx) => (
            <div key={idx} className={`risk-card risk-${item.risk?.toLowerCase() || 'low'}`}>
              <div>{item.title}</div>
              <div style={{ fontSize: '2rem', margin: '10px 0' }}>{item.risk || 'Low'}</div>
              <div style={{ fontSize: '1.1rem', opacity: 0.9 }}>{getRiskScore(item.risk)}/100 Risk Score</div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="chart-container">
            <div className="metric-title" style={{ textAlign: 'center', marginBottom: '20px' }}>Diabetes & Heart Risk Levels</div>
            <Pie data={riskPieData} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
          </div>
          <div className="chart-container">
            <div className="metric-title" style={{ textAlign: 'center', marginBottom: '20px' }}>BMI Analysis</div>
            <Bar data={bmiBarData} options={{ responsive: true, scales: { y: { beginAtZero: true } } }} />
          </div>
        </div>

        {/* Parameter Comparison Table */}
        <div className="metric-card">
          <div className="metric-title">Parameter Analysis (vs Normal Ranges)</div>
          <table className="param-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Your Value</th>
                <th>Normal Range</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {parameters.map((param, idx) => (
                <tr key={idx}>
                  <td>{param.name}</td>
                  <td>{param.value?.toFixed(1) || 'N/A'} {param.unit}</td>
                  <td>{param.normal[0]}-{param.normal[1]} {param.unit}</td>
                  <td className={`status-${param.value < param.normal[0] || param.value > param.normal[1] ? 'high' : 'normal'}`}>
                    {param.value >= param.normal[0] && param.value <= param.normal[1] ? 'Normal' : 'Abnormal'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Patient Summary */}
        <div className="metric-card">
          <div className="metric-title">Patient Profile</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            {[
              { label: 'Age', value: healthData.age || 'N/A' },
              { label: 'Gender', value: healthData.gender || 'N/A' },
              { label: 'BMI', value: healthData.bmi || 'N/A' },
              { label: 'Weight', value: `${healthData.weight || 'N/A'} kg` },
              { label: 'Height', value: `${healthData.height || 'N/A'} cm` },
              { label: 'Location', value: healthData.location || 'N/A' },
              { label: 'Smoking', value: healthData.smokingStatus || 'N/A' }
            ].map((item, idx) => (
              <div key={idx} style={{ padding: '10px', background: '#f8f9fa', borderRadius: '10px' }}>
                <div style={{ fontWeight: 'bold', color: '#666' }}>{item.label}</div>
                <div>{item.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="pdf-btn" onClick={downloadPDF}>
            <i className="fas fa-download"></i> Download PDF Report
          </button>
          <Link to="/dashboard" className="pdf-btn" style={{ background: '#6c757d', textDecoration: 'none' }}>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HealthReport;

