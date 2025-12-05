import { Generate } from './pages/Generate';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <Generate />
    </ErrorBoundary>
  );
}

export default App;
