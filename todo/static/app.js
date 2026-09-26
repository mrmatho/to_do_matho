function within(root, selector) {
    const matches = [...root.querySelectorAll(selector)];
    return root.matches?.(selector) ? [root, ...matches] : matches;
}

document.addEventListener('htmx:after:request', (event) => {
    const form = event.target.closest('form');
    const status = event.detail.ctx.response?.status;
    if (!form || !status || status >= 400) return;
    form.reset();
    form.querySelector('output')?.replaceChildren();
    form.closest('dialog')?.close();
});

document.addEventListener('click', (event) => {
    const dialog = event.target.closest('dialog');
    // The dialog has no padding, so a click landing on the dialog itself is on the backdrop.
    if (event.target === dialog || event.target.closest('[data-close-dialog]')) {
        dialog.close();
    }
});

function initSortables(root) {
    for (const list of within(root, '.task-list')) {
        if (Sortable.get(list)) continue;
        Sortable.create(list, {
            group: 'tasks',
            animation: 150,
            delay: 150,
            delayOnTouchOnly: true,
            forceFallback: true,
            ghostClass: 'task-ghost',
            chosenClass: 'task-chosen',
            fallbackClass: 'task-drag',
            onEnd: saveMove,
        });
    }
}

async function saveMove(event) {
    if (event.from === event.to && event.oldIndex === event.newIndex) return;
    const body = new URLSearchParams({
        category_id: event.to.dataset.categoryId,
        position: event.newIndex,
    });
    try {
        const response = await fetch(event.item.dataset.moveUrl, { method: 'POST', body });
        if (response.ok) return;
    } catch {
        // Network failure: fall through and resync with the server.
    }
    const board = document.getElementById('board');
    htmx.ajax('GET', board.dataset.refreshUrl, { target: '#board', swap: 'outerHTML' });
}

function showModals(root) {
    for (const dialog of within(root, 'dialog[data-show-modal]')) {
        if (!dialog.open) dialog.showModal();
    }
}

initSortables(document);
htmx.onLoad((root) => {
    initSortables(root);
    showModals(root);
});
