import React, { useState, useEffect, useRef } from 'react';
import { useLang } from '../context/LangContext';

const GRADE_CFG = {
  Gold:        { emoji:'🥇', color:'#d97706', bg:'#fef3c7', border:'#f59e0b' },
  Silver:      { emoji:'🥈', color:'#4b5563', bg:'#f3f4f6', border:'#9ca3af' },
  Bronze:      { emoji:'🥉', color:'#b45309', bg:'#fef9c3', border:'#d97706' },
  Participant: { emoji:'🎖', color:'#7c3aed', bg:'#ede9fe', border:'#8b5cf6' },
};

function Confetti({ active }) {
  const ref = useRef();
  useEffect(() => {
    if (!active) return;
    const cv = ref.current; if (!cv) return;
    const ctx = cv.getContext('2d');
    cv.width = window.innerWidth; cv.height = window.innerHeight;
    const P = Array.from({length:110}, () => ({
      x: Math.random()*cv.width, y: Math.random()*-cv.height,
      w: Math.random()*9+4, h: Math.random()*5+3,
      col: ['#f59e0b','#22c55e','#3b82f6','#ec4899','#ef4444','#8b5cf6'][Math.floor(Math.random()*6)],
      spd: Math.random()*3+1.5, ang: Math.random()*360, spin: (Math.random()-.5)*5, drift: (Math.random()-.5)*1.5
    }));
    let fr; const draw = () => {
      ctx.clearRect(0,0,cv.width,cv.height);
      P.forEach(p => {
        ctx.save(); ctx.translate(p.x+p.w/2,p.y+p.h/2); ctx.rotate(p.ang*Math.PI/180);
        ctx.fillStyle=p.col; ctx.fillRect(-p.w/2,-p.h/2,p.w,p.h); ctx.restore();
        p.y+=p.spd; p.x+=p.drift; p.ang+=p.spin;
        if (p.y>cv.height) { p.y=-20; p.x=Math.random()*cv.width; }
      });
      fr = requestAnimationFrame(draw);
    };
    draw();
    const t = setTimeout(() => cancelAnimationFrame(fr), 5000);
    return () => { cancelAnimationFrame(fr); clearTimeout(t); };
  }, [active]);
  if (!active) return null;
  return <canvas ref={ref} style={{position:'fixed',inset:0,pointerEvents:'none',zIndex:999}}/>;
}

function fmt(s, t) {
  const m=Math.floor(s/60), sec=s%60;
  return m>0 ? `${m}${t.mins} ${sec}${t.secs}` : `${sec}${t.secs}`;
}

