// 可用日期列表
window.availableDates = [
  {id: '20251212', display: '2025-12-12', file: 'history/picks_20251212.json'},
  {id: '20251226', display: '2025-12-26', file: 'history/picks_20251226.json'},
  {id: '20251231', display: '2025-12-31', file: 'history/picks_20251231.json'},
];

// 默认选中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[window.availableDates.length - 1].id;
}
