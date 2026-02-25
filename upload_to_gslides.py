#!/usr/bin/env python3
"""
Google Slidesに画像を一括アップロード

使い方:
1. Google Cloud Consoleで認証情報を作成
2. credentials.jsonをこのフォルダに配置
3. python upload_to_gslides.py を実行
"""

import os
import glob
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

def get_credentials():
    """認証情報を取得"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json が見つかりません")
                print("\n以下の手順で取得してください:")
                print("1. https://console.cloud.google.com/ にアクセス")
                print("2. プロジェクトを作成/選択")
                print("3. 「APIとサービス」→「認証情報」")
                print("4. 「認証情報を作成」→「OAuthクライアントID」")
                print("5. 「デスクトップアプリ」を選択")
                print("6. JSONをダウンロードして credentials.json として保存")
                return None

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def upload_image_to_drive(drive_service, image_path):
    """画像をGoogle Driveにアップロード"""
    file_metadata = {
        'name': os.path.basename(image_path),
        'mimeType': 'image/png'
    }
    media = MediaFileUpload(image_path, mimetype='image/png')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webContentLink'
    ).execute()

    # 公開設定
    drive_service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return f"https://drive.google.com/uc?id={file['id']}"


def create_presentation(slides_service, drive_service, image_folder):
    """プレゼンテーションを作成して画像を追加"""

    # 画像ファイルを取得（ソート済み）
    images = sorted(glob.glob(os.path.join(image_folder, 'slide_*.png')))
    print(f"📊 {len(images)} 枚のスライド画像を処理します")

    # プレゼンテーション作成
    presentation = slides_service.presentations().create(
        body={'title': 'TechNova採用説明会'}
    ).execute()
    presentation_id = presentation['presentationId']
    print(f"✅ プレゼンテーション作成: https://docs.google.com/presentation/d/{presentation_id}")

    # 最初の空スライドを削除するためのID取得
    first_slide_id = presentation['slides'][0]['objectId']

    requests = []

    # 各画像をスライドとして追加
    for i, image_path in enumerate(images):
        print(f"  📤 アップロード中: {os.path.basename(image_path)} ({i+1}/{len(images)})")

        # 画像をDriveにアップロード
        image_url = upload_image_to_drive(drive_service, image_path)

        slide_id = f'slide_{i:03d}'

        # スライド作成
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'insertionIndex': i,
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        })

        # 画像を追加
        requests.append({
            'createImage': {
                'url': image_url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': 720, 'unit': 'PT'},
                        'height': {'magnitude': 405, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': 0,
                        'translateY': 0,
                        'unit': 'PT'
                    }
                }
            }
        })

    # 最初の空スライドを削除
    requests.append({
        'deleteObject': {
            'objectId': first_slide_id
        }
    })

    # バッチ実行
    print("  🔄 スライドを作成中...")
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print(f"\n🎉 完了！")
    print(f"📎 URL: https://docs.google.com/presentation/d/{presentation_id}/edit")

    return presentation_id


def main():
    print("🚀 Google Slides アップローダー")
    print("=" * 50)

    creds = get_credentials()
    if not creds:
        return

    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    image_folder = os.path.join(os.path.dirname(__file__), 'slide_images')

    if not os.path.exists(image_folder):
        print(f"❌ 画像フォルダが見つかりません: {image_folder}")
        return

    create_presentation(slides_service, drive_service, image_folder)


if __name__ == '__main__':
    main()
