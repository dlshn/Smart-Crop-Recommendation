# Frontend changes: separate Home/About pages + modern nav bar

## New dependency
Added `react-router-dom` to `package.json`. Run `npm install` after
copying these files in.

## New files
- `src/components/Navbar.jsx` — sticky, glass-blurred nav bar (keeps
  your existing leaf/wheat/cream/ink theme and soft-shadow style).
  Active route gets a highlighted color + underline. Below the `md`
  breakpoint it collapses into an animated hamburger menu instead of
  the desktop link row.
- `src/pages/Home.jsx` — the hero, stats, recommendation form, results,
  and long-term crops sections (moved out of the old single-file
  `App.jsx`, content unchanged).
- `src/pages/About.jsx` — a full dedicated About page (previously just
  a small inline card): how a recommendation is built (4-step
  breakdown), the short-term vs long-term crop distinction, and the
  tech stack -- all in the same card/section style as the rest of the
  site.

## Changed files
- `src/App.jsx` — now just sets up `<Routes>` (`/` -> Home, `/about` ->
  About) plus the shared `Navbar` and footer, instead of holding all
  the page content directly.
- `src/main.jsx` — wrapped the app in `<BrowserRouter>` so the nav
  links do real client-side routing.

## Nothing else changed
`tailwind.config.js` and `src/index.css` are untouched -- the same
colors, shadows, and fonts are reused throughout the new Navbar/About
page, nothing about the visual theme was replaced.

## To apply
```
cd frontend
npm install       # picks up react-router-dom
npm run dev
```
Visit `/` for the dashboard, `/about` for the new About page, and try
narrowing the browser window to see the mobile menu.

## One thing to know for production builds
If you later run `npm run build` and deploy the static output to a
host that doesn't rewrite unknown paths to `index.html` (some static
hosts need this configured), a direct visit to `/about` (not
navigated-to via a link) could 404. Vite's own dev server and
`vite preview` already handle this correctly; it only matters for
your eventual production hosting setup.
