// date_config.js - 自动生成
// 生成时间: $(date '+%Y-%m-%d %H:%M:%S')

window.availableDates = [
  {id: '20260202', display: '2026-02-02', file: 'history/picks_20260202.json'},
];

// 默认选中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[0].id;
    window.latestDate = window.availableDates[0];
}

// 获取数据文件路径
window.getDataFilePath = function(dateId) {
    const date = window.availableDates.find(d => d.id === dateId);
    return date ? date.file : null;
};

// 获取日期显示名称
window.getDateDisplay = function(dateId) {
    const date = window.availableDates.find(d => d.id === dateId);
    return date ? date.display : dateId;
};

console.log('✅ date_config.js 已加载');
console.log('📅 可用日期:', window.availableDates.length);
