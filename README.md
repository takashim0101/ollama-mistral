# Ollama + Mistral 7B Local LLM Stack

完全なローカル LLM スタック。GPU 加速、Web UI、REST API 対応。

## 特徴

- **Ollama** - Mistral 7B モデル（4.4GB）
- **Open WebUI** - ブラウザから使用可能なチャットインターフェース
- **FastAPI サーバー** - REST API エンドポイント
- **本番対応** - `.env` 管理、ヘルスチェック、ロギング
- **GPU 対応** - NVIDIA GPU で高速推論
- **Docker Compose** - ワンコマンド起動

## 前提条件

- Docker Desktop（GPU サポート有効）
- NVIDIA GPU（RTX 4060 以上推奨）
- 8GB 以上の VRAM

## インストール

```bash
git clone <repository>
cd <project>
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
pip install -r requirements-api.txt
```

## 開発環境で実行

```bash
docker compose up -d
```

### アクセス

- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

## API 使用例

### テキスト生成

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?"}'
```

### Python

```python
import requests

response = requests.post('http://localhost:8000/generate', 
    json={'prompt': 'Hello!'}
)
print(response.json()['response'])
```

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### モデル一覧

```bash
curl http://localhost:8000/models
```

## 本番環境へのデプロイ

### 1. 本番用設定を準備

```bash
cp .env.production .env.prod
# .env.prod を編集してシークレットキーなどを設定
```

### 2. リモートサーバーで実行

```bash
export $(cat .env.prod | xargs)
docker compose -f docker-compose.prod.yml up -d
```

### 3. ポートを公開（オプション）

```bash
# nginx でリバースプロキシを設定
# または AWS ALB/Load Balancer で公開
```

## ファイル構成

```
.
├── .env                      # 開発環境用環境変数
├── .env.production          # 本番用環境変数テンプレート
├── .gitignore               # Git 除外ファイル
├── Dockerfile               # Ollama コンテナ
├── Dockerfile.api           # API サーバー コンテナ
├── docker-compose.yml       # 開発環境用 Compose
├── docker-compose.prod.yml  # 本番環境用 Compose
├── api_server.py            # FastAPI サーバー
├── test_ollama.py           # テストスクリプト
├── requirements-api.txt     # Python 依存関係
└── README.md                # このファイル
```

## トラブルシューティング

### コンテナが起動しない

```bash
docker compose logs ollama
docker compose logs api-server
docker compose logs web-ui
```

### GPU が認識されない

```bash
docker run --rm --runtime=nvidia nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### メモリ不足

Mistral 7B には 8GB VRAM 必要です。確認：

```bash
nvidia-smi
```

## API エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|-------------|------|
| GET | `/` | サービス情報 |
| GET | `/health` | ヘルスチェック |
| POST | `/generate` | テキスト生成 |
| GET | `/models` | モデル一覧 |

## 停止

```bash
docker compose down
```

## クリーンアップ

```bash
docker compose down -v  # ボリュームも削除
```

## ライセンス

MIT

## 参考

- [Ollama](https://ollama.ai)
- [Open WebUI](https://github.com/open-webui/open-webui)
- [FastAPI](https://fastapi.tiangolo.com)
- [Docker](https://www.docker.com)
