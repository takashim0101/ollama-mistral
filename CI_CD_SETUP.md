# GitHub Actions CI/CD Setup Guide

## CI/CD パイプライン

### 1. CI - Build and Test (`ci.yml`)
- コミット/PR 時に実行
- Python 依存関係のインストール
- Linting（flake8）
- Docker イメージのビルド
- Docker Compose で起動
- API エンドポイントのテスト

**トリガー:**
- `main` ブランチへの push
- `develop` ブランチへの push
- PR 作成

### 2. CD - Build and Push (`cd.yml`)
- Docker イメージをビルド
- GitHub Container Registry（ghcr.io）へプッシュ
- Docker Hub へもプッシュ（オプション）

**トリガー:**
- `main` ブランチへの push
- タグ作成時（v1.0.0 など）

### 3. Deploy - Production (`deploy.yml`)
- CD 完了後に本番サーバーにデプロイ
- SSH で本番マシンに接続
- Docker Compose で起動
- Slack 通知

**トリガー:**
- CD ワークフロー完了時

## セットアップ手順

### Step 1: GitHub リポジトリを作成

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/ollama-mistral.git
git branch -M main
git add .
git commit -m "Initial commit: Ollama + Mistral 7B setup"
git push -u origin main
```

### Step 2: GitHub Secrets を設定

リポジトリの `Settings → Secrets and variables → Actions` で以下を追加：

#### Docker Hub（オプション）
```
DOCKER_USERNAME = your_docker_username
DOCKER_PASSWORD = your_docker_token
```

#### 本番デプロイ用
```
DEPLOY_HOST = your-server-ip-or-domain.com
DEPLOY_USER = deploy_user
DEPLOY_KEY = (SSH 秘密鍵)
DEPLOY_PATH = /home/deploy_user/ollama-mistral
```

#### Slack 通知（オプション）
```
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 3: SSH キーペアを生成（本番デプロイ用）

```bash
ssh-keygen -t ed25519 -f deploy_key -N ""
```

- `deploy_key` — GitHub Secrets に `DEPLOY_KEY` として登録
- `deploy_key.pub` — 本番サーバーの `~/.ssh/authorized_keys` に追加

### Step 4: 本番サーバーの準備

```bash
# 本番サーバー
mkdir -p /home/deploy_user/ollama-mistral
cd /home/deploy_user/ollama-mistral

# Docker, Docker Compose がインストール済みか確認
docker --version
docker compose --version

# Git リポジトリ初期化
git clone https://github.com/YOUR_USERNAME/ollama-mistral.git .
cp .env.production .env
```

## ワークフロー実行フロー

```
1. コミット push
   ↓
2. GitHub Actions CI 実行
   - テスト ✓
   - ビルド ✓
   ↓
3. CD ワークフロー実行
   - Docker イメージをビルド
   - ghcr.io へプッシュ ✓
   ↓
4. Deploy ワークフロー実行
   - 本番サーバーに SSH 接続
   - git pull
   - docker compose 更新
   - コンテナ再起動 ✓
   ↓
5. Slack 通知（デプロイ完了）
```

## GitHub Actions ステータス確認

リポジトリの `Actions` タブで以下が表示されます：

- ✓ CI パイプラインの実行状況
- ✓ テスト結果
- ✓ ビルド状況
- ✓ デプロイ履歴

## トラブルシューティング

### CI が失敗する場合
```bash
# ローカルでテスト
docker compose up -d --wait
curl http://localhost:8000/health
```

### CD が失敗する場合
- Secrets が正しく設定されているか確認
- Docker Hub クレデンシャルが正しいか確認

### Deploy が失敗する場合
- SSH キーが正しく設定されているか確認
- 本番サーバーが起動しているか確認
- `DEPLOY_PATH` が存在するか確認

## 本番環境チェックリスト

- [ ] SSH キーペアを生成
- [ ] GitHub Secrets を設定
- [ ] 本番サーバーに SSH アクセス確認
- [ ] Docker Compose が本番にインストール済み
- [ ] `.env.production` を本番サーバーにコピー
- [ ] ファイアウォール設定（ポート公開）

## 参考

- [GitHub Actions ドキュメント](https://docs.github.com/ja/actions)
- [Docker setup-buildx-action](https://github.com/docker/setup-buildx-action)
- [GitHub Container Registry](https://docs.github.com/ja/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
