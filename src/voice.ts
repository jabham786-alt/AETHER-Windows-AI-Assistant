const API = "http://127.0.0.1:8765/api";

export async function transcribeAudio(blob: Blob, language = "") {
  const form = new FormData();
  const extension = blob.type.includes("wav") ? "wav" : "webm";
  form.append("audio", blob, "aether-recording." + extension);
  const query = language ? "?language=" + encodeURIComponent(language) : "";
  const r = await fetch(API + "/voice/transcribe" + query, { method: "POST", body: form });
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail || "Voice transcription failed");
  return data;
}

export async function speakText(text: string, rate = 175) {
  const r = await fetch(API + "/voice/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, rate }),
  });
  if (!r.ok) {
    const data = await r.json().catch(() => ({}));
    throw new Error(data.detail || "Voice synthesis failed");
  }
  return r.blob();
}

export async function voiceProviders() {
  const r = await fetch(API + "/voice/providers");
  if (!r.ok) throw new Error("Voice provider status unavailable");
  return r.json();
}
