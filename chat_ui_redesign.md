# Chat UI Redesign Concepts

## 1. Visual Aesthetics (The "Premium" Feel)
*   **Glassmorphism Background:** Instead of a solid white/black drawer, use a translucent background with a blur effect (`backdrop-filter: blur(10px)`). This makes it feel lightweight and integrated with the site.
*   **Floating Panel:** Detach the panel slightly from the edge of the screen (giving it a margin) and round the corners (20px radius). This makes it look like a floating "widget" rather than a sidebar.
*   **Typography:** Use a clean, sans-serif font (Inter or sf-pro).
*   **Color Palette:** Stick to the monochrome theme but use shades of gray (#F5F5F5, #333) for depth, rather than pure black/white.

## 2. User Experience (UX)
*   **"Thinking" Indicator:** Since the agent uses tools (GitHub, Medium), show *what* it is doing.
    *   *Example:* A small text appearing above the response area: "🔎 Searching GitHub..." -> "📖 Reading Resume...".
*   **Streaming Responses:** Text should appear character-by-character (typewriter effect) to feel alive.
*   **Markdown Rendering:** Ensure the UI supports bold, lists, code blocks, and clickable links.

## 3. Structural Elements
### Header
*   **Avatar:** A small avatar of you (or a robot icon) with a green "Online" dot.
*   **Title:** "Pamudu AI" or "Digital Brain".
*   **Controls:** Close (X) and perhaps a "Clear Chat" (Trash icon).

### Message Area
*   **User Bubble:** Aligned Right, solid dark color (Accent). Small text.
*   **AI Bubble:** Aligned Left, light gray background or transparent.
*   **Citations (Crucial):** If the bot uses a source, display it as a small "Chip" or footnote at the bottom of the bubble.
    *   *Example:* `[📄 Resume]`, `[🐙 GitHub: virtual-pamudu]`

### Input Area
*   **Floating Input:** A pill-shaped input field floating at the bottom.
*   **Suggestions:** Before the user types, show 2-3 bubbles:
    *   "Tell me about your experience"
    *   "What are your latest projects?"

## 4. Frontend Integration
### Backend URL
**`https://virtual-pamudu-bt71onx2g-pamudu-ranasinghes-projects.vercel.app`**

### Connection Example (Streaming)
Since the endpoint is `POST`, use `fetch` instead of `EventSource`.

```javascript
const API_URL = "https://virtual-pamudu-bt71onx2g-pamudu-ranasinghes-projects.vercel.app";

async function sendMessage(sessionId, message) {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message: message })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n\n");
    
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const event = JSON.parse(line.slice(6));
        
        if (event.type === "status") {
          console.log("Thinking:", event.message); // Update UI "Thinking..."
        } else if (event.type === "result") {
          console.log("Answer:", event.answer);   // Show final answer
        }
      }
    }
  }
}
```
