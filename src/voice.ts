const API = "http://127.0.0.1:8765/api";

async function readError(r: Response, fallback: string) {
  const data = await r.json().catch(() => ({}));
  return data.detail || fallback;
}

export async function transcribeAudio(blob: Blob, language = "") {
  const form = new FormData();
  const extension = blob.type.includes("wav") ? "wav" : "webm";
  form.append("audio", blob, "aether-recording." + extension);
  const query = language ? "?language=" + encodeURIComponent(language) : "";
  const r = await fetch(API + "/voice/transcribe" + query, {
    method: "POST",
    body: form,
  });
  if (!r.ok) throw new Error(await readError(r, "Voice transcription failed"));
  return r.json() as Promise<{
    text: string;
    language?: string;
    language_probability?: number;
    provider: string;
    model: string;
  }>;
}

export async function chatForVoice(
  message: string,
  history: { role: "user" | "assistant"; content: string }[] = [],
) {
  const voiceInstruction =
    "This is a voice conversation. Answer naturally and concisely in the same language as the user's latest message. " +
    "If the user speaks Urdu, reply in Urdu script, not Hindi. Avoid markdown tables and unnecessary formatting because the answer will be spoken aloud.";

  const r = await fetch(API + "/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: voiceInstruction + "\n\nUser's voice message:\n" + message,
      history,
    }),
  });
  if (!r.ok) throw new Error(await readError(r, "AI voice response failed"));
  return r.json() as Promise<{
    content: string;
    provider: string;
    model: string;
  }>;
}

export async function speakText(
  text: string,
  rate = 175,
  language = "",
) {
  const r = await fetch(API + "/voice/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, rate, language }),
  });
  if (!r.ok) throw new Error(await readError(r, "Voice synthesis failed"));
  return r.blob();
}

export async function voiceProviders() {
  const r = await fetch(API + "/voice/providers");
  if (!r.ok) throw new Error("Voice provider status unavailable");
  return r.json();
}
