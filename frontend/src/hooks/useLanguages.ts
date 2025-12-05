import { useState, useEffect } from 'react';
import { geoApi } from '../api/endpoints';
import type { LanguageInfo } from '../api/types';

interface UseLanguagesResult {
  languages: LanguageInfo[];
  rtlLanguages: string[];
  isLoading: boolean;
  error: string | null;
}

export function useLanguages(): UseLanguagesResult {
  const [languages, setLanguages] = useState<LanguageInfo[]>([]);
  const [rtlLanguages, setRtlLanguages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await geoApi.getLanguages();
        setLanguages(response.data.languages);
        setRtlLanguages(response.data.rtl_languages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load languages');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLanguages();
  }, []);

  return { languages, rtlLanguages, isLoading, error };
}

export default useLanguages;
