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
const offerDialog = document.createElement('dialog');
offerDialog.className = 'diwali-offer-dialog';
offerDialog.setAttribute('aria-labelledby', 'diwali-offer-title');
offerDialog.innerHTML = `
  <button class="offer-close" type="button" aria-label="Close offer form">×</button>
  <div class="offer-kicker"><span aria-hidden="true">✦</span> DIWALI SPECIAL <b>20% OFF</b></div>
  <h2 id="diwali-offer-title">Get your Vetra CRM offer</h2>
  <p class="offer-intro">Get 20% off the Vetra CRM monthly subscription and one-time setup. Share your details and our team will confirm offer validity and the discounted quote.</p>
  <form class="contact-form offer-form" name="offer-enquiry" method="POST">
    <p class="hidden-field"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
    <div class="form-grid">
      <label>Full name <em>*</em><input required name="name" autocomplete="name" placeholder="Your name"></label>
      <label>Business name <em>*</em><input required name="business" autocomplete="organization" placeholder="Your business"></label>
      <label>Work email <em>*</em><input required type="email" name="email" autocomplete="email" placeholder="you@company.com"></label>
      <label>Mobile number <span class="optional">Optional</span><input type="tel" name="phone" autocomplete="tel" placeholder="+91 98765 43210"></label>
      <label>City <span class="optional">Optional</span><input name="city" autocomplete="address-level2" placeholder="Your city"></label>
      <label>State / region <span class="optional">Optional</span><input name="state" autocomplete="address-level1" placeholder="Your state"></label>
      <label>Business type <em>*</em><select required name="business_type"><option value="" disabled selected>Select your business type</option><option>IndiaMART seller</option><option>Manufacturer or supplier</option><option>Wholesaler or distributor</option><option>B2B trading or export</option><option>Professional or service business</option><option>Consulting or agency</option><option>E-commerce</option><option>Retail or trading</option><option>Other</option></select></label>
      <label>Interested in <select name="interest"><option selected>Diwali offer (20% off subscription + setup)</option><option>Monthly CRM subscription</option><option>One-time setup and onboarding</option><option>Both</option><option>Not sure yet</option></select></label>
      <label class="form-full">What would you like help with? <span class="optional">Optional</span><textarea name="message" rows="2" placeholder="Tell us what your team needs…"></textarea></label>
    </div>
    <div class="form-bottom"><p>By submitting, you agree we may contact you about Vetra CRM. See our <a href="/privacy.html">privacy notice</a>.</p><button class="btn btn-primary" type="submit">Get 20% offer <span>↗</span></button></div>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
`;
document.body.append(offerDialog);

const contactForms = [...document.querySelectorAll('.contact-form')];
const claimOfferFromUrl = new URLSearchParams(window.location.search).get('offer') === 'diwali20';

contactForms.forEach((contactForm) => {
  const contactStatus = contactForm.querySelector('.form-status');
  const interestSelect = contactForm.querySelector('[name="interest"]');
  if (claimOfferFromUrl && interestSelect) interestSelect.value = 'Diwali offer (20% off subscription + setup)';

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
    const contextLines = [
      businessType ? `Business type: ${businessType}` : '',
      `Website page: ${pageUrl}`,
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

offerDialog.querySelector('.offer-close').addEventListener('click', () => offerDialog.close('dismiss'));
offerDialog.addEventListener('click', (event) => {
  if (event.target === offerDialog) offerDialog.close('dismiss');
});

// Show the offer form on every page load; no delay or prior-visit/session gate.
offerDialog.showModal();
window.addEventListener('pageshow', (event) => {
  if (event.persisted && !offerDialog.open) offerDialog.showModal();
});
