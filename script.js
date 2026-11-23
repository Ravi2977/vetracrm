const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#nav-menu');

menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  menuButton.setAttribute('aria-label', isOpen ? 'Open navigation' : 'Close navigation');
  menu?.classList.toggle('open', !isOpen);
});

menu?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  menu.classList.remove('open');
  menuButton?.setAttribute('aria-expanded', 'false');
  menuButton?.setAttribute('aria-label', 'Open navigation');
}));

const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

// Deployed Google Apps Script Web App endpoint.
const GOOGLE_SHEETS_WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbyvoKnzxBZX57sl4nRGlbBv4NuigQNfS2mWWL-xtb0thJJzdWSkGPWxrVmPXLKgF9fj/exec';
// Public Vetra CRM webhook URL for website enquiries.
const VETRA_CRM_LEADS_API_URL = 'https://api.vetracrm.in/api/v1/webhooks/leads/custom/5e45385cd6f94968be4c08920235ba50cb6069c816e448f8a9e677aa8f2b449f';

function createSourceLeadId() {
  const uniquePart = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
  return `vetracrm-website-${uniquePart}`;
}
/* ---------------------------------------------------------------------------
   Lead popup (har page par landing ke time). Left: heading + benefits + product image,
   right: form. Submit wahi same CRM + Google Sheet flow se hota hai (neeche).
   OFFER_END ke baad offer wali lines apne aap hatt jaati hain, popup "free demo" ban jaata hai.
--------------------------------------------------------------------------- */
const OFFER_END = Date.parse('2026-12-26T00:00:00+05:30');
const offerActive = Date.now() < OFFER_END;
const OFFER_INTEREST = 'Christmas offer (20% off subscription + setup)';
const pageForm = document.querySelector('#contact-form');
const pageInterest = pageForm?.querySelector('[name="interest"]');
const interestOptions = pageInterest
  ? [...pageInterest.options].filter((o) => o.value !== '').map((o) => o.text)
  : [OFFER_INTEREST, 'Cloud CRM: Starter plan', 'Cloud CRM: Growth plan', 'Cloud CRM: Pro plan', 'Self-hosted CRM (on my own server)', 'Not sure yet, help me choose'];
// Product/service page par wahi interest pehle se select (warna offer ya "help me choose")
const pageDefault = pageInterest?.querySelector('option[selected]:not([value=""])')?.text;
const popupDefault = pageDefault || (offerActive ? OFFER_INTEREST : 'Not sure yet, help me choose');
const escapeHtml = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const offerDialog = document.createElement('dialog');
offerDialog.className = 'lead-pop';
offerDialog.setAttribute('aria-labelledby', 'lead-pop-title');
offerDialog.innerHTML = `
  <button class="offer-close" type="button" aria-label="Close">×</button>
  <div class="lp-side">
    ${offerActive ? '<span class="lp-badge"><b>20% OFF</b> Christmas offer · till 25 Dec</span>' : '<span class="lp-badge"><b>FREE</b> Demo · no obligation</span>'}
    <h2 id="lead-pop-title">${offerActive ? 'Get 20% off + a free demo' : 'See Vetra in a free demo'}</h2>
    <p>Software that runs your business, from first lead to final bill. Tell us what you need and we'll call you back.</p>
    <ul class="lp-points">
      <li>Free demo with your kind of data</li>
      <li>Clear written quote, no hidden costs</li>
      <li>Setup, training &amp; support included</li>
    </ul>
    <div class="lp-shot" aria-hidden="true">
      <img src="/assets/media/product-screen-01.jpg" alt="" width="1440" height="810" loading="lazy" decoding="async">
      <span class="screen-redaction screen-redaction-profile"></span><span class="screen-redaction screen-redaction-greeting"></span>
    </div>
  </div>
  <form class="contact-form lp-form" name="popup-enquiry" method="POST" data-lead-source="Popup form">
    <p class="hidden-field"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <div class="form-heading"><h3>Get a call back</h3><p>Takes 20 seconds. Fields marked * are required.</p></div>
    <div class="form-grid">
      <label class="form-full">Full name <em>*</em><input required name="name" autocomplete="name" placeholder="Your name"></label>
      <label class="form-full">Mobile / WhatsApp <em>*</em><input required type="tel" name="phone" autocomplete="tel" inputmode="tel" pattern="[0-9+\\s\\-]{10,15}" title="Enter a valid mobile number, 10 to 15 digits" placeholder="+91 98765 43210"></label>
      <label class="form-full">Work email <em>*</em><input required type="email" name="email" autocomplete="email" placeholder="you@company.com"></label>
      <label>Business name <em>*</em><input required name="business" autocomplete="organization" placeholder="Your business"></label>
      <label>Interested in <select name="interest">${interestOptions.map((t) => `<option${t === popupDefault ? ' selected' : ''}>${escapeHtml(t)}</option>`).join('')}</select></label>
    </div>
    <button class="btn btn-primary lp-submit" type="submit">${offerActive ? 'Claim my 20% offer' : 'Book my free demo'}</button>
    <p class="lp-legal">We'll only contact you about your enquiry. <a href="/privacy.html">Privacy notice</a>.</p>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
`;
document.body.append(offerDialog);

