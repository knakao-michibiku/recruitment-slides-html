/**
 * HTMLスライドをスクリーンショットして画像化
 * Usage: node capture_slides.js
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureSlides() {
  const outputDir = path.join(__dirname, 'slide_images');

  // 出力ディレクトリ作成
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }

  console.log('🚀 Puppeteer起動中...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // スライドサイズに合わせてビューポート設定 (1280x720)
  await page.setViewport({
    width: 1280,
    height: 720,
    deviceScaleFactor: 2 // 高解像度
  });

  const htmlPath = `file://${path.join(__dirname, 'index.html')}`;
  console.log(`📄 HTMLを読み込み中: ${htmlPath}`);

  await page.goto(htmlPath, { waitUntil: 'networkidle2' });

  // スライドの数を取得
  const slideCount = await page.evaluate(() => {
    return document.querySelectorAll('.slide').length;
  });

  console.log(`📊 スライド数: ${slideCount}`);

  // 各スライドをキャプチャ
  for (let i = 0; i < slideCount; i++) {
    const slideNum = String(i + 1).padStart(2, '0');

    // 対象スライドを画面中央に表示
    await page.evaluate((index) => {
      const slides = document.querySelectorAll('.slide');
      if (slides[index]) {
        // すべてのスライドを非表示にし、対象だけ表示
        slides.forEach((slide, idx) => {
          if (idx === index) {
            slide.style.position = 'fixed';
            slide.style.top = '0';
            slide.style.left = '0';
            slide.style.zIndex = '9999';
            slide.style.display = 'block';
          } else {
            slide.style.display = 'none';
          }
        });

        // コンテナを非表示
        const container = document.querySelector('.slides-container');
        if (container) {
          container.style.padding = '0';
          container.style.gap = '0';
          container.style.background = 'transparent';
        }

        // ナビゲーション非表示
        const nav = document.querySelector('.slideshow-nav');
        if (nav) nav.style.display = 'none';

        const help = document.querySelector('.slideshow-help');
        if (help) help.style.display = 'none';

        const btn = document.querySelector('.slideshow-start-btn');
        if (btn) btn.style.display = 'none';

        document.body.style.background = 'transparent';
        document.body.style.margin = '0';
        document.body.style.padding = '0';
      }
    }, i);

    // 少し待機（アニメーション完了）
    await new Promise(resolve => setTimeout(resolve, 100));

    // スクリーンショット
    const outputPath = path.join(outputDir, `slide_${slideNum}.png`);
    await page.screenshot({
      path: outputPath,
      clip: {
        x: 0,
        y: 0,
        width: 1280,
        height: 720
      }
    });

    console.log(`✅ スライド ${slideNum}/${slideCount} を保存: ${outputPath}`);
  }

  await browser.close();

  console.log(`\n🎉 完了！ ${slideCount}枚のスライド画像を保存しました`);
  console.log(`📁 出力先: ${outputDir}`);
  console.log('\n次のステップ:');
  console.log('1. Google Slides を開く');
  console.log('2. 「挿入」→「画像」→「パソコンからアップロード」');
  console.log('3. 画像を選択してスライドに配置');
}

captureSlides().catch(console.error);
