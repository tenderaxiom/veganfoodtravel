// Free phrase-card pack signup. Stores consenting subscribers in D1, then sends the
// visitor to /thanks/ where the pack downloads immediately.
const CONSENT = "Send me the free vegan phrase-card pack and the Vegan Food Travel weekly email. I can unsubscribe at any time.";
const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,255}\.[a-z]{2,}$/i;

function back(request, path, params = {}) {
  const url = new URL(path, request.url);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  return Response.redirect(url.toString(), 303);
}

export async function onRequestPost({ request, env }) {
  let form;
  try { form = await request.formData(); } catch { return back(request, "/free-guide/", { error: "form" }); }
  // Honeypot: real people never fill this hidden field.
  if ((form.get("website") || "").toString().trim()) return back(request, "/thanks/");
  const email = (form.get("email") || "").toString().trim().toLowerCase();
  const consent = form.get("consent");
  const country = (form.get("country") || "").toString().slice(0, 40);
  const source = (form.get("source") || "").toString().slice(0, 80);
  if (!EMAIL_RE.test(email)) return back(request, source || "/free-guide/", { error: "email" });
  if (!consent) return back(request, source || "/free-guide/", { error: "consent" });
  const token = crypto.randomUUID().replace(/-/g, "");
  const cc = (request.cf && request.cf.country) || null;
  await env.DB.prepare(
    `INSERT INTO subscribers (email, first_country, source, consent_text, token, country_code)
     VALUES (?1, ?2, ?3, ?4, ?5, ?6)
     ON CONFLICT(email) DO UPDATE SET status='active', unsubscribed_at=NULL`
  ).bind(email, country || null, source || null, CONSENT, token, cc).run();
  return back(request, "/thanks/");
}

export async function onRequestGet({ request }) {
  return back(request, "/free-guide/");
}
