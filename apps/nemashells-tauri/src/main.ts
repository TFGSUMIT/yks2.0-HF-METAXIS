import { fetch } from "@tauri-apps/plugin-http";

const API = "http://127.0.0.1:4310";

type OperatorState = {
  service: { status: string; profile: string; transport: string };
  operator_context: { cadence: string };
  classification: { status: string; reasons: string[] };
  model: {
    primary_candidate: string;
    sufficiency: string;
    active_route: string;
    external_api_allowed: boolean;
  };
  proof: { posture: string };
  storage: {
    backend: string;
    durable: boolean;
    credential_exposed_to_model: boolean;
  };
  capabilities: {
    profile: string;
    loaded_count: number;
    active_count: number;
    execution_boundary: string;
    credential_exposed_to_model: boolean;
    skills: Array<{ id: string; version: string; active: boolean }>;
    plugins: Array<{ id: string; version: string; active: boolean }>;
  };
  integrations: {
    github: {
      account: string;
      authority_repo: string;
      implementation_repo: string;
      mode: string;
      live: boolean;
      reason: string;
      writes_allowed: boolean;
      credential_exposed_to_model: boolean;
    };
  };
  next_safe_action: string;
};

type ThreadCreated = { id: string };
type StoredTurn = TurnCreated & {
  created_at: string;
  classification: string;
};
type StoredThread = {
  id: string;
  title: string;
  created_at: string;
  turns: StoredTurn[];
};
type ThreadList = { threads: StoredThread[] };
type TurnCreated = {
  id: string;
  operator: string;
  assistant: string;
  route: string;
};

let threadId: string | undefined;
let threads: StoredThread[] = [];
let sending = false;

function element<T extends HTMLElement>(id: string): T {
  const value = document.getElementById(id);
  if (!value) throw new Error(`missing UI element: ${id}`);
  return value as T;
}

function setText(id: string, value: string): void {
  element(id).textContent = value;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  const value = (await response.json()) as T | { error?: string; message?: string };
  if (!response.ok) {
    const error = value as { error?: string; message?: string };
    throw new Error(error.message || error.error || `METAXIS HTTP ${response.status}`);
  }
  return value as T;
}

function tags(values: string[]): void {
  const target = element("readback-tags");
  target.replaceChildren(
    ...values.map((value) => {
      const tag = document.createElement("span");
      tag.textContent = value;
      return tag;
    }),
  );
}

function renderState(state: OperatorState): void {
  setText("service-status", state.service.status.toLowerCase());
  setText("service-profile", state.service.profile);
  setText("service-transport", state.service.transport);
  setText("profile-label", state.service.profile);
  setText("classification-pill", state.classification.status);
  setText("classification-reason", state.classification.reasons[0] || "No denial reason supplied.");
  const candidateParts = state.model.primary_candidate.split("/");
  setText("brain-candidate", candidateParts[candidateParts.length - 1] || "—");
  setText("brain-route", state.model.active_route);
  setText("brain-quality", state.model.sufficiency.toLowerCase());
  setText("brain-api", state.model.external_api_allowed ? "eligible" : "denied");
  setText("storage-backend", state.storage.backend);
  setText("storage-durable", state.storage.durable ? "yes" : "no");
  setText("storage-credential", state.storage.credential_exposed_to_model ? "violation" : "never");
  const activeSkill = state.capabilities.skills.find((item) => item.active);
  setText("capability-skill", activeSkill ? `${activeSkill.id}@${activeSkill.version}` : "none");
  setText("capability-plugins", `${state.capabilities.active_count - state.capabilities.skills.filter((item) => item.active).length} active / ${state.capabilities.plugins.length} loaded`);
  setText("capability-boundary", state.capabilities.execution_boundary);
  setText("capability-credential", state.capabilities.credential_exposed_to_model ? "violation" : "never");
  setText("github-account", state.integrations.github.account);
  setText("github-authority", state.integrations.github.authority_repo.split("/").pop() || "—");
  setText("github-implementation", state.integrations.github.implementation_repo.split("/").pop() || "—");
  setText("github-live", state.integrations.github.live ? "live read" : "declared only");
  setText("github-writes", state.integrations.github.writes_allowed ? "enabled" : "denied");
  setText("github-credential", state.integrations.github.credential_exposed_to_model ? "violation" : "never");
  setText("proof-posture", state.proof.posture);
  setText("next-action", state.next_safe_action);
  tags([
    state.proof.posture,
    state.model.sufficiency.toLowerCase(),
    state.storage.backend,
    state.integrations.github.live ? "github-live-read" : "github-declared-only",
    `${state.capabilities.active_count}/${state.capabilities.loaded_count}-capabilities-active`,
    state.operator_context.cadence,
  ]);
  element("service-dot").classList.add("online");
}

