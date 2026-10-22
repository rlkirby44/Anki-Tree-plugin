(function () {
    const IGNORE_SELECTORS = [];            // extra CSS selectors to never treat as obstacles
    const MAX_WIDTH_FRACTION = 0.9;         // styled boxes wider than this count as wrappers
    const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "LINK", "META", "NOSCRIPT", "TEMPLATE"]);
    const ATOMIC_TAGS = new Set(["BUTTON", "INPUT", "SELECT", "TEXTAREA", "CANVAS",
                                "SVG", "IMG", "VIDEO", "IFRAME"]);
    const rects = [];

    function add(r) {
        if (r.width >= 1 && r.height >= 1) {
            rects.push({ x: r.left, y: r.top, w: r.width, h: r.height });
        }
    }

    function isStyled(style) {
        const bg = style.backgroundColor;
        const hasBg = bg !== "transparent" && bg !== "rgba(0, 0, 0, 0)";
        const hasImage = style.backgroundImage !== "none";
        const hasBorder = ["Top", "Right", "Bottom", "Left"].some(side =>
        parseFloat(style["border" + side + "Width"]) > 0 &&
        style["border" + side + "Style"] !== "none");
        const hasShadow = style.boxShadow !== "none";
        return hasBg || hasImage || hasBorder || hasShadow;
    }

    function addText(node) {
        if (!node.nodeValue.trim()) return;
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const r of range.getClientRects()) add(r);
    }

    function walk(el, isRoot) {
        if (SKIP_TAGS.has(el.tagName.toUpperCase())) return;
        if (IGNORE_SELECTORS.some(sel => el.matches(sel))) return;
        const style = getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden") return;

        if (!isRoot) {
            const rect = el.getBoundingClientRect();
            const hasSize = rect.width >= 1 && rect.height >= 1;
            const tooWide = rect.width > window.innerWidth * MAX_WIDTH_FRACTION;
            const atomic = ATOMIC_TAGS.has(el.tagName.toUpperCase());
            if (hasSize && (atomic || (isStyled(style) && !tooWide))) {
                add(rect);
                return;
            }
        }
        for (const child of el.childNodes) {
            if (child.nodeType === Node.TEXT_NODE) addText(child);
            else if (child.nodeType === Node.ELEMENT_NODE) walk(child, false);
        }
    }

    walk(document.body, true);
    return rects;
})()
