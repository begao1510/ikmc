import React, { useState } from 'react';
import { useLang } from '../context/LangContext';

const GRADE_TOPICS = {
  1: "Addition, Subtraction, Counting, Shapes",
  2: "Multiplication, Missing Numbers, Geometry",
  3: "Division, Fractions, Perimeter, Logic",
  4: "Area, Factors, Averages, Equations",
  5: "Percentages, Ratios, Primes, Algebra",
};
const GRADE_TOPICS_VI = {
  1: "Cộng, Trừ, Đếm số, Hình học",
  2: "Nhân, Số còn thiếu, Hình học",
  3: "Chia, Phân số, Chu vi, Lô-gic",
  4: "Diện tích, Ước số, Trung bình, Phương trình",
  5: "Phần trăm, Tỉ lệ, Số nguyên tố, Đại số",
};

export default function LoginScreen({ onStart, onProgress }) {
  const { t, lang, toggleLang } = useLang();
  const [name, setName]           = useState('');
  const [grade, setGrade]         = useState(1);
  const [qCount, setQCount]       = useState(10);
  const [error, setError]         = useState('');

  const handleStart = () => {
    if (!name.trim()) { setError(lang === 'en' ? 'Please enter your name!' : 'Vui lòng nhập tên!'); return; }
    onStart({ name: name.trim(), grade, qCount });
  };

  return (
    <div className="login-screen">
      <button className="lang-toggle" onClick={toggleLang}>{t.language}</button>

      <div className="login-card">
        <div className="login-hero">
          <div className="kang-big">🦘</div>
          <div className="login-stars"><span>⭐</span><span>✨</span><span>⭐</span></div>
        </div>

        <h1 className="login-title">{t.appTitle}</h1>
        <p className="login-sub">{t.appSubtitle}</p>

        {/* Name */}
        <div className="form-group">
          <label className="form-label">{t.enterName}</label>
          <input
            className={`form-input ${error ? 'input-error' : ''}`}
            placeholder={t.namePlaceholder}
            value={name}
            onChange={e => { setName(e.target.value); setError(''); }}
            onKeyDown={e => e.key === 'Enter' && handleStart()}
            maxLength={40}
          />
          {error && <span className="form-error">{error}</span>}
        </div>

        {/* Grade */}
        <div className="form-group">
          <label className="form-label">{t.selectGrade}</label>
          <div className="grade-grid">
            {[1,2,3,4,5].map(g => (
              <button key={g}
                className={`grade-btn ${grade === g ? 'grade-selected' : ''}`}
                onClick={() => setGrade(g)}
              >
                <span className="grade-num">{t.gradeLabel(g)}</span>
                <span className="grade-topics">{lang === 'en' ? GRADE_TOPICS[g] : GRADE_TOPICS_VI[g]}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Question count */}
        <div className="form-group">
          <label className="form-label">
            {t.selectQuestions}: <strong>{qCount}</strong>
            <span className="q-time-hint"> ({qCount} {lang === 'en' ? 'min' : 'phút'})</span>
          </label>
          <div className="qcount-btns">
            {[5, 10, 15, 20].map(n => (
              <button key={n}
                className={`qcount-btn ${qCount === n ? 'qcount-selected' : ''}`}
                onClick={() => setQCount(n)}
              >{n}</button>
            ))}
          </div>
        </div>

        <button className="start-btn" onClick={handleStart}>
          {t.startTest} →
        </button>

        <button className="progress-btn" onClick={() => {
          if (!name.trim()) { setError(lang === 'en' ? 'Please enter your name first!' : 'Vui lòng nhập tên trước!'); return; }
          onProgress({ name: name.trim(), grade });
        }}>
          📊 {t.viewProgress}
        </button>

        <div className="medal-row">🥇 🥈 🥉 🎖</div>
      </div>
    </div>
  );
}
