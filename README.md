# Vegan Food Travel (veganfoodtravel.com)

Eat like a local. Stay vegan.

## How the site works

- `data/countries.json` holds every country guide: dishes, what to watch for, phrase card.
- `build.py` turns that data into the website in `dist/`.
- Pushing to the `main` branch on GitHub rebuilds and deploys the site on Cloudflare Pages automatically.

## Making a country guide go live

A country is hidden from search engines until it has been checked first-hand.

1. Check the dishes in `data/countries.json` and correct anything wrong.
2. Add `"checked": "March 2027"` (the month you checked it).
3. Change `"verified": false` to `"verified": true`.
4. Push to GitHub. The site rebuilds, the page becomes indexable and is added to the sitemap.

## Build locally

```
python build.py
```

Cloudflare Pages settings: build command `python build.py`, output directory `dist`.
