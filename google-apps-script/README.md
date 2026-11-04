# Connect the Vetra enquiry form to Google Sheets

## 1. Prepare the Sheet

The website enquiry Sheet ID is already set in `Code.gs`, and the script targets the first tab (`gid=0`) from the shared Sheet URL.

## 2. Add the Apps Script

1. Open [script.google.com](https://script.google.com) and create a project.
2. Replace the editor contents with `Code.gs` from this folder.
3. If you use a different Sheet, change `SPREADSHEET_ID` and `SHEET_GID` in `Code.gs`.
4. Select `setupSheet` in the function picker and run it once. Review and grant the requested Google Sheets permission. This adds the headers if the first tab is empty.

## 3. Deploy the form endpoint

1. Select **Deploy → New deployment → Web app**.
2. Set **Execute as** to your Google account so the script can write to your Sheet.
3. Set access to **Anyone** so visitors can submit without signing into Google, then deploy and approve the requested access.
4. Copy the deployment URL ending in `/exec`.

## 4. Connect the website

The website now submits each enquiry to the Vetra CRM leads webhook first. After the CRM accepts it, the form also attempts a best-effort copy to the deployed `/exec` URL configured in `script.js`. The Sheet backup uses these keys (as `text/plain` to avoid a browser CORS preflight): `Full name`, `Business name`, `Work email`, `Mobile number`, `Business type`, `Interested in`, `Message`, and `Page URL`; Apps Script fills `Submitted at` automatically. City and state are sent to Vetra CRM, but are not included in the existing Sheet columns. The page reports success when Vetra CRM accepts the lead; a Sheet backup failure does not undo the CRM submission.

Open the `/exec` URL in a browser to run the `doGet` health check. A working deployment returns JSON with `"ok": true`; `"sheetExists": false` means run `setupSheet` once. If you change `Code.gs`, copy the updated file into the Apps Script editor and deploy a new version from **Deploy → Manage deployments → Edit → Version: New version → Deploy**.

The public endpoint is meant only for this contact form. Keep the script limited to appending validated form fields; do not add sensitive spreadsheet data or expose OAuth tokens in the website code.

## If the form fails or the Sheet stays empty

A `401` usually means the web app is asking the visitor to sign in. In Apps Script, open **Deploy → Manage deployments**, edit the web app deployment, and set **Execute as** to your account and **Who has access** to **Anyone** (not **Anyone with Google account**). Save the deployment, then copy its current `/exec` URL into `script.js` if it changed.

Google's web app deployment settings determine whether visitors can call `doPost` without signing in. See the [Apps Script web app deployment guide](https://developers.google.com/apps-script/guides/web#deploy_a_script_as_a_web_app).


If the page reports a Google response/CORS error, confirm the web app is deployed for **Anyone**, then publish a new deployment version. Check **Apps Script → Executions** for the matching `doPost` run and its error. If the page reports that it cannot access the Sheet, verify `SPREADSHEET_ID` in the deployed `Code.gs`, run `setupSheet` to grant access, and redeploy.
