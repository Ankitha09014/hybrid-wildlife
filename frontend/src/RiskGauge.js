// frontend/src/RiskGauge.js
import React from "react";

const severityMap = {
  lion: "High", tiger: "High", leopard: "High", wolf: "High",
  bear: "High", elephant: "High", dog: "Low", cat: "Low",
  cow: "Low", goat: "Low", sheep: "Low", monkey: "Medium", unknown: "Unknown"
};

function RiskGauge({ detected }) {
  if (!detected || detected.length === 0) return <div>Waiting for prediction...</div>;

  const animal = detected[0];
  const label = animal.label.toLowerCase();
  const confidence = Math.round((animal.confidence || 0) * 100);
  const severity = severityMap[label] || "Unknown";

  const gaugeColor =
    severity === "High" ? "#e74c3c" :
    severity === "Medium" ? "#f1c40f" :
    severity === "Low" ? "#2ecc71" : "#95a5a6";

  return (
    <div style={{ textAlign:"center", padding:"20px", borderRadius:"12px", boxShadow:"0 4px 10px rgba(0,0,0,0.15)", maxWidth:"350px", margin:"auto" }}>
      <h4>⚡ Risk Level</h4>
      <div style={{
        position:"relative", height:"160px", width:"160px",
        borderRadius:"50%", border:`10px solid ${gaugeColor}`,
        display:"flex", alignItems:"center", justifyContent:"center",
        margin:"auto", background:"linear-gradient(145deg,#f0f0f0,#fff)"
      }}>
        <span style={{ fontSize:"20px", fontWeight:"bold", color:gaugeColor }}>{severity}</span>
      </div>
      <div style={{ marginTop:"15px", fontSize:"16px" }}>
        <strong>Animal:</strong> {label.charAt(0).toUpperCase() + label.slice(1)}<br/>
        <strong>Confidence:</strong> {confidence}%
      </div>
    </div>
  );
}

export default RiskGauge;
