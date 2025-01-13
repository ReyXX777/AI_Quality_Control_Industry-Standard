import React, { useState } from 'react';

function DefectDisplay() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/defects/detect', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setResult(data.defect_detected ? 'Defect Detected' : 'No Defect');
  };

  return (
    <div>
      <h1>Defect Detection</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Upload</button>
      {result && <p>{result}</p>}
    </div>
  );
}

export default DefectDisplay;
