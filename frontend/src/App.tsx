import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Generate } from './pages/Generate';
import { Rewrite } from './pages/Rewrite';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/generate" replace />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/rewrite" element={<Rewrite />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
