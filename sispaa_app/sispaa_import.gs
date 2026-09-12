function importFromGitHub() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  if (!sheet) sheet = SpreadsheetApp.getActiveSheet();
  
  var csvUrl = 'https://raw.githubusercontent.com/bursasearch/myx_shop/main/sispaa_export.csv';
  
  try {
    var response = UrlFetchApp.fetch(csvUrl);
    var csvData = response.getContentText();
    var rows = Utilities.parseCsv(csvData);
    
    if (rows.length === 0) { 
      Logger.log('CSV kosong!'); 
      return; 
    }
    
    sheet.clear();
    sheet.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
    sheet.autoResizeColumns(1, rows[0].length);
    
    var headerRange = sheet.getRange(1, 1, 1, rows[0].length);
    headerRange.setBackground('#0d47a1');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    
    Logger.log('Import selesai! ' + (rows.length - 1) + ' baris.');
  } catch (e) {
    Logger.log('Error: ' + e.toString());
  }
}

function createTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(t) { ScriptApp.deleteTrigger(t); });
  
  ScriptApp.newTrigger('importFromGitHub')
    .timeBased().everyMinutes(30).create();
  
  Logger.log('Auto-trigger created: every 30 minutes');
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('SISPAA')
    .addItem('Import Sekarang', 'importFromGitHub')
    .addItem('Setup Auto-Import', 'createTrigger')
    .addToUi();
}
