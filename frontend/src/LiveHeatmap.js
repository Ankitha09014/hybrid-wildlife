import React from "react";

// Labels and data for the risk matrix
const impactLabels = ["Catastrophic", "Significant", "Moderate", "Low", "Negligible"];
const likelihoodLabels = ["Improbable", "Remote", "Occasional", "Probable", "Frequent"];
const riskMatrix = [
  [5, 10, 15, 20, 25],
  [4, 8, 12, 16, 20],
  [3, 6, 9, 12, 15],
  [2, 4, 6, 8, 10],
  [1, 2, 3, 4, 5],
];

// Color mapping based on risk value
const getColor = (value) => {
  if (value >= 20) return "#e53935";     // Red
  if (value >= 15) return "#fb8c00";     // Orange
  if (value >= 6)  return "#fbc02d";     // Yellow
  if (value >= 3)  return "#43a047";     // Light Green
  return "#1b5e20";                      // Dark Green
};

// Legend data
const legend = [
  { label: "Catastrophic", color: "#e53935", action: "Stop" },
  { label: "Unacceptable", color: "#fb8c00", action: "Urgent Action" },
  { label: "Undesirable", color: "#fbc02d", action: "Action" },
  { label: "Acceptable", color: "#43a047", action: "Monitor" },
  { label: "Desirable", color: "#1b5e20", action: "No Action" },
];

// Colors for axis headers
const axisHeaderStyle = {
  background: "linear-gradient(90deg, #42a5f5 0%, #7e57c2 100%)",
  color: "#fff",
  textAlign: "center",
  fontWeight: "bold",
  fontSize: "1.1em",
  border: "1px solid #fff"
};
const axisVerticalStyle = {
  background: "linear-gradient(180deg, #ffb300 0%, #e53935 100%)",
  color: "#fff",
  textAlign: "center",
  fontWeight: "bold",
  fontSize: "1.1em",
  border: "1px solid #fff"
};

const LiveHeatmap = () => (

  <div style={{
    fontFamily: "sans-serif",
    width: "100%",
    maxWidth: 800,
    margin: "0 auto",
    overflowX: "auto",
    padding: "1em",
   
  }}>
    <div style={{fontWeight: "bold", fontSize: "1.3em", marginBottom: 12, color: "#37474f"}}>
      Risk Prediction Heatmap
    </div>
    <table style={{
      borderCollapse: "collapse",
      width: "100%",
      minWidth: 500,
      boxShadow: "0 2px 12px rgba(0,0,0,0.07)"
    }}>
      <thead>
        <tr>
          <th style={{...axisVerticalStyle, minWidth: 110}} rowSpan={2}>Impact</th>
          <th style={{...axisHeaderStyle}} colSpan={5}>Likelihood</th>
        </tr>
        <tr>
          {likelihoodLabels.map((label, idx) => (
            <th key={idx} style={{...axisHeaderStyle, padding: "8px 4px"}}>
              <div style={{ fontWeight: "bold", fontSize: "1em" }}>{idx + 1}</div>
              <div style={{ fontSize: "0.95em" }}>{label}</div>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {riskMatrix.map((row, i) => (
          <tr key={i}>
            <td style={{
              ...axisVerticalStyle,
              fontWeight: "bold",
              fontSize: "1em",
              minWidth: 110
            }}>
              {impactLabels[i]} <span style={{ fontWeight: "normal" }}>{5 - i}</span>
            </td>
            {row.map((value, j) => (
              <td
                key={j}
                style={{
                  background: getColor(value),
                  color: "#fff",
                  textAlign: "center",
                  fontWeight: "bold",
                  border: "1px solid #fff",
                  fontSize: "1.1em",
                  width: 60,
                  height: 40,
                  transition: "background 0.3s"
                }}
              >
                {value}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
    {/* Legend */}
    <div style={{
      marginTop: 20,
      display: "flex",
      flexWrap: "wrap",
      gap: "1.2em 2em",
      alignItems: "center"
    }}>
      {legend.map((item, idx) => (
        <div key={idx} style={{ display: "flex", alignItems: "center", marginBottom: 2 }}>
          <div style={{
            width: 18, height: 18, background: item.color, marginRight: 8, border: "1px solid #ccc"
          }} />
          <span style={{ minWidth: 110, fontWeight: "bold" }}>{item.label}</span>
          <span style={{ marginLeft: 8 }}>{item.action}</span>
        </div>
      ))}
    </div>
  </div>
);

export default LiveHeatmap;
