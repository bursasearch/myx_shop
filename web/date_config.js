// 可用日期列表 - 自動生成 $(date '+%Y-%m-%d %H:%M:%S')
window.availableDates = [
  {id: '20251221', display: '2025-12-21', file: 'history/picks_20251221.json'},
  {id: '20251222', display: '2025-12-22', file: 'history/picks_20251222.json'},
  {id: '20251223', display: '2025-12-23', file: 'history/picks_20251223.json'},
  {id: '20251224', display: '2025-12-24', file: 'history/picks_20251224.json'},
  {id: '20251226', display: '2025-12-26', file: 'history/picks_20251226.json'},
  {id: '20251229', display: '2025-12-29', file: 'history/picks_20251229.json'},
  {id: '20251230', display: '2025-12-30', file: 'history/picks_20251230.json'},
  {id: '20251231', display: '2025-12-31', file: 'history/picks_20251231.json'},
  {id: '20260102', display: '2026-01-02', file: 'history/picks_20260102.json'},
  {id: '20260104', display: '2026-01-04', file: 'history/picks_20260104.json'},
  {id: '20260105', display: '2026-01-05', file: 'history/picks_20260105.json'},
];

// 默認選中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[window.availableDates.length - 1].id;
    window.latestDate = window.availableDates[window.availableDates.length - 1];
}

// 獲取日期顯示名稱
window.getDateDisplay = function(dateId) {
    const date = window.availableDates.find(d => d.id === dateId);
    return date ? date.display : dateId;
};

// 檢查日期是否存在
window.isDateAvailable = function(dateId) {
    return window.availableDates.some(d => d.id === dateId);
};
