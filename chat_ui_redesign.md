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
*   **Controls:** 
    *   `[ ! ]` **Info Icon:** Hover/Click to show "About System".
    *   `[ 🗑️ ]` **Clear Chat:** Reset conversation.

### About System Popover (Content for `!`)
**Pamudu AI v1.0.0**

**Key Features:**
- Optimized context management to reduce tool calling.
- Simultaneous tool calling.
- Dynamic graph-based reasoning engine.

**Key Capabilities so Far:**
- Live data scraping from GitHub, Medium, & YouTube.
- Deep context retrieval from academic papers & resume.
- Autonomous email drafting & workflow execution.

### Message Area
*   **User Bubble:** Aligned Right, solid dark color (Accent). Small text.
*   **AI Bubble:** Aligned Left, light gray background or transparent.
*   **Citations (Crucial):** If the bot uses a source, display it as a small "Chip" or footnote at the bottom of the bubble.
    *   *Example:* `[📄 Resume]`, `[🐙 GitHub: virtual-pamudu]`

### Input Area
*   **Floating Input:** A pill-shaped input field floating at the bottom.
*   **Suggestions:** Before the user types, show 2-3 bubbles:
    *   "Summarize AI Paper 📄"
    *   "Find Python Projects 🐙"
    *   "Draft Email 📧"

## 4. Frontend Integration Guide

### 1. Backend URL
**Base URL:** `https://virtual-pamudu-git-main-pamudu-ranasinghes-projects.vercel.app`

### 2. API Endpoints

#### A. Create Session (Required Step 1)
Create a session ID before starting a chat.
*   **Method:** `POST`
*   **Endpoint:** `/sessions`
*   **Body:** (Empty)

**Response:**
```json
{
  "session_id": "unique-session-id",
  "created_at": "..."
}
```

#### B. Chat with Streaming (Step 2)
Send a message and receive real-time "Thinking" updates.
*   **Method:** `POST`
*   **Endpoint:** `/chat/stream`
*   **Content-Type:** `application/json`
*   **Body:**
    ```json
    {
      "session_id": "unique-session-id",
      "message": "Hello"
    }
    ```

### 3. Implementation Code (React/JavaScript)
Use this helper function to handle connection and streaming.

```javascript
const API_URL = "https://virtual-pamudu-git-main-pamudu-ranasinghes-projects.vercel.app";

// 1. Create a Session
async function createSession() {
  try {
    const res = await fetch(`${API_URL}/sessions`, { method: "POST" });
    const data = await res.json();
    return data.session_id; // Save this in localStorage
  } catch (error) {
    console.error("Failed to create session:", error);
  }
}

// 2. Send Message & Stream Response
async function sendMessage(sessionId, userMessage, onStatusUpdate, onFinalResult) {
  try {
    const response = await fetch(`${API_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: userMessage })
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
          try {
            const event = JSON.parse(line.slice(6));
            
            if (event.type === "status") {
              onStatusUpdate(event.message); 
            } else if (event.type === "result") {
              onFinalResult(event.answer, event.citations);
            }
          } catch (e) { console.error("Parse error:", e); }
        }
      }
    }
  } catch (error) {
    console.error("Stream error:", error);
  }
}
```

### 4. Displaying Citations (UI Example)
When the API returns a result, it includes a `citations` array. Here is how to render them as "Chips" below the message.

**Data Structure:**
```json
"citations": [
  { "source_type": "github", "source_name": "virtual-pamudu", "url": "https://..." },
  { "source_type": "brain", "source_name": "resume.md", "url": "" }
]
```
