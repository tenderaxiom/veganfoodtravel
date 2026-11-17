// One-click unsubscribe: /api/unsubscribe?t=TOKEN (GET shows confirmation, POST for List-Unsubscribe-Post).
async function unsubscribe(env, token) {
  if (!token || !/^[a-f0-9]{32}$/.test(token)) return false;
  const r = await env.DB.prepare(
    "UPDATE subscribers SET status='unsubscribed', unsubscribed_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE token=?1"
  ).bind(token).run();
  return r.meta.changes > 0;
}

export async function onRequestGet({ request, env }) {
  const t = new URL(request.url).searchParams.get("t");
  const ok = await unsubscribe(env, t);
  return Response.redirect(new URL(ok ? "/unsubscribed/" : "/unsubscribed/?status=unknown", request.url).toString(), 303);
}

export async function onRequestPost({ request, env }) {
  const t = new URL(request.url).searchParams.get("t");
  await unsubscribe(env, t);
  return new Response("Unsubscribed", { status: 200 });
}
