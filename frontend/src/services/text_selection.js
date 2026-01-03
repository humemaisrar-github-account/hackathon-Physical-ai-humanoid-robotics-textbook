/**
 * Text selection service for the RAG Chatbot frontend
 */

class TextSelectionService {
  constructor() {
    this.selectedText = '';
    this.selectionStart = null;
    this.selectionEnd = null;
    this.onSelectionChange = null;
  }

  /**
   * Initialize the text selection service
   */
  init() {
    document.addEventListener('mouseup', this.handleSelection.bind(this));
  }

  /**
   * Handle text selection event
   */
  handleSelection() {
    const selectedText = window.getSelection().toString().trim();

    if (selectedText) {
      this.selectedText = selectedText;
      this.updateSelectionRange();

      // Notify any listeners of the selection change
      if (this.onSelectionChange) {
        this.onSelectionChange(selectedText);
      }
    } else {
      this.selectedText = '';
      this.selectionStart = null;
      this.selectionEnd = null;
    }
  }

  /**
   * Update the selection range coordinates
   */
  updateSelectionRange() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      this.selectionStart = {
        node: range.startContainer,
        offset: range.startOffset
      };
      this.selectionEnd = {
        node: range.endContainer,
        offset: range.endOffset
      };
    }
  }

  /**
   * Get the currently selected text
   */
  getSelectedText() {
    return this.selectedText;
  }

  /**
   * Clear the current selection
   */
  clearSelection() {
    this.selectedText = '';
    this.selectionStart = null;
    this.selectionEnd = null;

    // Remove the selection from the DOM
    window.getSelection().removeAllRanges();
  }

  /**
   * Highlight selected text with a custom style
   */
  highlightSelection(customClass = 'highlighted-text') {
    if (!this.selectedText) return;

    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const span = document.createElement('span');
      span.classList.add(customClass);

      range.surroundContents(span);
    }
  }

  /**
   * Remove highlighting from selected text
   */
  removeHighlighting(customClass = 'highlighted-text') {
    const highlightedElements = document.querySelectorAll(`.${customClass}`);
    highlightedElements.forEach(element => {
      const parent = element.parentNode;
      while (element.firstChild) {
        parent.insertBefore(element.firstChild, element);
      }
      parent.removeChild(element);
    });
  }

  /**
   * Set a callback to be notified when text selection changes
   */
  setOnSelectionChange(callback) {
    this.onSelectionChange = callback;
  }

  /**
   * Get the coordinates of the selection for positioning UI elements
   */
  getSelectionCoordinates() {
    const selection = window.getSelection();
    if (selection.rangeCount === 0) return null;

    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    return {
      x: rect.left + window.scrollX,
      y: rect.top + window.scrollY,
      width: rect.width,
      height: rect.height,
      rect: rect
    };
  }

  /**
   * Create a floating button near the selection
   */
  createFloatingButton(buttonText = 'Ask', onClickCallback) {
    // Remove any existing floating buttons
    this.removeFloatingButton();

    if (!this.selectedText) return null;

    const coords = this.getSelectionCoordinates();
    if (!coords) return null;

    const button = document.createElement('button');
    button.textContent = buttonText;
    button.style.position = 'fixed';
    button.style.left = `${coords.x + coords.width / 2}px`;
    button.style.top = `${coords.y - 40}px`;
    button.style.zIndex = '10000';
    button.style.backgroundColor = '#007bff';
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.borderRadius = '4px';
    button.style.padding = '8px 12px';
    button.style.cursor = 'pointer';
    button.style.fontSize = '14px';
    button.onclick = onClickCallback || (() => {
      // Default action: log the selected text
      console.log('Selected text:', this.selectedText);
    });

    document.body.appendChild(button);
    return button;
  }

  /**
   * Remove the floating button
   */
  removeFloatingButton() {
    const existingButton = document.querySelector('button[style*="position: fixed"]');
    if (existingButton) {
      existingButton.remove();
    }
  }

  /**
   * Get word count of selected text
   */
  getWordCount() {
    if (!this.selectedText) return 0;
    return this.selectedText.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Get character count of selected text
   */
  getCharacterCount() {
    return this.selectedText ? this.selectedText.length : 0;
  }
}

// Create a singleton instance
const textSelectionService = new TextSelectionService();

// Initialize the service when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    textSelectionService.init();
  });
} else {
  textSelectionService.init();
}

export default textSelectionService;