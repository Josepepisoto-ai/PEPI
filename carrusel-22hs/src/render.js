// Renderiza cada <section class="slide"> de carrusel.html como PNG 1080x1350.
// Uso: node carrusel-22hs/src/render.js
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto('file://' + path.join(__dirname, 'carrusel.html'));
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('section.slide');
  for (let i = 0; i < slides.length; i++) {
    const out = path.join(__dirname, '..', `slide-${String(i + 1).padStart(2, '0')}.png`);
    await slides[i].screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
