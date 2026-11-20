const form = document.getElementById('contact-form') as HTMLFormElement | null;
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    // Use the SSR proxy route — avoids CORS entirely (same-origin request).
    const submitBtn = document.getElementById('cf-submit') as HTMLButtonElement;
    const submitText = document.getElementById('cf-submit-text')!;
    const submitLoading = document.getElementById('cf-submit-loading')!;
    const status = document.getElementById('cf-status')!;

    document.querySelectorAll('.form-error').forEach(el => (el.textContent = ''));
    status.textContent = '';
    status.className = 'contact-form__status';

    const data: Record<string, string> = {};
    new FormData(form).forEach((v, k) => { data[k] = String(v); });
    // enquiry_type field removed from UI — default to 'general' for the backend
    data['enquiry_type'] = 'general';

    submitBtn.disabled = true;
    submitText.style.display = 'none';
    submitLoading.style.display = '';

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) {
        if (Array.isArray(json.detail)) {
          json.detail.forEach((err: { loc?: string[]; msg: string }) => {
            const field = err.loc?.[err.loc.length - 1];
            if (field) {
              const errorEl = document.getElementById(`cf-${field}-error`);
              if (errorEl) errorEl.textContent = err.msg;
            }
          });
          status.textContent = 'Please fix the errors above.';
          status.className = 'contact-form__status error';
        } else {
          status.textContent = json.detail || 'Something went wrong. Please try again.';
          status.className = 'contact-form__status error';
        }
      } else {
        status.textContent = json.message || "Message sent! I'll get back to you soon.";
        status.className = 'contact-form__status success';
        form.reset();
      }
    } catch {
      status.textContent = 'Network error. Please check your connection and try again.';
      status.className = 'contact-form__status error';
    } finally {
      submitBtn.disabled = false;
      submitText.style.display = '';
      submitLoading.style.display = 'none';
    }
  });
}