function renderError(error: unknown): void {
  const message = error instanceof Error ? error.message : String(error);
  setText("service-status", "unavailable");
  setText("profile-label", "service unavailable");
  setText("next-action", `Local METAXIS unavailable: ${message}. No external fallback was attempted.`);
  element("service-dot").classList.remove("online");
}

async function refresh(): Promise<void> {
  try {
    renderState(await request<OperatorState>("/api/v1/operator-state"));
  } catch (error) {
    renderError(error);
  }
}

function message(role: "operator" | "assistant", text: string, route?: string, state?: "pending" | "error"): HTMLElement {
  const article = document.createElement("article");
  article.className = "message runtime-message";
  if (state) article.classList.add(state);
  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "operator" ? "blue" : "mint"}`;
  avatar.textContent = role === "operator" ? "YO" : "NS";
  const body = document.createElement("div");
  const title = document.createElement("h2");
  title.textContent = role === "operator" ? "You" : `NemaShells · ${route || "METAXIS"}`;
  const copy = document.createElement("p");
  copy.textContent = text;
  body.append(title, copy);
  article.append(avatar, body);
  element("conversation").append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
  return article;
}

function clearRuntimeMessages(): void {
  document.querySelectorAll(".runtime-message").forEach((item) => item.remove());
}

function renderThread(thread?: StoredThread): void {
  clearRuntimeMessages();
  if (!thread) return;
  threadId = thread.id;
  for (const turn of thread.turns) {
    message("operator", turn.operator);
    message("assistant", turn.assistant, turn.route);
  }
  document.querySelectorAll("#task-list .nav-item").forEach((item) => {
    item.classList.toggle("active", (item as HTMLElement).dataset.threadId === thread.id);
  });
}

function renderThreadList(): void {
  const list = element("task-list");
  list.replaceChildren();
  if (!threads.length) {
    const empty = document.createElement("p");
    empty.className = "task-empty";
    empty.textContent = "No saved tasks yet.";
    list.append(empty);
    return;
  }
  for (const thread of [...threads].reverse()) {
    const button = document.createElement("button");
    button.className = "nav-item";
    button.type = "button";
    button.dataset.threadId = thread.id;
    button.textContent = `◫  ${thread.title}`;
    button.title = thread.title;
    button.addEventListener("click", () => renderThread(thread));
    list.append(button);
  }
}

async function loadThreads(selectLatest = false): Promise<void> {
  const value = await request<ThreadList>("/api/v1/threads");
  threads = value.threads;
  renderThreadList();
  const selected = threads.find((thread) => thread.id === threadId);
  if (selected) renderThread(selected);
  else if (selectLatest && threads.length) renderThread(threads[threads.length - 1]);
}

async function submit(text: string): Promise<void> {
  if (sending) return;
  sending = true;
  const send = element<HTMLButtonElement>("send");
  send.disabled = true;
  try {
    if (!threadId) {
      const thread = await request<ThreadCreated>("/api/v1/threads", {
        method: "POST",
        body: JSON.stringify({ title: text.slice(0, 72) }),
      });
      threadId = thread.id;
    }
    message("operator", text);
    const pending = message("assistant", "Thinking…", "METAXIS", "pending");
    const turn = await request<TurnCreated>(`/api/v1/threads/${threadId}/turns`, {
      method: "POST",
      body: JSON.stringify({ text, classification: "DEVELOPMENT" }),
    });
    pending.remove();
    message("assistant", turn.assistant, turn.route);
    await loadThreads();
  } catch (error) {
    const messageText = error instanceof Error ? error.message : String(error);
    document.querySelectorAll(".runtime-message.pending").forEach((item) => item.remove());
    message("assistant", `Request failed safely: ${messageText}`, "METAXIS", "error");
  } finally {
    sending = false;
    send.disabled = false;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const input = element<HTMLTextAreaElement>("message-input");
  element("composer").addEventListener("submit", (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    void submit(text);
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      element<HTMLFormElement>("composer").requestSubmit();
    }
  });
  element("refresh").addEventListener("click", () => void refresh());
  element("new-task").addEventListener("click", () => {
    threadId = undefined;
    clearRuntimeMessages();
    document.querySelectorAll("#task-list .nav-item").forEach((item) => item.classList.remove("active"));
    input.focus();
  });
  void Promise.all([refresh(), loadThreads(true)]).catch(renderError);
  window.setInterval(() => void refresh(), 15_000);
});
