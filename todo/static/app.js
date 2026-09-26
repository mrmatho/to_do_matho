document.addEventListener('htmx:after:request', (event) => {
    const form = event.target.closest('form');
    const status = event.detail.ctx.response?.status;
    if (!form || !status || status >= 400) return;
    form.reset();
    form.querySelector('output')?.replaceChildren();
});
