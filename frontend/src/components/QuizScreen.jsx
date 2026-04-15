import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLang } from '../context/LangContext';

const LEVEL_CFG = {
  easy:   { color:'#22c55e', emoji:'🟢' },
  medium: { color:'#f59e0b', emoji:'🟡' },
  hard:   { color:'#ef4444', emoji:'🔴' },
};

function playTone(freq, dur, vol=0.12) {
  try {
    const ctx = new (window.AudioContext||window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.frequency.value = freq;
    g.gain.setValueAtTime(vol, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
    o.start(); o.stop(ctx.currentTime + dur);
  } catch {}
}
const sfxSelect = () => playTone(540, 0.07);
const sfxSkip   = () => playTone(220, 0.2, 0.08);
const sfxDone   = () => { playTone(523, 0.1); setTimeout(() => playTone(659, 0.1), 120); };

function formatSecs(s) {
  const m = Math.floor(s/60); const sec = s%60;
  return m > 0 ? `${m}:${String(sec).padStart(2,'0')}` : `${sec}s`;
}

export default function QuizScreen({ questions, onSubmit, studentName, grade }) {
  const { t, lang, toggleLang } = useLang();
  const [current,      setCurrent]      = useState(0);
  const [answers,      setAnswers]      = useState({});   // {id: answer}
  const [skipped,      setSkipped]      = useState([]);   // ids auto-skipped
  const [perQSecs,     setPerQSecs]     = useState(60);   // countdown per question
  const [totalSecs,    setTotalSecs]    = useState(0);    // total elapsed
  const [showConfirm,  setShowConfirm]  = useState(false);
  const [showTimeUp,   setShowTimeUp]   = useState(false);
  const [skipFlash,    setSkipFlash]    = useState(false);
  const [selected,     setSelected]     = useState(null);
  const perQRef  = useRef(60);
  const totalRef = useRef(0);
  const timerRef = useRef(null);
  const totalTimerRef = useRef(null);

  const QUESTION_DURATION = 60; // 1 min per question

  const advanceQuestion = useCallback((reason = 'skip') => {
    if (reason === 'skip') {
      sfxSkip();
      setSkipFlash(true);
      const qid = questions[current]?.id;
      if (qid && !answers[qid]) setSkipped(s => [...s, qid]);
      setTimeout(() => setSkipFlash(false), 600);
    }
    setCurrent(c => {
      const next = c + 1;
      if (next >= questions.length) {
        // all done
        handleAutoSubmit();
        return c;
      }
      setSelected(null);
      perQRef.current = QUESTION_DURATION;
      setPerQSecs(QUESTION_DURATION);
      return next;
    });
  }, [current, questions, answers]);

  const advanceRef = useRef(advanceQuestion);
  useEffect(() => { advanceRef.current = advanceQuestion; }, [advanceQuestion]);

  // Per-question countdown
  useEffect(() => {
    clearInterval(timerRef.current);
    perQRef.current = QUESTION_DURATION;
    setPerQSecs(QUESTION_DURATION);
    timerRef.current = setInterval(() => {
      perQRef.current -= 1;
      setPerQSecs(perQRef.current);
      if (perQRef.current <= 0) {
        clearInterval(timerRef.current);
        advanceRef.current('skip');
      }
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [current]);

  // Total elapsed timer
  useEffect(() => {
    totalTimerRef.current = setInterval(() => {
      totalRef.current += 1;
      setTotalSecs(totalRef.current);
    }, 1000);
    return () => clearInterval(totalTimerRef.current);
  }, []);

  const handleAutoSubmit = useCallback(() => {
    clearInterval(timerRef.current);
    clearInterval(totalTimerRef.current);
    setShowTimeUp(true);
    sfxDone();
    setTimeout(() => {
      setShowTimeUp(false);
      doSubmit();
    }, 2200);
  }, []);

  const doSubmit = useCallback(() => {
    clearInterval(timerRef.current);
    clearInterval(totalTimerRef.current);
    onSubmit({
      answers,
      skipped,
      timeTaken: totalRef.current,
      questionIds: questions.map(q => q.id),
    });
  }, [answers, skipped, questions, onSubmit]);

  const handleSelect = (opt) => {
    sfxSelect();
    const qid = questions[current].id;
    setSelected(opt);
    setAnswers(prev => ({ ...prev, [qid]: opt }));
  };

  const goTo = (idx) => {
    setCurrent(idx);
    setSelected(answers[questions[idx]?.id] || null);
  };

  useEffect(() => {
    setSelected(answers[questions[current]?.id] || null);
  }, [current]);

  const q = questions[current];
  if (!q) return null;
  const lvl = LEVEL_CFG[q.level] || LEVEL_CFG.easy;
  const qText = lang === 'en' ? q.question_en : q.question_vi;
  const answeredCount = Object.keys(answers).length;
  const pct = (perQSecs / QUESTION_DURATION) * 100;
  const timerColor = pct > 40 ? '#22c55e' : pct > 20 ? '#f59e0b' : '#ef4444';
  const urgent = pct <= 20;

  return (
    <div className="quiz-screen">
      {/* Overlays */}
      {showTimeUp && (
        <div className="overlay"><div className="modal-box">
          <div style={{fontSize:'3rem'}}>⏰</div>
          <h2>{t.timeUp}</h2><p>{t.timeUpMsg}</p>
        </div></div>
      )}
      {skipFlash && <div className="skip-flash">{t.autoSkip}</div>}
      {showConfirm && (
        <div className="overlay"><div className="modal-box">
          <div style={{fontSize:'2.5rem'}}>📋</div>
          <h3>{t.confirmSubmit}</h3>
          <p style={{color:'#64748b',margin:'8px 0'}}>{answeredCount}/{questions.length} {lang==='en'?'answered':'đã trả lời'}</p>
          <div className="confirm-btns">
            <button className="btn-yes" onClick={doSubmit}>{t.yes}</button>
            <button className="btn-cancel" onClick={() => setShowConfirm(false)}>{t.cancel}</button>
          </div>
        </div></div>
      )}

      {/* Header */}
      <div className="quiz-header">
        <div className="quiz-logo">🦘 {lang==='en'?`Grade ${grade}`:`Lớp ${grade}`}</div>
        <div className="quiz-header-center">
          <span className="student-badge">👤 {studentName}</span>
        </div>
        <div className={`q-timer ${urgent ? 'q-timer-urgent' : ''}`} style={{color: timerColor}}>
          <svg viewBox="0 0 44 44" width="46" height="46">
            <circle cx="22" cy="22" r="18" fill="none" stroke="#e5e7eb" strokeWidth="4"/>
            <circle cx="22" cy="22" r="18" fill="none" stroke={timerColor} strokeWidth="4"
              strokeDasharray={`${2*Math.PI*18}`}
              strokeDashoffset={`${2*Math.PI*18*(1-pct/100)}`}
              strokeLinecap="round" transform="rotate(-90 22 22)"
              style={{transition:'stroke-dashoffset 1s linear, stroke 0.3s'}}
            />
          </svg>
          <span className="q-timer-text">{perQSecs}s</span>
        </div>
      </div>

      {/* Top bar */}
      <div className="quiz-topbar">
        <span className="total-elapsed">⏱ {formatSecs(totalSecs)}</span>
        <div className="progress-bar-wrap">
          <div className="progress-bar" style={{width:`${((current)/questions.length)*100}%`}}/>
        </div>
        <span className="q-fraction">{current+1}/{questions.length}</span>
      </div>

      {/* Question nav dots */}
      <div className="question-dots">
        {questions.map((qn, i) => {
          const isAns = !!answers[qn.id];
          const isSkip = skipped.includes(qn.id);
          return (
            <button key={i} onClick={() => goTo(i)}
              className={`dot ${i===current?'dot-active':''} ${isAns?'dot-answered':''} ${isSkip?'dot-skipped':''}`}
            >{i+1}</button>
          );
        })}
      </div>

      {/* Question card */}
      <div className="question-card">
        <div className="question-meta">
          <span className="q-num-label">{t.question} {current+1} {t.of} {questions.length}</span>
          <span className="q-level-badge" style={{background: lvl.color}}>
            {lvl.emoji} {lang==='en'?q.level:q.level==='easy'?'Dễ':q.level==='medium'?'TB':'Khó'}
          </span>
        </div>
        <div className="question-text">{qText}</div>
        <div className="options-grid">
          {q.options.map((opt, i) => {
            const letter = ['A','B','C','D'][i];
            const isSel = selected === opt;
            return (
              <button key={i} className={`option-btn ${isSel?'option-selected':''}`}
                onClick={() => handleSelect(opt)}>
                <span className="opt-letter" style={isSel?{background:'#ea580c'}:{}}>{letter}</span>
                <span className="opt-text">{opt}</span>
                {isSel && <span style={{marginLeft:'auto',color:'#16a34a',fontWeight:900}}>✓</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Navigation */}
      <div className="quiz-nav">
        <button className="nav-btn" onClick={() => goTo(current-1)} disabled={current===0}>← {t.prevQuestion}</button>
        <button className="submit-btn-green" onClick={() => setShowConfirm(true)}>🏁 {t.submitTest}</button>
        <button className="nav-btn" onClick={() => goTo(current+1)} disabled={current===questions.length-1}>{t.nextQuestion}</button>
      </div>

      <div className="answered-bar">
        ✅ {answeredCount} &nbsp;|&nbsp; ⏭ {skipped.length} &nbsp;|&nbsp; ⬜ {questions.length - answeredCount - skipped.length}
      </div>
    </div>
  );
}
