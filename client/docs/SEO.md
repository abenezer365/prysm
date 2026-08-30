# SEO

`RouteManager` derives document titles and descriptions from the content registry and updates Open Graph and Twitter metadata on route navigation. `index.html` includes baseline description, social-card, theme, canonical, and viewport metadata. Public pages use semantic headings, breadcrumbs, descriptive links, and clean URLs.

`public/robots.txt` allows public routes, blocks `/app/`, and points to `sitemap.xml`. The current sitemap lists primary routes. At deployment, generate absolute canonical and sitemap URLs from the registry because the production hostname is not yet known. Client-side metadata improves navigation and sharing, but robust indexing should eventually use static generation or server rendering.
