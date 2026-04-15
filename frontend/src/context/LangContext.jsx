import React, { createContext, useContext, useState } from 'react';

const T = {
  en: {
    appTitle: "IKMC Math Practice", appSubtitle: "International Kangaroo Mathematics Contest",
    // Login
    welcomeBack: "Welcome!", enterName: "Enter your name", namePlaceholder: "Your name...",
    selectGrade: "Select Grade", selectQuestions: "Number of Questions",
    startTest: "Start Test", viewProgress: "My Progress",
    gradeLabel: g => `Grade ${g}`,
    // Quiz
    question: "Question", of: "of", timeLeft: "Time Left",
    nextQuestion: "Next →", prevQuestion: "← Back",
    submitTest: "Submit Test", confirmSubmit: "Submit your answers?",
    yes: "Yes, Submit", cancel: "Cancel",
    autoSkip: "Time's up for this question!",
    timeUp: "Time's Up!", timeUpMsg: "Your test has been submitted automatically.",
    skipped: "Skipped",
    // Levels
    easy: "Easy", medium: "Medium", hard: "Hard",
    // Results
    results: "Test Results", yourScore: "Your Score",
    passLabel: "✅ Pass", failLabel: "❌ Fail", skipLabel: "⏭ Skip",
    gold: "🥇 Gold", silver: "🥈 Silver", bronze: "🥉 Bronze", participant: "🎖 Participant",
    excellent: "Outstanding! IKMC Champion! 🎉", great: "Great work! Keep going! 🌟",
    good: "Good effort! Practice makes perfect!", keepTrying: "Don't give up! You can do it! 💪",
    newVoucher: "🎁 You earned a voucher!",
    voucherValue: "300,000 VND reward!",
    tryAgain: "Try Again", reviewAnswers: "Review Answers", backToResults: "← Results",
    correct: "Correct", incorrect: "Wrong",
    explanation: "Explanation",
    loading: "Loading...", error: "Cannot connect to server. Is Python running on port 5000?",
    retry: "Retry",
    language: "🇻🇳 Tiếng Việt",
    // Progress / Dashboard
    myProgress: "My Progress", back: "← Back",
    quarterProgress: "Quarter Progress", sessionsLabel: s => `${s} sessions completed`,
    sessionsNeeded: n => `${n} sessions to earn voucher`,
    quarterBest: "Quarter Best", quarterAvg: "Quarter Average",
    totalTests: "Total Tests", totalCorrect: "Total Correct",
    recentSessions: "Recent Sessions", vouchersSection: "My Vouchers",
    noVouchers: "No vouchers yet. Complete 12 sessions this quarter!",
    voucherEarned: "Earned", voucherRedeemed: "✓ Redeemed",
    redeemBtn: "Redeem (Parent)", redeemPrompt: "Enter parent PIN to redeem:",
    redeemPin: "Parent PIN", redeemConfirm: "Confirm Redeem",
    redeemSuccess: "Voucher redeemed! 🎉", redeemError: "Incorrect PIN",
    passShort: "P", failShort: "F", skipShort: "S",
    timeTaken: "Time", mins: "m", secs: "s",
    topic: "Topic",
  },
  vi: {
    appTitle: "Luyện Thi Toán Kangaroo", appSubtitle: "Kỳ thi Toán Quốc tế Kangaroo (IKMC)",
    welcomeBack: "Xin chào!", enterName: "Nhập tên của bạn", namePlaceholder: "Tên bạn...",
    selectGrade: "Chọn Khối Lớp", selectQuestions: "Số Câu Hỏi",
    startTest: "Bắt Đầu Làm Bài", viewProgress: "Tiến Trình",
    gradeLabel: g => `Lớp ${g}`,
    question: "Câu", of: "trong", timeLeft: "Thời Gian",
    nextQuestion: "Tiếp →", prevQuestion: "← Trước",
    submitTest: "Nộp Bài", confirmSubmit: "Xác nhận nộp bài?",
    yes: "Có, Nộp", cancel: "Hủy",
    autoSkip: "Hết giờ cho câu này!",
    timeUp: "Hết Giờ!", timeUpMsg: "Bài thi đã được nộp tự động.",
    skipped: "Bỏ qua",
    easy: "Dễ", medium: "Trung bình", hard: "Khó",
    results: "Kết Quả Bài Thi", yourScore: "Điểm Của Bạn",
    passLabel: "✅ Đúng", failLabel: "❌ Sai", skipLabel: "⏭ Bỏ qua",
    gold: "🥇 Vàng", silver: "🥈 Bạc", bronze: "🥉 Đồng", participant: "🎖 Tham Dự",
    excellent: "Xuất sắc! Sẵn sàng thi IKMC! 🎉", great: "Giỏi lắm! Tiếp tục nào! 🌟",
    good: "Cố gắng tốt! Luyện tập thêm nhé!", keepTrying: "Đừng nản! Bạn làm được! 💪",
    newVoucher: "🎁 Bạn nhận được phiếu thưởng!",
    voucherValue: "Phần thưởng 300.000 VND!",
    tryAgain: "Làm Lại", reviewAnswers: "Xem Đáp Án", backToResults: "← Kết Quả",
    correct: "Đúng", incorrect: "Sai",
    explanation: "Giải thích",
    loading: "Đang tải...", error: "Không kết nối được máy chủ. Python có đang chạy cổng 5000 không?",
    retry: "Thử Lại",
    language: "🇬🇧 English",
    myProgress: "Tiến Trình", back: "← Quay Lại",
    quarterProgress: "Tiến Trình Quý", sessionsLabel: s => `${s} buổi đã hoàn thành`,
    sessionsNeeded: n => `Cần ${n} buổi để nhận phiếu thưởng`,
    quarterBest: "Điểm Cao Nhất Quý", quarterAvg: "Điểm TB Quý",
    totalTests: "Tổng Số Bài", totalCorrect: "Tổng Câu Đúng",
    recentSessions: "Bài Làm Gần Đây", vouchersSection: "Phiếu Thưởng",
    noVouchers: "Chưa có phiếu. Hoàn thành 12 buổi trong quý để nhận thưởng!",
    voucherEarned: "Ngày nhận", voucherRedeemed: "✓ Đã đổi",
    redeemBtn: "Đổi Thưởng (Phụ huynh)", redeemPrompt: "Nhập mã PIN phụ huynh để đổi thưởng:",
    redeemPin: "Mã PIN Phụ Huynh", redeemConfirm: "Xác Nhận Đổi",
    redeemSuccess: "Đổi thưởng thành công! 🎉", redeemError: "Mã PIN không đúng",
    passShort: "Đ", failShort: "S", skipShort: "B",
    timeTaken: "Thời gian", mins: "phút", secs: "giây",
    topic: "Chủ đề",
  }
};

const LangContext = createContext();
export function LangProvider({ children }) {
  const [lang, setLang] = useState('en');
  const t = T[lang];
  const toggleLang = () => setLang(l => l === 'en' ? 'vi' : 'en');
  return <LangContext.Provider value={{ lang, t, toggleLang }}>{children}</LangContext.Provider>;
}
export const useLang = () => useContext(LangContext);
