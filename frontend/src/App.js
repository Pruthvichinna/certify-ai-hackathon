import React, { useState, useCallback } from 'react';

// ==============================================================================
// CertifyAI Frontend - FINAL PRESENTATION VERSION
// File: App.js
// Description: A visually enhanced and polished UI with animations, a modern
//              design, and improved user feedback.
// ==============================================================================


// --- Helper Components ---

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    <p className="mt-4 text-lg font-semibold text-gray-700">Agent at Work...</p>
    <p className="text-gray-500">Analyzing clauses and identifying risks.</p>
  </div>
);

const ErrorDisplay = ({ message }) => (
  <div className="bg-red-100 border-l-4 border-red-500 text-red-800 p-4 rounded-lg shadow-md" role="alert">
    <div className="flex items-center">
      <svg className="w-6 h-6 mr-3 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
      <div>
        <p className="font-bold">An Error Occurred</p>
        <p>{message}</p>
      </div>
    </div>
  </div>
);

const RiskCard = ({ item }) => {
    const riskStyles = {
        High: { border: 'border-red-400', bg: 'bg-red-50', icon: '🔴', text: 'text-red-800' },
        Red: { border: 'border-red-400', bg: 'bg-red-50', icon: '🔴', text: 'text-red-800' },
        Medium: { border: 'border-amber-400', bg: 'bg-amber-50', icon: '🟡', text: 'text-amber-800' },
        Amber: { border: 'border-amber-400', bg: 'bg-amber-50', icon: '🟡', text: 'text-amber-800' },
        Low: { border: 'border-green-400', bg: 'bg-green-50', icon: '🟢', text: 'text-green-800' },
        Green: { border: 'border-green-400', bg: 'bg-green-50', icon: '🟢', text: 'text-green-800' },
    };
    const styles = riskStyles[item.risk_level] || { border: 'border-gray-300', bg: 'bg-gray-50', icon: '⚪️', text: 'text-gray-800' };
    return (
        <div className={`p-5 rounded-lg border-l-4 ${styles.border} ${styles.bg} mb-4 shadow-sm transition-all duration-300 hover:shadow-md hover:scale-[1.02]`}>
            <h3 className={`font-bold text-lg ${styles.text} flex items-center`}>
              <span className="mr-2">{styles.icon}</span> {item.clause_summary}
            </h3>
            <p className="text-gray-700 mt-2 pl-6"><strong className="font-semibold">Explanation:</strong> {item.explanation}</p>
            <p className="text-indigo-700 mt-3 pl-6 font-medium"><strong className="font-semibold text-indigo-800">Suggested Action:</strong> {item.action_suggestion}</p>
        </div>
    );
};

// --- Main App Component ---

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setAnalysisResult(null);
      setError(null);
    }
  };
  
  const handleDrag = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    if (event.type === "dragenter" || event.type === "dragover") {
      setIsDragActive(true);
    } else if (event.type === "dragleave") {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      const file = event.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setSelectedFile(file);
        setAnalysisResult(null);
        setError(null);
      } else {
        setError("Invalid file type. Please upload a PDF.");
      }
    }
  }, []);


  const handleAnalyzeClick = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file to analyze.');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/analyze-pdf', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'An unknown server error occurred.');
      }

      setAnalysisResult(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message || 'Failed to connect to the analysis server.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-gray-50 to-indigo-100 font-sans text-gray-800" onDragEnter={handleDrag}>
      <main className="max-w-4xl mx-auto p-4 md:p-8">
        
        <header className="text-center mb-10">
          <div className="flex justify-center items-center gap-3">
            <svg className="w-12 h-12 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            <h1 className="text-5xl md:text-6xl font-extrabold text-gray-800 tracking-tight">
              Certify<span className="text-indigo-600">AI</span>
            </h1>
          </div>
          <p className="mt-3 text-lg text-gray-500">Demystify Legal Documents with Confidence.</p>
        </header>

        <div className="bg-white/70 backdrop-blur-xl p-6 rounded-2xl shadow-lg border border-gray-200">
          <label htmlFor="file-upload" onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
            className={`flex justify-center w-full h-48 px-6 pt-5 pb-6 border-2 ${isDragActive ? 'border-indigo-500' : 'border-gray-300'} border-dashed rounded-xl cursor-pointer transition-all duration-300`}>
            <div className="space-y-1 text-center self-center">
               <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
              <div className="flex text-sm text-gray-600">
                  <span className="font-semibold text-indigo-600 hover:text-indigo-500">Upload a file</span>
                  <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept=".pdf" />
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF documents only</p>
              {selectedFile && <p className="text-sm font-semibold text-green-700 pt-2 animate-pulse">Ready to Analyze: {selectedFile.name}</p>}
            </div>
          </label>
          <button
            onClick={handleAnalyzeClick}
            disabled={isLoading || !selectedFile}
            className="w-full mt-5 px-6 py-4 bg-gradient-to-r from-indigo-600 to-blue-500 text-white font-bold text-lg rounded-xl hover:shadow-lg hover:scale-105 focus:outline-none focus:ring-4 focus:ring-indigo-300 disabled:bg-gray-400 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed disabled:scale-100 transition-all duration-300"
          >
            {isLoading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>

        <div className="mt-10">
          {isLoading && <LoadingSpinner />}
          {error && <ErrorDisplay message={error} />}
          {analysisResult && (
            <div className="bg-white/70 backdrop-blur-xl p-6 rounded-2xl shadow-lg border border-gray-200 animate-fade-in">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-800 border-b-2 border-gray-200 pb-3 mb-4">Analysis Summary</h2>
                <p className="text-gray-700 text-base leading-relaxed">{analysisResult.analysis.summary}</p>
              </div>
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-800 border-b-2 border-gray-200 pb-3 mb-5">Risk Breakdown</h2>
                {analysisResult.analysis.risk_analysis.map((item, index) => (
                  <RiskCard key={index} item={item} />
                ))}
              </div>
              <div>
                <h2 className="text-3xl font-bold text-gray-800 border-b-2 border-gray-200 pb-3 mb-4">Agent Actions Log</h2>
                <ul className="space-y-2">
                  {analysisResult.actions_taken.map((action, index) => (
                    <li key={index} className="flex items-center text-gray-700">
                      <svg className="w-6 h-6 mr-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                      <span className="font-medium">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
         <footer className="text-center mt-16 pb-8 text-gray-500">
            <p>Powered by Google Cloud's Gemini Models</p>
        </footer>
      </main>
    </div>
  );
}

export default App;