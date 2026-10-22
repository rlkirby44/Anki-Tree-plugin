document.addEventListener("DOMContentLoaded", () => {
    const notify = () => pycmd("tree_changed");
    window.addEventListener("scroll", notify, true);
    window.addEventListener("resize", notify);
    new MutationObserver(notify).observe(document.body, { childList: true, subtree: true });
    notify();
});