const contactForms = [...document.querySelectorAll('.contact-form')];
const claimOfferFromUrl = new URLSearchParams(window.location.search).get('offer') === 'xmas20';

contactForms.forEach((contactForm) => {
  const contactStatus = contactForm.querySelector('.form-status');
  const interestSelect = contactForm.querySelector('[name="interest"]');
  if (claimOfferFromUrl && interestSelect) interestSelect.value = 'Christmas offer (20% off subscription + setup)';

  contactForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!contactForm.reportValidity()) return;

    const submitButton = contactForm.querySelector('button[type="submit"]');
    const submitLabel = submitButton.innerHTML;
    const formData = new FormData(contactForm);
    if (formData.get('website')) {
      contactForm.reset();
      return;
    }
    const pageUrl = ['localhost', '127.0.0.1'].includes(window.location.hostname)
      ? `https://vetracrm.in${window.location.pathname}`
      : `${window.location.origin}${window.location.pathname}`;
    const businessType = String(formData.get('business_type') || '').trim();
    const customerMessage = String(formData.get('message') || '').trim();
    const urlParams = new URLSearchParams(window.location.search);
    const utm = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
      .map((k) => (urlParams.get(k) ? `${k}=${urlParams.get(k)}` : '')).filter(Boolean).join(', ');
    const contextLines = [
      businessType ? `Business type: ${businessType}` : '',
      `Lead form: ${contactForm.dataset.leadSource || 'Page form'}`,
      `Website page: ${pageUrl}`,
      utm ? `Campaign: ${utm}` : '',
    ].filter(Boolean);
    const sourceLeadId = contactForm.dataset.sourceLeadId || createSourceLeadId();
    contactForm.dataset.sourceLeadId = sourceLeadId;
    const crmPayload = {
      lead_id: sourceLeadId,
      name: String(formData.get('name') || '').trim(),
      email: String(formData.get('email') || '').trim(),
      phone: String(formData.get('phone') || '').trim(),
      company: String(formData.get('business') || '').trim(),
      subject: String(formData.get('interest') || '').trim() || 'Vetra CRM enquiry',
      message: [customerMessage, ...contextLines].filter(Boolean).join('\n\n'),
      city: String(formData.get('city') || '').trim(),
      state: String(formData.get('state') || '').trim(),
    };
    const sheetsPayload = {
      'Full name': formData.get('name') || '',
      'Business name': formData.get('business') || '',
      'Work email': formData.get('email') || '',
      'Mobile number': formData.get('phone') || '',
      'Business type': businessType,
      'Interested in': formData.get('interest') || '',
      'Message': customerMessage,
      'Page URL': pageUrl,
    };
    if (formData.get('website')) sheetsPayload.website = formData.get('website');

    submitButton.disabled = true;
    submitButton.textContent = 'Sending…';
    contactStatus.textContent = 'Sending your enquiry…';
    contactStatus.classList.remove('is-error', 'is-success');

    try {
      const response = await fetch(VETRA_CRM_LEADS_API_URL, {
        method: 'POST',
        credentials: 'omit',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(crmPayload),
      });
      const responseText = await response.text();
      let result = {};
      try {
        result = responseText ? JSON.parse(responseText) : {};
      } catch {
        result = { message: responseText.trim() };
      }

      const responseStatus = String(result.status || '').toLowerCase();
      const explicitFailure = result.ok === false
        || result.success === false
        || ['error', 'failed', 'failure'].includes(responseStatus)
        || Boolean(result.error);
      if (!response.ok || explicitFailure) {
        throw new Error(result.error || result.message || `CRM webhook returned HTTP ${response.status}.`);
      }

      // Keep the existing Sheet as a best-effort backup after the CRM accepts the lead.
      try {
        await fetch(GOOGLE_SHEETS_WEB_APP_URL, {
          method: 'POST',
          mode: 'cors',
          redirect: 'follow',
          credentials: 'omit',
          headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
          body: JSON.stringify(sheetsPayload),
        });
      } catch (sheetError) {
        console.warn('CRM accepted the lead, but the Google Sheets backup could not be reached.', sheetError);
      }

      contactForm.reset();
      delete contactForm.dataset.sourceLeadId;
      contactStatus.textContent = 'Thank you. Your enquiry has been sent to the Vetra CRM team.';
      contactStatus.classList.add('is-success');
      contactForm.dispatchEvent(new CustomEvent('vetra:lead', { bubbles: true }));
    } catch (error) {
      contactStatus.textContent = error instanceof TypeError
        ? 'We could not reach the Vetra CRM service. Please check your connection and try again.'
        : (error.message || 'We could not send your enquiry. Please try again.');
      contactStatus.classList.add('is-error');
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = submitLabel;
    }
  });
});

