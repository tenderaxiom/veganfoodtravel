// Send www and *.pages.dev traffic to the one canonical address, so search engines see a single site.
export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname === "www.veganfoodtravel.com" || url.hostname.endsWith(".pages.dev")) {
    url.hostname = "veganfoodtravel.com";
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
