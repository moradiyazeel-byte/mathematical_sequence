import { useState, useCallback } from 'react';
import { analyzeSequence } from '../services/api';

const useAnalyze = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (inputText) => {
    setLoading(true);
    setError(null);
    setResult(null);

    // Artificial delay for better UX (between 1 and 1.5 seconds)
    const delay = Math.floor(Math.random() * 500) + 1000;
    await new Promise(resolve => setTimeout(resolve, delay));

    try {
      const sequence = inputText
        .split(',')
        .map(s => s.trim())
        .filter(s => s !== '')
        .map(s => {
          const num = parseFloat(s);
          if (isNaN(num)) throw new Error(`"${s}" valid number nathi`);
          return num;
        });

      if (sequence.length < 3) throw new Error('Minimum 3 numbers joie');

      const data = await analyzeSequence(sequence);
      setResult(data);
      return data;

    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, analyze, reset };
};

export default useAnalyze;