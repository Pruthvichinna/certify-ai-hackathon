import React, { useState, useCallback, useRef } from 'react';
import { FileUp, ImageUp, ClipboardPaste } from 'lucide-react';

// ==============================================================================
// CertifyAI Frontend - Multi-Modal FINAL with Tabs
// File: App.js
// ==============================================================================

// --- Helper Component: Loading Spinner ---
const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center p-8 text-center" aria-label="Loading analysis">
    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    <p className="mt-4 text-lg font-semibold text-gray-700">Agent at Work...</p>
    <p className="text-gray-500">Your document is being analyzed by our AI assistant.</p>
  </div>
);

// --- Helper Component: Error Display ---
const ErrorDisplay = ({ message }) => (
  <div className="bg-red-100 border-l-4 border-red-500 text-red-800 p-4 rounded-lg shadow-md animate-fade-in" role="alert">
    <div className="flex items-center">
      <svg className="w-6 h-6 mr-3 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
      <div>
        <p className="font-bold">An Error Occurred</p>
        <p>{message}</p>
      </div>
    </div>
  </div>
);

// --- Helper Component: Risk Card ---
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
        <span className="mr-3">{styles.icon}</span> {item.clause_summary}
      </h3>
      <p className="text-gray-700 mt-2 pl-8"><strong className="font-semibold">Explanation:</strong> {item.explanation}</p>
      <p className="text-indigo-700 mt-3 pl-8 font-medium"><strong className="font-semibold text-indigo-800">Suggested Action:</strong> {item.action_suggestion}</p>
    </div>
  );
};

// --- Main App Component ---
function App() {
  const [activeTab, setActiveTab] = useState('pdf');
  const [selectedFile, setSelectedFile] = useState(null);
  const [pastedText, setPastedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const fileInputRef = useRef(null);

  const resetState = useCallback(() => {
    setSelectedFile(null);
    setPastedText('');
    setAnalysisResult(null);
    setError(null);
    if(fileInputRef.current) fileInputRef.current.value = null;
  }, []);

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
    resetState();
  }, [resetState]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleAnalyzeClick = async () => {
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    
    // ========================================================================
    // CRITICAL: Replace this with your actual deployed Cloud Run backend URL
    // ========================================================================
    const API_BASE_URL = 'https://certify-ai-backend-15690670158.us-central1.run.app';
    
    let endpoint = '';
    let body;
    let headers = {};

    if (activeTab === 'pdf' || activeTab === 'image') {
      if (!selectedFile) {
        setError('Please select a file to analyze.');
        setIsLoading(false);
        return;
      }
      endpoint = activeTab === 'pdf' ? '/analyze-pdf' : '/analyze-image';
      const formData = new FormData();
      formData.append('file', selectedFile);
      body = formData;
    } else {
      if (!pastedText.trim()) {
        setError('Please paste some text to analyze.');
        setIsLoading(false);
        return;
      }
      endpoint = '/analyze-text';
      body = JSON.stringify({ text: pastedText });
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(API_BASE_URL + endpoint, { method: 'POST', body, headers });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'An unknown server error occurred.');
      setAnalysisResult(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to the analysis server.');
    } finally {
      setIsLoading(false);
    }
  };

  const TabButton = ({ tabName, label, Icon }) => (
    <button
      onClick={() => handleTabChange(tabName)}
      className={`flex items-center justify-center w-full px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
        activeTab === tabName ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-600 hover:bg-indigo-100'
      }`}
    >
      <Icon className="w-5 h-5 mr-2" />
      {label}
    </button>
  );
  
  const FileInputArea = ({ acceptedFiles }) => (
    <div className="text-center p-6 border-2 border-dashed border-gray-300 rounded-lg">
      <input type="file" ref={fileInputRef} id="file-upload" className="hidden" onChange={handleFileChange} accept={acceptedFiles} />
      <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center text-gray-500 hover:text-indigo-600 transition-colors">
         <div className="p-4 bg-indigo-100 rounded-full mb-3">
            {activeTab === 'pdf' ? <FileUp className="w-8 h-8 text-indigo-600" /> : <ImageUp className="w-8 h-8 text-indigo-600" />}
         </div>
         <span className="font-semibold">Click to browse</span>
         <span className="text-xs mt-1">or drag and drop your file</span>
      </label>
      {selectedFile && <p className="mt-3 text-sm font-medium text-green-700">Selected: {selectedFile.name}</p>}
    </div>
  );

  return (
    <div className="min-h-screen w-full bg-gray-50 font-sans text-gray-800">
      <main className="max-w-4xl mx-auto p-4 md:p-8">
        <header className="text-center mb-10 animate-fade-in-down">
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-800">
            Certify<span className="text-indigo-600">AI</span>
          </h1>
          <p className="mt-3 text-lg text-gray-600">Your Proactive Legal Guardian</p>
        </header>

        <div className="bg-white p-6 rounded-2xl shadow-xl border border-gray-200 animate-fade-in-up">
          <div className="grid grid-cols-3 gap-2 mb-6 p-1 bg-gray-100 rounded-lg">
            <TabButton tabName="pdf" label="Upload PDF" Icon={FileUp} />
            <TabButton tabName="image" label="Upload Image" Icon={ImageUp} />
            <TabButton tabName="text" label="Paste Text" Icon={ClipboardPaste} />
          </div>

          {activeTab === 'pdf' && <FileInputArea acceptedFiles=".pdf" />}
          {activeTab === 'image' && <FileInputArea acceptedFiles="image/png, image/jpeg" />}
          {activeTab === 'text' && (
            <textarea
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste the full text of your legal document here..."
              className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-sm"
            />
          )}

          <button onClick={handleAnalyzeClick} disabled={isLoading} className="w-full mt-6 text-lg font-semibold text-white bg-indigo-600 rounded-lg py-3 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-transform duration-200 active:scale-95 disabled:bg-indigo-300 disabled:cursor-not-allowed shadow-lg hover:shadow-indigo-300">
            {isLoading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>

        <div className="mt-12">
          {isLoading && <LoadingSpinner />}
          {error && <ErrorDisplay message={error} />}
          {analysisResult && (
            <div className="bg-white p-6 rounded-2xl shadow-xl border border-gray-200 animate-fade-in-up">
              <h2 className="text-3xl font-bold text-gray-800 mb-2 border-b-2 pb-2 border-indigo-200">Analysis Complete</h2>
              <div className="mt-6">
                <h3 className="text-xl font-bold text-gray-700 mb-3">Summary</h3>
                <p className="text-gray-600 bg-gray-50 p-4 rounded-lg">{analysisResult.analysis.summary}</p>
              </div>
              <div className="mt-6">
                 <h3 className="text-xl font-bold text-gray-700 mb-4">Risk Breakdown</h3>
                 {analysisResult.analysis.risk_analysis.map((item, index) => <RiskCard key={index} item={item} />)}
              </div>
               <div className="mt-6">
                 <h3 className="text-xl font-bold text-gray-700 mb-3">Agent Actions</h3>
                 <ul className="list-disc list-inside bg-gray-50 p-4 rounded-lg text-gray-600 space-y-1">
                   {analysisResult.actions_taken.map((action, index) => <li key={index} className="text-green-800"><span className="font-semibold">✔</span> {action}</li>)}
                 </ul>
              </div>
            </div>
          )}
        </div>
         <footer className="text-center mt-16 pb-8 text-gray-500">
            <p>Powered by Google Cloud's Gemini</p>
        </footer>
      </main>
    </div>
  );
}

export default App;