export default function ResultsScreen({ data, newVoucher, onRetry }) {
  const { t, lang, toggleLang } = useLang();
  const [review, setReview] = useState(false);
  const [rIdx, setRIdx] = useState(0);
  const [animIn, setAnimIn] = useState(false);
  const [showVoucher, setShowVoucher] = useState(!!newVoucher);
  useEffect(() => { setTimeout(() => setAnimIn(true), 80); }, []);

  const { pass, fail, skip, total, percentage, grade_label, results, time_taken } = data;
  const gcfg = GRADE_CFG[grade_label] || GRADE_CFG.Participant;
  const gradeLabel = { Gold:t.gold, Silver:t.silver, Bronze:t.bronze, Participant:t.participant }[grade_label];
  const msg = percentage>=90?t.excellent:percentage>=75?t.great:percentage>=60?t.good:t.keepTrying;

  if (review) {
    const r = results[rIdx];
    const qText = lang==='en' ? r.question_en : r.question_vi;
    const expText = lang==='en' ? r.explanation_en : r.explanation_vi;
    const statusColor = r.status==='pass'?'#16a34a':r.status==='fail'?'#dc2626':'#64748b';
    const statusLabel = r.status==='pass'?`✅ ${t.correct}`:r.status==='fail'?`❌ ${t.incorrect}`:`⏭ ${t.skipped}`;
    return (
      <div className="review-screen">
        <div className="review-header">
          <button className="back-btn" onClick={()=>setReview(false)}>← {t.backToResults}</button>
          <span style={{fontWeight:700,color:'#64748b'}}>{rIdx+1}/{results.length}</span>
          <button className="lang-toggle-sm" onClick={toggleLang}>{t.language}</button>
        </div>
        <div className="review-nav-dots">
          {results.map((_,i)=>{
            const s=results[i].status;
            return <button key={i} onClick={()=>setRIdx(i)}
              className={`dot ${i===rIdx?'dot-active':''} ${s==='pass'?'dot-answered':s==='fail'?'dot-skipped':''}`}
            >{i+1}</button>;
          })}
        </div>
        <div className="review-card">
          <div className="review-meta">
            <span className="q-level-badge" style={{background: GRADE_CFG[grade_label]?.color || '#64748b', color:'white', fontSize:'0.78rem', padding:'3px 10px', borderRadius:'999px'}}>
              {r.level}
            </span>
            <span style={{fontWeight:800, color:statusColor}}>{statusLabel}</span>
          </div>
          <div className="review-question">{qText}</div>
          <div className="review-options">
            {(r.options||[]).map((opt,i)=>{
              const letter=['A','B','C','D'][i];
              const isC=opt===r.correct_answer; const isU=opt===r.user_answer;
              return <div key={i} className={`review-opt ${isC?'opt-correct':isU&&!isC?'opt-wrong':''}`}>
                <span className="opt-letter">{letter}</span>
                <span style={{flex:1}}>{opt}</span>
                {isC && <span style={{color:'#16a34a',fontWeight:900}}>✓</span>}
                {isU&&!isC && <span style={{color:'#dc2626',fontWeight:900}}>✗</span>}
              </div>;
            })}
          </div>
          {!r.user_answer && <div className="skipped-note">⏭ {t.skipped}</div>}
          {expText && <div className="explanation-box"><strong>💡 {t.explanation}:</strong><p>{expText}</p></div>}
        </div>
        <div className="review-footer-nav">
          <button onClick={()=>setRIdx(i=>Math.max(0,i-1))} disabled={rIdx===0}>←</button>
          <button onClick={()=>setRIdx(i=>Math.min(results.length-1,i+1))} disabled={rIdx===results.length-1}>→</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`results-screen ${animIn?'results-in':''}`}>
      <Confetti active={grade_label==='Gold'} />
      <button className="lang-toggle" onClick={toggleLang}>{t.language}</button>

      {/* Voucher modal */}
      {showVoucher && newVoucher && (
        <div className="overlay">
          <div className="modal-box voucher-modal">
            <div style={{fontSize:'3.5rem'}}>🎁</div>
            <h2 style={{color:'#d97706'}}>{t.newVoucher}</h2>
            <p style={{fontSize:'1.2rem',fontWeight:800,color:'#92400e',margin:'8px 0'}}>{t.voucherValue}</p>
            <p style={{color:'#64748b',fontSize:'0.9rem'}}>ID: {newVoucher.id}</p>
            <button className="btn-yes" style={{marginTop:'16px'}} onClick={()=>setShowVoucher(false)}>
              🎉 {lang==='en'?'Awesome!':'Tuyệt vời!'}
            </button>
          </div>
        </div>
      )}

      <div className="results-content">
        <div className="medal-display" style={{background:gcfg.bg, border:`2px solid ${gcfg.border}`}}>
          <div style={{fontSize:'3.5rem'}}>{gcfg.emoji}</div>
          <div style={{fontFamily:'Baloo 2',fontWeight:800,fontSize:'1.2rem',color:gcfg.color}}>{gradeLabel}</div>
        </div>
        <p className="results-message">{msg}</p>

        {/* Pass / Fail / Skip summary */}
        <div className="pfs-row">
          <div className="pfs-card pfs-pass">
            <span className="pfs-num">{pass}</span>
            <span className="pfs-label">{t.passLabel}</span>
          </div>
          <div className="pfs-card pfs-fail">
            <span className="pfs-num">{fail}</span>
            <span className="pfs-label">{t.failLabel}</span>
          </div>
          <div className="pfs-card pfs-skip">
            <span className="pfs-num">{skip}</span>
            <span className="pfs-label">{t.skipLabel}</span>
          </div>
        </div>

        {/* Circle score */}
        <div className="score-circle">
          <svg viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" strokeWidth="10"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke={gcfg.color} strokeWidth="10"
              strokeDasharray={`${2*Math.PI*52}`}
              strokeDashoffset={`${2*Math.PI*52*(1-percentage/100)}`}
              strokeLinecap="round" transform="rotate(-90 60 60)"
              style={{transition:'stroke-dashoffset 1.2s ease-out'}}
            />
          </svg>
          <div className="score-inner">
            <span className="score-num" style={{color:gcfg.color}}>{pass}</span>
            <span className="score-denom">/{total}</span>
          </div>
        </div>
        <div style={{fontFamily:'Baloo 2',fontSize:'1.3rem',fontWeight:800,color:gcfg.color,marginBottom:'8px'}}>
          {percentage}%
        </div>
        {time_taken != null && (
          <div className="time-taken-badge">⏱️ {t.timeTaken}: <strong>{fmt(time_taken,t)}</strong></div>
        )}

        <div className="results-actions">
          <button className="review-btn" onClick={()=>setReview(true)}>📖 {t.reviewAnswers}</button>
          <button className="retry-btn" onClick={onRetry}>🔄 {t.tryAgain}</button>
        </div>
      </div>
    </div>
  );
}
