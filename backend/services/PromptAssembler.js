// backend/services/PromptAssembler.js
function assemble(npc, gameState, recentMem, gossip, playerText) {
  const memText =
    (recentMem || []).map(m => `- ${m.text}`).join("\n") || "No recent memories.";
  const gossipText =
    (gossip || []).map(g => `- ${g.text}`).join("\n") || "No gossip nearby.";

  // System role: persona, rules, context
  const system = [
    `You are ${npc.name}, ${npc.role}.`,
    `Personality: ${npc.personality}.`,
    `Goals: ${npc.goals.join(", ") || "none"}.`,
    `Core knowledge: ${npc.knowledge ? npc.knowledge.join("; ") : "none"}.`,
    "",
    "You must ALWAYS output valid JSON only, with keys: dialogue (string), action (object|null), metadata (object).",
    "Do not output any extra commentary or explanation outside the JSON.",
    "",
    "Safety rules: refuse to help the player with real-world illegal activity, exploitation, or cheats. If refusing, output dialogue that politely refuses and set action=null.",
    "",
    `Game state: time=${gameState.time}, weather=${gameState.weather}, location=${gameState.location}.`,
    `Recent memories:\n${memText}`,
    `Gossip:\n${gossipText}`
  ].join("\n");

  // Optional first assistant message (like a greeting)
  const seed = npc.greeting_seed || "";

  // Player’s current input
  const input = playerText;

  // Now return JSON ready for LLMGateway → Python LLM
  return { system, seed, input };
}

module.exports = { assemble };