/* ---------------------------------------------------------------------------
   Popup kab dikhe:
   - kisi bhi page par landing ke time (contact/thanks/privacy/404 chhod kar)
   - desktop: ~1.5s baad, mobile: ~4s baad bottom sheet (Google ki mobile popup guideline ke liye)
   - close kiya => 24 ghante nahi; form bhar diya => 30 din nahi
   - ek tab-session me sirf ek baar
   - ?popup=1 URL me ho to hamesha dikhe (testing ke liye)
--------------------------------------------------------------------------- */
const POPUP_KEY = 'vetraLeadPopup';
const DAY = 24 * 60 * 60 * 1000;
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage blocked */ } },
  session(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch { return null; } return null; },
};
const track = (name, params = {}) => { if (window.gtag) window.gtag('event', name, params); };

function closePopup(reason) {
  if (!offerDialog.open) return;
  offerDialog.close(reason);
}
offerDialog.querySelector('.offer-close').addEventListener('click', () => closePopup('dismiss'));
offerDialog.addEventListener('click', (event) => {
  if (event.target === offerDialog) closePopup('dismiss');   // backdrop click
});
offerDialog.addEventListener('close', () => {
  if (offerDialog.returnValue !== 'lead') {
    store.set(POPUP_KEY, { until: Date.now() + DAY });
    track('popup_close', { page: location.pathname });
  }
});
document.addEventListener('vetra:lead', (event) => {
  // Kisi bhi form se lead aayi => 30 din tak popup nahi
  store.set(POPUP_KEY, { until: Date.now() + 30 * DAY, submitted: true });
  if (event.target === offerDialog.querySelector('form')) {
    track('generate_lead', { form: 'popup' });
    setTimeout(() => closePopup('lead'), 2500);
  }
});

(function maybeShowPopup() {
  const path = location.pathname;
  const excluded = ['/contact/', '/thanks.html', '/privacy.html', '/404.html'].includes(path)
    || document.title.startsWith('Page not found');
  const forced = new URLSearchParams(location.search).get('popup') === '1';
  const saved = store.get(POPUP_KEY);
  const snoozed = saved && saved.until > Date.now();
  const shownThisSession = store.session(POPUP_KEY) === '1';
  if (!forced && (excluded || snoozed || shownThisSession)) return;

  const mobile = window.matchMedia('(max-width: 680px)').matches;
  setTimeout(() => {
    // User kisi aur form me type kar raha ho ya koi dialog khula ho to disturb mat karo
    const active = document.activeElement;
    if (!forced && active && active.closest && active.closest('form')) return;
    if (document.querySelector('dialog[open]')) return;
    offerDialog.showModal();
    store.session(POPUP_KEY, '1');
    track('popup_view', { page: path, device: mobile ? 'mobile' : 'desktop' });
  }, mobile ? 4000 : 1500);
})();
