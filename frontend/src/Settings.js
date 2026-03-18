function Settings() {
  return (
    <div className="page-container">
      <h2 className="page-title">⚙️ System Settings</h2>

      <div className="card-box">
        <label>Camera URL</label>
        <input className="input-field" type="text" placeholder="Enter IP Camera URL" />

        <label>Email for Alerts</label>
        <input className="input-field" type="email" placeholder="Enter alert email" />

        <button className="save-btn">Save Settings</button>
      </div>
    </div>
  );
}

export default Settings;