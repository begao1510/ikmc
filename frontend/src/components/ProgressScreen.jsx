import React, { useState, useEffect } from 'react';
import { useLang } from '../context/LangContext';

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const SESSIONS_NEEDED = 12;

function fmt(s, t) {
  const m = Math.floor(s/60), sec = s%60;
  return m>0 ? `${m}${t.mins} ${sec}${t.secs}` : `${sec}${t.secs}`;
}

export default function ProgressScreen({ studentId, studentName, onBack }) {
  const { t, lang, toggleLang } = useLang();
  const [data,      setData]      = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [redeemId,  setRedeemId]  = useState(null);
  const [pin,       setPin]       = useState('');
  const [pinErr,    setPinErr]    = useState('');
  const [pinOk,     setPinOk]     = useState('');
  const [showPin,   setShowPin]   = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/student/${studentId}/progress`);
      const d = await r.json();
      setData(d);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [studentId]);

  const handleRedeem = async () => {
    if (!pin) { setPinErr(lang==='en'?'Enter PIN':'Nhập mã PIN'); return; }
    try {
      const r = await fetch(`${API}/student/${studentId}/redeem`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ voucher_id: redeemId, pin })
      });
      const d = await r.json();
      if (d.success) {
        setPinOk(t.redeemSuccess); setPinErr(''); setPin('');
        setTimeout(() => { setRedeemId(null); setPinOk(''); load(); }, 1800);
      } else {
        setPinErr(t.redeemError);
      }
    } catch { setPinErr('Error'); }
  };

  const gradeColor = (g) => g==='Gold'?'#d97706':g==='Silver'?'#4b5563':g==='Bronze'?'#b45309':'#7c3aed';
  const gradeLabel = (g) => ({ Gold:t.gold, Silver:t.silver, Bronze:t.bronze, Participant:t.participant }[g] || g);

  return (
    <div className="progress-screen">
      <div className="dash-header">
        <button className="back-btn" onClick={onBack}>{t.back}</button>
        <div className="dash-header-title">
          <span style={{fontSize:'1.1rem'}}>📊</span>
          <h2 className="dash-title">{studentName}</h2>
        </div>
        <button className="lang-toggle-sm" onClick={toggleLang}>{t.language}</button>
      </div>

      {/* Redeem modal */}
      {redeemId && (
        <div className="overlay">
          <div className="modal-box">
            <div style={{fontSize:'2.5rem'}}>🔐</div>
            <h3 style={{marginBottom:'8px'}}>{t.redeemPrompt}</h3>
            <input type="password" className="form-input" placeholder={t.redeemPin}
              value={pin} onChange={e=>{setPin(e.target.value);setPinErr('');}}
              maxLength={8} style={{textAlign:'center',letterSpacing:'6px',fontSize:'1.3rem'}}
            />
            {pinErr && <div style={{color:'#dc2626',fontWeight:700,marginTop:'6px'}}>{pinErr}</div>}
            {pinOk  && <div style={{color:'#16a34a',fontWeight:700,marginTop:'6px'}}>{pinOk}</div>}
            <div className="confirm-btns" style={{marginTop:'14px'}}>
              <button className="btn-yes" onClick={handleRedeem}>{t.redeemConfirm}</button>
              <button className="btn-cancel" onClick={()=>{setRedeemId(null);setPin('');setPinErr('');}}>
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="dash-loading"><div className="kangaroo-bounce">🦘</div><p>{t.loading}</p></div>
      ) : !data ? (
        <div className="dash-loading"><p>⚠️ Error loading data</p></div>
      ) : (
        <div className="dash-content">

          {/* Quarter progress */}
          <div className="dash-section">
            <h3 className="dash-section-title">🗓️ {t.quarterProgress} — {data.quarter}</h3>
            <div className="quarter-bar-wrap">
              <div className="quarter-bar" style={{width:`${data.progress_pct}%`}}/>
              <div className="quarter-bar-labels">
                <span>{t.sessionsLabel(data.sessions_done)}</span>
                <span>{data.sessions_done}/{SESSIONS_NEEDED}</span>
              </div>
            </div>
            <p style={{fontSize:'0.85rem',color:'#64748b',marginTop:'6px'}}>
              {data.sessions_done >= SESSIONS_NEEDED
                ? (lang==='en'?'✅ Quarter complete! Check your voucher below.':'✅ Hoàn thành quý! Xem phiếu thưởng bên dưới.')
                : t.sessionsNeeded(SESSIONS_NEEDED - data.sessions_done)}
            </p>
            <div className="stat-cards" style={{marginTop:'12px'}}>
              <div className="stat-card"><div className="stat-icon">📝</div><div className="stat-num">{data.total_tests}</div><div className="stat-label">{t.totalTests}</div></div>
              <div className="stat-card gold-card"><div className="stat-icon">🏆</div><div className="stat-num">{data.q_best}%</div><div className="stat-label">{t.quarterBest}</div></div>
              <div className="stat-card"><div className="stat-icon">📊</div><div className="stat-num">{data.q_avg}%</div><div className="stat-label">{t.quarterAvg}</div></div>
              <div className="stat-card"><div className="stat-icon">✅</div><div className="stat-num">{data.total_correct}</div><div className="stat-label">{t.totalCorrect}</div></div>
            </div>
          </div>

          {/* Vouchers */}
          <div className="dash-section">
            <h3 className="dash-section-title">🎁 {t.vouchersSection}</h3>
            {data.vouchers.length === 0 ? (
              <p style={{color:'#64748b',fontSize:'0.9rem'}}>{t.noVouchers}</p>
            ) : (
              <div style={{display:'flex',flexDirection:'column',gap:'10px'}}>
                {[...data.vouchers].reverse().map(v => (
                  <div key={v.id} className={`voucher-card ${v.redeemed?'voucher-redeemed':''}`}>
                    <div className="voucher-left">
                      <div className="voucher-icon">{v.redeemed?'✓':'🎟️'}</div>
                      <div>
                        <div className="voucher-amount">300,000 VND</div>
                        <div className="voucher-quarter">{v.quarter}</div>
                        <div className="voucher-date">{t.voucherEarned}: {v.earned_date}</div>
                        {v.redeemed && <div style={{color:'#16a34a',fontSize:'0.78rem',fontWeight:700}}>{t.voucherRedeemed} {v.redeemed_date}</div>}
                      </div>
                    </div>
                    {!v.redeemed && (
                      <button className="redeem-btn" onClick={()=>{setRedeemId(v.id);setPin('');setPinErr('');}}>
                        🔐 {t.redeemBtn}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent sessions */}
          <div className="dash-section">
            <h3 className="dash-section-title">🕐 {t.recentSessions}</h3>
            {data.trend.length === 0 ? (
              <p style={{color:'#64748b',fontSize:'0.9rem'}}>{t.noHistory || 'No sessions yet.'}</p>
            ) : (
              <div style={{display:'flex',flexDirection:'column',gap:'8px'}}>
                {[...data.trend].reverse().map((s,i) => (
                  <div key={i} className="history-item">
                    <div className="hi-left">
                      <span className="hi-grade" style={{
                        background: gradeColor(s.grade_label)+'22',
                        color: gradeColor(s.grade_label),
                        border:`1.5px solid ${gradeColor(s.grade_label)}44`
                      }}>
                        {gradeLabel(s.grade_label)}
                      </span>
                      <div className="hi-meta">
                        <span className="hi-date">{s.date}</span>
                        <span className="hi-time">✅{s.pass} ❌{s.fail} ⏭{s.skip}</span>
                      </div>
                    </div>
                    <div className="hi-right">
                      <span style={{fontFamily:'Baloo 2',fontWeight:900,fontSize:'1.1rem',color:gradeColor(s.grade_label)}}>{s.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
