import { useState, useEffect, useRef, useCallback } from 'react';

export function useTimer(initialSeconds, onExpire) {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);
  const intervalRef = useRef(null);
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  const start = useCallback(() => setIsRunning(true), []);
  const stop  = useCallback(() => { setIsRunning(false); clearInterval(intervalRef.current); }, []);
  const reset = useCallback((secs) => {
    clearInterval(intervalRef.current);
    setSecondsLeft(secs ?? initialSeconds);
    setIsRunning(false);
  }, [initialSeconds]);

  useEffect(() => {
    if (!isRunning) { clearInterval(intervalRef.current); return; }
    intervalRef.current = setInterval(() => {
      setSecondsLeft(s => {
        if (s <= 1) {
          clearInterval(intervalRef.current);
          setIsRunning(false);
          onExpireRef.current();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, [isRunning]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const formatted = `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
  const percentage = (secondsLeft / initialSeconds) * 100;

  return { secondsLeft, formatted, percentage, start, stop, reset, setSecondsLeft };
}
