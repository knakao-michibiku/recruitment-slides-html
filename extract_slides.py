#!/usr/bin/env python3
"""
HTMLスライドからコンテンツを抽出してMarkdown形式で出力
"""

from bs4 import BeautifulSoup
import re

def extract_slides(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    slides = soup.find_all('div', class_='slide')

    output = []
    for i, slide in enumerate(slides, 1):
        slide_content = []
        slide_content.append(f"\n## スライド {i}")

        # タイトルを取得
        title = slide.find(['h1', 'h2', 'h3'], class_=lambda x: x and ('title' in str(x) or 'section-title' in str(x)))
        if not title:
            title = slide.find(['h1', 'h2', 'h3'])

        if title:
            title_text = title.get_text(strip=True)
            slide_content.append(f"**タイトル**: {title_text}")

        # サブタイトル
        subtitle = slide.find(class_='subtitle')
        if subtitle:
            slide_content.append(f"**サブタイトル**: {subtitle.get_text(strip=True)}")

        # メインコンテンツ
        content_div = slide.find('div', class_='content')
        if content_div:
            # リストアイテム
            items = content_div.find_all('li')
            if items:
                slide_content.append("**内容**:")
                for item in items:
                    text = item.get_text(strip=True)
                    if text:
                        slide_content.append(f"  - {text}")

            # 段落
            paragraphs = content_div.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    slide_content.append(f"  {text}")

        # 統計カード
        stats = slide.find_all(class_=lambda x: x and ('stat' in str(x) or 'number' in str(x) or 'metric' in str(x)))
        if stats:
            slide_content.append("**データ**:")
            for stat in stats:
                text = stat.get_text(strip=True)
                if text and len(text) < 100:
                    slide_content.append(f"  - {text}")

        # カード
        cards = slide.find_all(class_=lambda x: x and 'card' in str(x))
        if cards:
            slide_content.append("**カード**:")
            for card in cards:
                card_title = card.find(['h3', 'h4', 'strong'])
                card_text = card.get_text(strip=True)
                if card_title:
                    slide_content.append(f"  - {card_title.get_text(strip=True)}")
                elif card_text and len(card_text) < 200:
                    slide_content.append(f"  - {card_text[:100]}...")

        # タイムラインやステップ
        steps = slide.find_all(class_=lambda x: x and ('step' in str(x) or 'timeline' in str(x)))
        if steps:
            slide_content.append("**ステップ**:")
            for step in steps:
                text = step.get_text(strip=True)
                if text and len(text) < 150:
                    slide_content.append(f"  - {text[:100]}")

        # セクション区切りの場合
        if 'section-divider' in slide.get('class', []):
            section_num = slide.find(class_='section-number')
            section_title = slide.find(class_='section-title')
            if section_num and section_title:
                slide_content.append(f"**セクション**: {section_num.get_text(strip=True)} {section_title.get_text(strip=True)}")

        # クラス情報
        classes = slide.get('class', [])
        slide_content.append(f"**スライドタイプ**: {', '.join(classes)}")

        output.append('\n'.join(slide_content))

    return '\n\n---\n'.join(output)


if __name__ == '__main__':
    content = extract_slides('/Users/michibikumac4/recruitment-slides-html/index.html')
    print(content)

    # ファイルに保存
    with open('/Users/michibikumac4/recruitment-slides-html/slides_content.md', 'w', encoding='utf-8') as f:
        f.write("# TechNova採用説明会スライド内容\n\n")
        f.write(content)

    print("\n\n✅ slides_content.md に保存しました")
