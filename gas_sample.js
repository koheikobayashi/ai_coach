/**
 * GAS (Google Apps Script) サンプルコード
 *
 * 使い方:
 * 1. Google スプレッドシートを作成
 * 2. 拡張機能 → Apps Script を開く
 * 3. このコードを貼り付けてデプロイ (ウェブアプリとして)
 * 4. デプロイURLを .env の GAS_POST_URL / GAS_GET_URL に設定
 *
 * スプレッドシートの列: A:user, B:date, C:exercise, D:sets, E:weight, F:reps, G:memo, H:created_at
 */

const SHEET_NAME = 'records';

function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) {
      return ContentService.createTextOutput(
        JSON.stringify({ error: 'Sheet not found' })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    const data = JSON.parse(e.postData.contents);
    sheet.appendRow([
      data.user,
      data.date,
      data.exercise,
      data.sets,
      data.weight,
      data.reps,
      data.memo,
      new Date().toISOString(),
    ]);

    return ContentService.createTextOutput(
      JSON.stringify({ status: 'ok' })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ error: err.message })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) {
      return ContentService.createTextOutput(
        JSON.stringify([])
      ).setMimeType(ContentService.MimeType.JSON);
    }

    const rows = sheet.getDataRange().getValues();
    const user = e.parameter.user || '';

    // 1行目はヘッダーとしてスキップ可能（ヘッダーがない場合は0から）
    const records = [];
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      if (user && row[0] !== user) continue;
      records.push({
        user: row[0],
        date: row[1],
        exercise: row[2],
        sets: row[3],
        weight: row[4],
        reps: row[5],
        memo: row[6],
        created_at: row[7],
      });
    }

    // 新しい順に並べ替え
    records.sort((a, b) => (b.date > a.date ? 1 : -1));

    return ContentService.createTextOutput(
      JSON.stringify(records)
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ error: err.message })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
