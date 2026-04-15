import React, { useState, useCallback } from 'react';
import { LangProvider } from './context/LangContext';
import LoginScreen    from './components/LoginScreen';
import QuizScreen     from './components/QuizScreen';
import ResultsScreen  from './components/ResultsScreen';
import ProgressScreen from './components/ProgressScreen';
import './App.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function AppInner() {
  const [screen,     setScreen]     = useState('login');
  const [student,    setStudent]    = useState(null);   // { id, name, grade }
  const [config,     setConfig]     = useState({ grade:1, qCount:10 });
  const [questions,  setQuestions]  = useState([]);
  const [resultData, setResultData] = useState(null);
  const [newVoucher, setNewVoucher] = useState(null);
  const [error,      setError]      = useState('');

  /* ── Login / start ── */
  const handleStart = useCallback(async ({ name, grade, qCount }) => {
    setScreen('loading');
    setError('');
    try {
      // Register / login student
      const loginRes = await fetch(`${API}/student/login`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name, grade })
      });
      const loginData = await loginRes.json();
      const sid = loginData.student?.id;
      setStudent({ id: sid, name, grade });
      setConfig({ grade, qCount });

      // Fetch questions
      const qRes = await fetch(`${API}/questions?grade=${grade}&count=${qCount}`);
      if (!qRes.ok) throw new Error('Failed to load questions');
      const qData = await qRes.json();
      setQuestions(qData.questions);
      setScreen('quiz');
    } catch (e) {
      setError(e.message);
      setScreen('error');
    }
  }, []);

  /* ── Submit ── */
  const handleSubmit = useCallback(async ({ answers, skipped, timeTaken, questionIds }) => {
    setScreen('submitting');
    try {
      const correct_answers = {};
      questions.forEach(q => { correct_answers[String(q.id)] = q.answer; });

      const res = await fetch(`${API}/submit`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          student_id:     student?.id,
          grade:          config.grade,
          answers,
          skipped,
          time_taken:     timeTaken,
          question_ids:   questionIds,
          correct_answers,
          questions_data: questions,
        })
      });
      if (!res.ok) throw new Error('Submit failed');
      const data = await res.json();
      setResultData(data);
      setNewVoucher(data.new_voucher || null);
      setScreen('results');
    } catch (e) {
      setError(e.message);
      setScreen('error');
    }
  }, [questions, student, config]);

  /* ── Retry ── */
  const handleRetry = () => {
    setResultData(null); setNewVoucher(null); setQuestions([]);
    setScreen('login');
  };

  /* ── Progress ── */
  const handleProgress = async ({ name, grade }) => {
    setScreen('loading');
    try {
      const loginRes = await fetch(`${API}/student/login`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ name, grade })
      });
      const d = await loginRes.json();
      setStudent({ id: d.student?.id, name, grade });
      setScreen('progress');
    } catch {
      setScreen('progress');
    }
  };

  /* ── Screens ── */
  if (screen === 'loading' || screen === 'submitting') {
    return (
      <div className="loading-screen">
        <div className="kangaroo-bounce">🦘</div>
        <p style={{fontWeight:700,color:'#64748b',fontSize:'1rem'}}>
          {screen==='submitting' ? 'Grading...' : 'Loading...'}
        </p>
      </div>
    );
  }

  if (screen === 'error') {
    return (
      <div className="error-screen">
        <div style={{fontSize:'3rem'}}>⚠️</div>
        <p style={{maxWidth:'340px',textAlign:'center',color:'#64748b',lineHeight:1.7}}>
          {error || 'Could not connect. Is the Python server running?'}
        </p>
        <button className="start-btn" style={{maxWidth:'260px',marginTop:'16px'}} onClick={() => setScreen('login')}>← Back</button>
      </div>
    );
  }

  if (screen === 'login')    return <LoginScreen    onStart={handleStart} onProgress={handleProgress} />;
  if (screen === 'quiz')     return <QuizScreen     questions={questions} onSubmit={handleSubmit} studentName={student?.name} grade={config.grade} />;
  if (screen === 'results')  return <ResultsScreen  data={resultData} newVoucher={newVoucher} onRetry={handleRetry} />;
  if (screen === 'progress') return <ProgressScreen studentId={student?.id} studentName={student?.name} onBack={() => setScreen('login')} />;
}

export default function App() {
  return <LangProvider><AppInner /></LangProvider>;
}
