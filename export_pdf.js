const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  const htmlPath = path.join(__dirname, 'index.html');
  await page.goto('file://' + htmlPath, {
    waitUntil: 'networkidle0'
  });

  const slides = await page.$$('.slide');
  console.log(slides.length + '枚のスライドを検出');

  await page.evaluate(() => {
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide) => {
      slide.style.pageBreakAfter = 'always';
      slide.style.width = '1280px';
      slide.style.height = '720px';
      slide.style.margin = '0';
      slide.style.boxSizing = 'border-box';
    });
  });

  await page.pdf({
    path: 'TechNova_slides.pdf',
    width: '1280px',
    height: '720px',
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 }
  });

  console.log('PDF出力完了: TechNova_slides.pdf');
  await browser.close();
})();
