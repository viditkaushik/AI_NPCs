from flask import Flask, request, jsonify
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import json

app = Flask(__name__)

# --- Model Setup ---
REPO_ID = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"
FILENAME = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"

print("Downloading model...")
try:
    model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
except Exception as e:
    print(f"Error downloading model: {e}")
    exit()
print("Model downloaded to:", model_path)

# --- Initialize LLaMA on Mac M1 ---
llm = Llama(
    model_path=model_path,
    n_gpu_layers=0,  # CPU inference
    n_ctx=2048,      # Reduced context for M1 RAM
    verbose=True
)

# --- API route ---
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)
        system_prompt = data.get("system", "")
        seed = data.get("seed", "")
        player_text = data.get("input", "")

        # Conversation history
        conversation = [
            {"role": "system", "content": system_prompt},
        ]
        if seed:
            conversation.append({"role": "assistant", "content": seed})
        if player_text:
            conversation.append({"role": "user", "content": player_text})

        # Run LLM
        stream_output = llm.create_chat_completion(
            messages=conversation,
            max_tokens=256,
            stop=["<|end_of_text|>", "<|eot_id|>"],
            temperature=0.7,
            stream=True
        )

        buffer = ""
        for chunk in stream_output:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                token = delta["content"]
                buffer += token

        # Try to parse as JSON, otherwise wrap in JSON
        try:
            response_json = json.loads(buffer)
        except json.JSONDecodeError:
            response_json = {
                "dialogue": buffer.strip(),
                "action": None,
                "metadata": {}
            }

        return jsonify(response_json)

    except Exception as e:
        print("Error during generation:", e)
        return jsonify({
            "dialogue": "Error during LLM generation.",
            "action": None,
            "metadata": {"error": str(e)}
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
