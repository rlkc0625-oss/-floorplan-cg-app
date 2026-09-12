# 図面→内観CGメーカー

スマホのブラウザから、住宅平面図をアップロードして内観CGを生成するStreamlit MVPです。

## 必要なもの
- GitHubアカウント
- Streamlit Community Cloud
- OpenAI APIキー

## 公開方法（スマホでも可）
1. GitHubで新しいPublicリポジトリを作成
2. このフォルダの `app.py` / `requirements.txt` / `.streamlit/config.toml` / `.gitignore` / `README.md` をアップロード
3. Streamlit Community CloudでGitHubリポジトリを選択し、`app.py` をMain fileにしてDeploy
4. StreamlitのSettings/Secretsに以下を登録（任意）

```toml
OPENAI_API_KEY = "sk-..."
```

APIキーをGitHubへ直接書き込まないでください。

## 注意
これは建築確認用CAD/BIMではなく、平面図を参照したAIによる完成イメージ生成です。壁・窓・ドア等をできるだけ維持する指示を入れていますが、寸法精度や完全な形状維持は保証できません。
