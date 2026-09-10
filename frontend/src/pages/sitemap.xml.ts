import type { APIRoute } from 'astro';

const pages = [
  '',
  'privacy',
  'terms',
  'contact',
  'tools/arxiv-to-latex-table',
  'tools/ieee-literature-survey-generator',
  'tools/research-paper-comparison-matrix',
  'tools/systematic-literature-review-matrix',
  'tools/research-gap-analyzer-matrix',
  'tools/acm-paper-synthesis-matrix',
  'tools/phd-dissertation-literature-survey',
  'tools/sciencedirect-paper-matrix',
  'en',
  'es',
  'de',
  'en/privacy',
  'es/privacy',
  'de/privacy',
  'en/terms',
  'es/terms',
  'de/terms'
];

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site ? site.toString().replace(/\/$/, '') : 'https://paper-matrix-ai.pages.dev';

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages
  .map((page) => {
    const url = page ? `${baseUrl}/${page}` : baseUrl;
    const priority = page.startsWith('tools/') ? '0.9' : page === '' ? '1.0' : '0.7';
    return `  <url>
    <loc>${url}</loc>
    <changefreq>weekly</changefreq>
    <priority>${priority}</priority>
  </url>`;
  })
  .join('\n')}
</urlset>`;

  return new Response(sitemap.trim(), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8'
    }
  });
};