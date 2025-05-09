import streamlit as st
import pandas as pd

# セッション初期化
if "logs" not in st.session_state:
    st.session_state["logs"] = {
        "1Q": [],
        "2Q": [],
        "3Q": [],
        "4Q": [],
        "OT": []
    }

st.title("バスケ・プレイバイプレイ記録アプリ")

quarter = st.selectbox("クォーターを選択", ["1Q", "2Q", "3Q", "4Q", "OT"])

with st.form("play_form"):
    col1, col2 = st.columns(2)
    with col1:
        minute = st.selectbox("分", list(range(0, 11)))
    with col2:
        second = st.selectbox("秒", list(range(0, 60)))
    time = f"{minute:02}:{second:02}"

    team = st.selectbox("チーム", ["濃色", "淡色"])
    player = st.text_input("背番号", "4")
    play_type = st.selectbox(
        "プレイの種類",
        [
            "3Pシュート（成功）",
            "3Pシュート（失敗）",
            "2Pシュート（成功）",
            "2Pシュート（失敗）",
            "フリースロー（成功）",
            "フリースロー（失敗）",
            "リバウンド（オフェンス）",
            "リバウンド（ディフェンス）",
            "ターンオーバー",
            "ファウル",
            "アウトオブバウンズ",
            "スティール",
            "ブロック",
        ]
    )
    fouled = st.text_input("ファウルされた選手（ファウル時のみ）", "")
    stolen_from = st.text_input("スティール対象の選手（スティール時のみ）", "")
    submitted = st.form_submit_button("記録")

    if submitted:
        points = 0
        if play_type == "ファウル" and fouled:
            text = f"{team} {player} がファウル（{fouled} へのファウル）"
        elif play_type == "スティール" and stolen_from:
            text = f"{team} {player} がスティール（{stolen_from} から）"
        elif play_type == "3Pシュート（成功）":
            text = f"{team} {player} が3ポイントシュート成功"
            points = 3
        elif play_type == "2Pシュート（成功）":
            text = f"{team} {player} が2ポイントシュート成功"
            points = 2
        elif play_type == "フリースロー（成功）":
            text = f"{team} {player} がフリースロー成功"
            points = 1
        else:
            text = f"{team} {player} が{play_type}"

        st.session_state["logs"][quarter].append({
            "クォーター": quarter,
            "時間": time,
            "チーム": team,
            "選手": player,
            "内容": text,
            "プレイ種別": play_type,
            "得点": points
        })
        st.success(f"{quarter} に記録しました！")

# プレイログ表示
st.subheader(f"{quarter} のプレイログ")

# チームごとの得点を計算
team_scores = {}
for q in ["1Q", "2Q", "3Q", "4Q", "OT"]:
    for entry in st.session_state["logs"][q]:
        team = entry["チーム"]
        team_scores[team] = team_scores.get(team, 0) + entry["得点"]

# ログ表示
for entry in st.session_state["logs"][quarter]:
    team = entry["チーム"]
    score_info = f"（+{entry['得点']}点）" if entry["得点"] > 0 else ""
    current_score = f"{team_scores.get(team, 0)}点"
    st.write(f"[{entry['時間']}] {entry['内容']} {score_info} | 現在の得点: {current_score}")

# ボックススコア表示
st.subheader("ボックススコア（全クォーター）")

def build_box_score(logs):
    stats = {}
    for entry in logs:
        p = entry["選手"]
        play = entry["プレイ種別"]
        stats.setdefault(p, {
            "PTS": 0,
            "FGM": 0, "FGA": 0,
            "3FGM": 0, "3FGA": 0,
            "2FGM": 0, "2FGA": 0,
            "FTM": 0, "FTA": 0,
            "OREB": 0, "DREB": 0,
            "TO": 0,
            "ST": 0,
            "BLK": 0,
            "PF": 0
        })

        if "3Pシュート" in play:
            stats[p]["3FGA"] += 1
            stats[p]["FGA"] += 1
            if "成功" in play:
                stats[p]["3FGM"] += 1
                stats[p]["FGM"] += 1
                stats[p]["PTS"] += 3
        elif "2Pシュート" in play:
            stats[p]["2FGA"] += 1
            stats[p]["FGA"] += 1
            if "成功" in play:
                stats[p]["2FGM"] += 1
                stats[p]["FGM"] += 1
                stats[p]["PTS"] += 2
        elif "フリースロー" in play:
            stats[p]["FTA"] += 1
            if "成功" in play:
                stats[p]["FTM"] += 1
                stats[p]["PTS"] += 1
        elif "リバウンド（オフェンス）" == play:
            stats[p]["OREB"] += 1
        elif "リバウンド（ディフェンス）" == play:
            stats[p]["DREB"] += 1
        elif "ターンオーバー" == play:
            stats[p]["TO"] += 1
        elif "スティール" == play:
            stats[p]["ST"] += 1
        elif "ブロック" == play:
            stats[p]["BLK"] += 1
        elif "ファウル" in play:
            stats[p]["PF"] += 1

    df = pd.DataFrame(stats).T
    df["FG%"] = (df["FGM"] / df["FGA"]).replace([float('inf'), float('nan')], 0).apply(lambda x: f"{x:.1%}")
    df["2FG%"] = (df["2FGM"] / df["2FGA"]).replace([float('inf'), float('nan')], 0).apply(lambda x: f"{x:.1%}")
    df["3FG%"] = (df["3FGM"] / df["3FGA"]).replace([float('inf'), float('nan')], 0).apply(lambda x: f"{x:.1%}")
    df["FT%"] = (df["FTM"] / df["FTA"]).replace([float('inf'), float('nan')], 0).apply(lambda x: f"{x:.1%}")
    return df

all_logs = sum(st.session_state["logs"].values(), [])
if all_logs:
    box_score_df = build_box_score(all_logs)
    st.dataframe(box_score_df)

    st.download_button(
        label="ボックススコアCSVをダウンロード",
        data=box_score_df.to_csv().encode("utf-8"),
        file_name="box_score.csv",
        mime="text/csv"
    )

    raw_log_df = pd.DataFrame(all_logs)
    st.download_button(
        label="プレイバイプレイCSVをダウンロード",
        data=raw_log_df.to_csv(index=False).encode("utf-8"),
        file_name="play_by_play_log.csv",
        mime="text/csv"
    )

if st.button("すべてのログをクリア"):
    for key in st.session_state["logs"]:
        st.session_state["logs"][key] = []
    st.warning("すべてのログをクリアしました")