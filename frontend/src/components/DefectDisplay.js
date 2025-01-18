import React, { useState } from 'react';

function DefectDisplay() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    // Create image preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please select an image first.");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/defects/detect', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to detect defects.");
      }

      const data = await response.json();
      setResult(data.defect_detected ? 'Defect Detected' : 'No Defect');
    } catch (error) {
      console.error(error);
      setResult("Error detecting defects. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Defect Detection</h1>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {imagePreview && (
        <div>
          <h3>Image Preview</h3>
          <img src={imagePreview} alt="Uploaded Preview" style={{ maxWidth: '100%', height: 'auto' }} />
        </div>
      )}
      <button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? "Processing..." : "Upload"}
      </button>
      {result && <p>{result}</p>}
    </div>
  );
}

export default DefectDisplay;
