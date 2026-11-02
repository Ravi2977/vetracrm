const SPREADSHEET_ID = '1vzDqVQTBJw0LiaILdkiZd_Rw8rdNQinBpf1x2c3SB9w';
const SHEET_GID = 0;
const SHEET_NAME = 'Website Leads';
const HEADERS = [
  'Submitted at',
  'Full name',
  'Business name',
  'Work email',
  'Mobile number',
  'Business type',
  'Interested in',
  'Message',
  'Page URL',
];

function setupSheet() {
  const sheet = getLeadSheet_();
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return 'Sheet is ready: ' + SHEET_NAME;
}

function doGet() {
  try {
    const spreadsheet = openLeadSpreadsheet_();
    const sheet = spreadsheet.getSheets().find((item) => item.getSheetId() === SHEET_GID)
      || spreadsheet.getSheetByName(SHEET_NAME);
    return jsonOutput_({
      ok: true,
      message: 'Vetra CRM lead endpoint is ready.',
      sheetName: sheet ? sheet.getName() : '',
      sheetExists: Boolean(sheet),
      sheetId: sheet ? sheet.getSheetId() : null,
      rows: sheet ? Math.max(0, sheet.getLastRow() - 1) : 0,
    });
  } catch (error) {
    console.error(error);
    return jsonOutput_({
      ok: false,
      error: 'Cannot access the configured Google Sheet. Check SPREADSHEET_ID and authorize the script.',
    });
  }
}

function doPost(e) {
  try {
    const data = parseRequestData_(e);

    // Silently discard bot submissions that fill the hidden honeypot field.
    if (cleanText_(data.website, 200)) {
      return jsonOutput_({ ok: true });
    }

    const submittedAt = cleanText_(data['Submitted at'], 100) || new Date();
    const name = cleanText_(data['Full name'], 120);
    const business = cleanText_(data['Business name'], 160);
    const email = cleanText_(data['Work email'], 254).toLowerCase();
    const phone = cleanText_(data['Mobile number'], 40);
    const businessType = cleanText_(data['Business type'], 120);
    const interest = cleanText_(data['Interested in'], 120);
    const message = cleanText_(data['Message'], 5000);
    const pageUrl = cleanText_(data['Page URL'], 1000);

    if (!name || !business || !businessType || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return jsonOutput_({ ok: false, error: 'Please provide the required contact details.' });
    }

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const sheet = getLeadSheet_();
      if (sheet.getLastRow() === 0) {
        sheet.appendRow(HEADERS);
        sheet.setFrozenRows(1);
      }
      const row = [
        submittedAt instanceof Date ? submittedAt : safeCell_(submittedAt),
        safeCell_(name),
        safeCell_(business),
        safeCell_(email),
        safeCell_(phone),
        safeCell_(businessType),
        safeCell_(interest),
        safeCell_(message),
        safeCell_(pageUrl),
      ];
      sheet.appendRow(row);
    } finally {
      lock.releaseLock();
    }

    return jsonOutput_({ ok: true });
  } catch (error) {
    console.error(error);
    return jsonOutput_({ ok: false, error: 'Could not write to the Sheet. Check the Sheet ID, tab access and Apps Script execution log.' });
  }
}

function openLeadSpreadsheet_() {
  if (!SPREADSHEET_ID) {
    throw new Error('SPREADSHEET_ID is required.');
  }
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function getLeadSheet_() {
  const spreadsheet = openLeadSpreadsheet_();
  const targetSheet = spreadsheet.getSheets().find((sheet) => sheet.getSheetId() === SHEET_GID);
  return targetSheet || spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
}

function parseRequestData_(e) {
  const rawBody = e && e.postData && e.postData.contents;
  if (rawBody) {
    try {
      return JSON.parse(rawBody);
    } catch (error) {
      throw new Error('Request body must contain valid JSON.');
    }
  }
  return (e && e.parameter) || {};
}

function cleanText_(value, maxLength) {
  return String(value || '')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
    .trim()
    .slice(0, maxLength);
}

function safeCell_(value) {
  const text = String(value || '');
  return /^[=+\-@]/.test(text) ? "'" + text : text;
}

function jsonOutput_(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
