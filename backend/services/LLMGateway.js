// backend/services/LLMGateway.js
/*
  Gateway from Node → Flask LLM service.
  Uses Node.js native fetch (no extra deps needed).
*/

async function generate(prompt) {
  try {
    const res = await fetch("http://localhost:5005/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prompt),
    });

    if (!res.ok) {
      throw new Error(`LLM service returned ${res.status}`);
    }

    const data = await res.json();

    // Ensure object shape for interactController
    return {
      dialogue: data.dialogue || "No response",
      action: data.action || null,
      metadata: data.metadata || {},
    };
  } catch (err) {
    console.error("LLMGateway error:", err);
    return {
      dialogue: "The NPC falls silent.",
      action: null,
      metadata: { error: err.message },
    };
  }
}

module.exports = { generate };
