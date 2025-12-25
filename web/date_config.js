// 可用日期列表
window.availableDates = [
  {id: '20251215', display: '2025-12-15', file: 'history/picks_20251215.json'},
  {id: '20251216', display: '2025-12-16', file: 'history/picks_20251216.json'},
  {id: '20251217', display: '2025-12-17', file: 'history/picks_20251217.json'},
  {id: '20251218', display: '2025-12-18', file: 'history/picks_20251218.json'},
  {id: '20251220', display: '2025-12-20', file: 'history/picks_20251220.json'},
  {id: '20251221', display: '2025-12-21', file: 'history/picks_20251221.json'},
  {id: '20251222', display: '2025-12-22', file: 'history/picks_20251222.json'},
];

// 默认选中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[window.availableDates.length - 1].id;
}
