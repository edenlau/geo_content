import { Activity } from 'lucide-react';
import { useState, useEffect } from 'react';
import { geoApi } from '../../api/endpoints';
import { cn } from '../../utils/cn';

export function Header() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await geoApi.health();
        setIsHealthy(response.data.status === 'healthy');
      } catch {
        setIsHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 60000); // Check every 60s
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-amber-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Title */}
          <div>
            <h1 className="text-2xl font-bold text-white">Tocanan GEO Action</h1>
          </div>

          {/* Status indicator */}
          <div className="flex items-center gap-2">
            <Activity className={cn(
              'w-4 h-4',
              isHealthy === null && 'text-gray-400',
              isHealthy === true && 'text-green-400',
              isHealthy === false && 'text-red-400'
            )} />
            <span className={cn(
              'text-sm',
              isHealthy === null && 'text-gray-400',
              isHealthy === true && 'text-green-400',
              isHealthy === false && 'text-red-400'
            )}>
              {isHealthy === null ? 'Checking...' : isHealthy ? 'API Connected' : 'API Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
