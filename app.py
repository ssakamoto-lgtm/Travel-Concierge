import streamlit as st
from google import genai
import os  #
# --- 設定 ---
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません（Secretsを確認してください）")
    st.stop()
client = genai.Client(api_key=api_key)

# --- UI ---
st.set_page_config(page_title="Travel Concierge", page_icon="✈️")

st.title("✈️ Travel Concierge")
st.subheader("あなたの旅の記憶")

col1, col2 = st.columns(2)

with col1:
    past_countries = st.text_input("過去に行った国", placeholder="例：フィンランド")

with col2:
    past_prefectures = st.text_input("過去に行った都道府県", placeholder="例：北海道")

past_detail = st.text_area("印象に残っている宿やエピソード", height=100)
request = st.text_area("今回の気分や、外せない条件", height=100)

submitted = st.button("AIにプランを相談する")

# --- AI処理 ---
if submitted:
    if not request:
        st.warning("「今回の気分や要望」を入力してください。")
    else:
        prompt = f"""
あなたは高級ホテルの旅行コンシェルジュです。

過去の旅行: {past_countries}, {past_prefectures}
印象: {past_detail}
要望: {request}

# 必ず守る
タイトル：
旅行先：（地域名＋ホテル名を「」で囲む）
理由：
プラン：
・朝：
・昼：
・夜：
"""

        with st.spinner("AIがあなたの旅を分析中..."):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                result = response.text if hasattr(response, "text") else str(response)

                if not result or len(result) < 20:
                    raise Exception("empty")

            except Exception:
                st.warning("💡 AIが混雑中のため、推奨プランを表示します")

                # --- フォールバック ---
                if "温泉" in request or "露天風呂" in request:
                    result = """
タイトル：♨️ 静寂と湯に包まれる大人の隠れ家
旅行先：箱根・強羅「ふふ箱根」
理由：全室露天風呂付きで癒しの時間。
プラン：
・朝：露天風呂と朝食
・昼：美術館巡り
・夜：懐石料理
"""
                elif "海" in request:
                    result = """
タイトル：🌊 海に癒されるリゾート旅
旅行先：熱海「星野リゾート リゾナーレ熱海」
理由：海と非日常体験。
プラン：
・朝：海を見ながら朝食
・昼：カフェ巡り
・夜：ディナー
"""
                elif "自然" in request:
                    result = """
タイトル：🌿 森のリトリート旅
旅行先：軽井沢「星のや軽井沢」
理由：自然と静けさ。
プラン：
・朝：森の散歩
・昼：カフェ巡り
・夜：温泉
"""
                elif "海外" in request:
                    result = """
タイトル：🇫🇮 北欧の癒し旅
旅行先：フィンランド「Kakslauttanen Arctic Resort」
理由：オーロラ体験。
プラン：
・朝：雪景色
・昼：サウナ
・夜：オーロラ
"""
                else:
                    result = """
タイトル：🌏 あなただけのバランス旅
旅行先：福岡・糸島「seven x seven 糸島」
理由：自然とカフェの融合。
プラン：
・朝：海散歩
・昼：カフェ巡り
・夜：地元グルメ
"""

        # --- 表示 ---
        st.markdown("---")
        st.subheader("🧭 あなたへのおすすめプラン")
        st.success("✨ あなたにぴったりの「新天地」が見つかりました！")
        st.balloons()

        lines = result.split("\n")

        for line in lines:
            if "タイトル" in line:
                st.header("✨ " + line.replace("タイトル：", ""))

            elif "旅行先" in line:
                place = line.replace("旅行先：", "")

                if "「" in place and "」" in place:
                    area = place.split("「")[0]
                    hotel = place.split("「")[1].replace("」", "")

                    st.subheader("📍 " + area)
                    st.write("🏨 **" + hotel + "**")

                    # 🔗 検索リンク生成
                    ikyu_url = "https://www.ikyu.com/"
                    expedia_url = f"https://www.expedia.co.jp/Hotel-Search?destination={hotel}"

                    st.markdown(f"[🔗 一休で見る]({ikyu_url})")
                    st.markdown(f"[🔗 Expediaで見る]({expedia_url})")

                else:
                    st.subheader("📍 " + place)

            elif "理由" in line:
                st.write("💡 " + line.replace("理由：", ""))

            elif "プラン" in line:
                st.write("🗓️ プラン")

            elif "朝" in line:
                st.write("🌅 " + line)

            elif "昼" in line:
                st.write("🍽️ " + line)

            elif "夜" in line:
                st.write("🌙 " + line)
