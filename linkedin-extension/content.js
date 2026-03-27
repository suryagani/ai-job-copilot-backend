let lastEditableEl = null;

// Detect and remember the last editable field the user clicked/focused
function isEditable(el) {
  if (!el) return false;

  const tag = el.tagName?.toUpperCase();
  if (tag === "INPUT" || tag === "TEXTAREA") return true;

  // LinkedIn often uses contenteditable divs
  if (el.isContentEditable) return true;

  // Sometimes the editable is a child inside a contenteditable wrapper
  if (el.closest && el.closest('[contenteditable="true"]')) return true;

  return false;
}

document.addEventListener("focusin", (e) => {
  const el = e.target;

  if (isEditable(el)) {
    lastEditableEl = el.isContentEditable ? el : (el.closest('[contenteditable="true"]') || el);
  } else if (el.closest && el.closest('[contenteditable="true"]')) {
    lastEditableEl = el.closest('[contenteditable="true"]');
  }
});

// Extra safety: also track click
document.addEventListener("click", (e) => {
  const el = e.target;
  if (isEditable(el)) {
    lastEditableEl = el.isContentEditable ? el : (el.closest('[contenteditable="true"]') || el);
  } else if (el.closest && el.closest('[contenteditable="true"]')) {
    lastEditableEl = el.closest('[contenteditable="true"]');
  }
});

function insertInto(el, text) {
  if (!el) return false;

  // If the element is inside a contenteditable wrapper, use wrapper
  const editable = el.isContentEditable ? el : (el.closest?.('[contenteditable="true"]') || el);

  editable.focus();

  // INPUT/TEXTAREA
  if (editable.tagName === "INPUT" || editable.tagName === "TEXTAREA") {
    editable.value = text;
    editable.dispatchEvent(new Event("input", { bubbles: true }));
    editable.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }

  // CONTENTEDITABLE
  if (editable.isContentEditable) {
    // Use execCommand for better compatibility with rich text editors
    document.execCommand("selectAll", false, null);
    document.execCommand("insertText", false, text);
    editable.dispatchEvent(new Event("input", { bubbles: true }));
    return true;
  }

  return false;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "INSERT_TEXT") {
    const ok = insertInto(lastEditableEl, message.text || "");

    if (!ok) {
      sendResponse({ ok: false, error: "No editable field selected. Click inside Headline/About field first." });
    } else {
      sendResponse({ ok: true });
    }
  }
});