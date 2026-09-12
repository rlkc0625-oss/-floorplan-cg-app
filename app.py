import base64
import io
import os
from pathlib import Path

import streamlit as st
from PIL import Image
from openai import OpenAI

st.set_page_config(
    page_title="図面→内観CGメーカー",
    page_icon="🏠",
    layout="centered",
)

st.title("🏠 図面 → 内観CGメーカー")
st.caption("図面を1枚添付して、間取りをできるだけ維持した完成イメージを作るMVP")

with st.sidebar:
    st.header("設定")
    api_key = st.text_input("OpenAI API Key", type="password",
                            help="APIキーはこの実行中のセッションでのみ使用します。公開リポジトリには保存しないでください。")
    st.divider()
    style = st.selectbox(
        "インテリアテイスト",
        ["ナチュラル", "グレージュモダン", "ホテルライク", "北欧", "和モダン", "シンプルモダン", "自由指定"]
    )
    view = st.selectbox(
        "視点",
        ["LDK全体", "リビング側からキッチンを見る", "キッチン側からリビングを見る",
         "ダイニング側からLDKを見る", "玄関ホール", "自由指定"]
    )
    lighting = st.selectbox("時間帯", ["昼", "夕方", "夜"])
    realism = st.select_slider("リアルさ", options=["標準", "高め", "最高"], value="高め")
    extra = st.text_area(
        "追加指定",
        placeholder="例：床は明るい木目。壁は淡いグレージュ。大開口から庭が見える。家具は少なめ。",
        height=120,
    )

uploaded = st.file_uploader(
    "① 図面を添付してください",
    type=["png", "jpg", "jpeg", "webp", "pdf"],
    help="まずは平面図1枚でOKです。"
)

if uploaded:
    if uploaded.type == "application/pdf":
        st.warning("PDF図面はMVPでは画像化が必要です。まずはPNG/JPGの平面図をおすすめします。")
    else:
        img = Image.open(uploaded)
        st.image(img, caption="添付した図面", use_container_width=True)

st.markdown("### ② CGを作成")
st.info("このMVPは「図面の形・壁・開口部・部屋配置をできるだけ維持し、内装・家具・照明・質感を加える」方針です。AI生成なので、建築確認用の正確な3D CAD/BIMではありません。")

if st.button("✨ CGを作成", type="primary", use_container_width=True):
    if not api_key:
        st.error("OpenAI API Keyを入力してください。")
        st.stop()
    if not uploaded or uploaded.type == "application/pdf":
        st.error("PNG / JPG / JPEG / WEBP の図面を1枚添付してください。")
        st.stop()

    client = OpenAI(api_key=api_key)

    style_text = {
        "ナチュラル":"明るく落ち着いたナチュラルインテリア",
        "グレージュモダン":"上品なグレージュを基調にしたモダンインテリア",
        "ホテルライク":"高級感のあるホテルライクなインテリア",
        "北欧":"明るく温かい北欧系インテリア",
        "和モダン":"木質感を活かした上品な和モダン",
        "シンプルモダン":"余白を活かしたシンプルモダン",
        "自由指定": extra or "上品で自然な住宅インテリア",
    }[style]

    view_text = {
        "LDK全体":"LDK全体を見渡せる自然なアイレベルの内観",
        "リビング側からキッチンを見る":"リビング側からキッチン方向を見る視点",
        "キッチン側からリビングを見る":"キッチン側からリビング方向を見る視点",
        "ダイニング側からLDKを見る":"ダイニング側からLDK全体を見る視点",
        "玄関ホール":"玄関ホールから室内を見る視点",
        "自由指定": extra or "自然な住宅内観の視点",
    }[view]

    realism_text = {
        "標準":"自然な住宅CG",
        "高め":"高品質で写実的な住宅完成イメージCG",
        "最高":"非常に写実的で高精細な住宅完成イメージCG",
    }[realism]

    prompt = f"""
この入力画像は住宅の平面図です。
この平面図を参照して、同じ住宅の内観完成イメージを作成してください。

最重要ルール：
- 平面図から読み取れる壁の位置、部屋の配置、主要な開口部、キッチン位置、建具位置、空間のつながりをできるだけ維持する。
- 平面図にない壁、窓、ドア、部屋、階段、家具を勝手に追加しない。
- 指定していない間取り変更を行わない。
- 入力図面を別の間取りに描き直さない。
- 建築図面としての形状を尊重し、現実的な住宅内観として視覚化する。
- 商品名、メーカー名、品番、ロゴ、架空の商品名、文字看板は入れない。

視点：
{view_text}

インテリア：
{style_text}

時間帯：
{lighting}

表現：
{realism_text}

追加指定：
{extra or "特になし"}

平面図から判断できない寸法・高さ・窓仕様などは、無理に断定せず自然な住宅CGとして補完する。
ただし、補完によって間取りを変更しない。
"""
    with st.spinner("CGを生成しています…少し時間がかかります。"):
        try:
            # Streamlit/iPhone uploads can arrive as application/octet-stream.
            # Re-encode the uploaded image to PNG and explicitly send a valid
            # filename + MIME type so the OpenAI Images API accepts it.
            source = Image.open(io.BytesIO(uploaded.getvalue())).convert("RGB")
            normalized = io.BytesIO()
            source.save(normalized, format="PNG")
            normalized.seek(0)

            result = client.images.edit(
                model="gpt-image-2",
                image=("floorplan.png", normalized, "image/png"),
                prompt=prompt,
                size="1536x1024",
                quality="medium",
            )
            b64 = result.data[0].b64_json
            out = base64.b64decode(b64)
            st.success("CGが完成しました。")
            st.image(out, caption="生成された内観CG", use_container_width=True)
            st.download_button(
                "⬇️ CGを保存",
                data=out,
                file_name="floorplan_cg.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception as e:
            st.error("生成に失敗しました。")
            st.code(str(e))

st.divider()
st.caption("MVP：図面→内観CG。今後、外観CG・複数アングル・素材指定・修正指示・履歴保存などを追加できます。")
