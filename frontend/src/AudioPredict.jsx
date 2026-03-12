import React, { useState } from "react";
import axios from "axios";

function AudioPredict() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");

  const handlePredict = async () => {
    if (!file) {
      alert("Upload an audio file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(
        "http://localhost:5000/predict-audio",
        formData
      );
      setResult(
        `🐾 Animal: ${res.data.animal} (Confidence: ${res.data.confidence}%)`
      );
    } catch (err) {
      console.error(err);
      alert("Prediction failed");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Animal Sound Prediction</h2>

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handlePredict}>Predict</button>

      <h3>{result}</h3>
    </div>
  );
}

export default AudioPredict;
