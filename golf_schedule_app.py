
import streamlit as st
import pandas as pd
import datetime

# タイトルと説明
st.title("⛳ ゴルフ巡回スケジュール作成ツール")
st.markdown("""
    スタート時刻や間隔を入力するだけで、組ごとの巡回スケジュールを自動作成します！  
    最大 **40組**、**18ホール** に対応しています。設定を入力してスケジュールを計算してください。
""")

# 入力セクション
st.header("📋 スケジュール設定")

col1, col2, col3 = st.columns(3)
with col1:
    start_time = st.time_input("⏱️ スタート時刻", datetime.time(9, 0))
    start_interval = st.number_input("⏳ スタート間隔（分）", min_value=1, max_value=60, value=8)
with col2:
    hole_duration = st.number_input("⛳ ホール所要時間（分）", min_value=1, max_value=60, value=9)
    num_holes = st.number_input("🏌️‍♂️ ホール数", min_value=1, max_value=18, value=18)
with col3:
    num_groups = st.number_input("👥 組数", min_value=1, max_value=40, value=10)

auto_calculate = st.checkbox("入力後に自動計算を有効化", value=False)

# スケジュール計算関数
def calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes):
    schedule = []
    start_time = datetime.datetime.combine(datetime.date.today(), start_time)

    for group in range(1, num_groups + 1):
        group_schedule = {"組番号": f"{group}組"}
        current_time = start_time + datetime.timedelta(minutes=(group - 1) * start_interval)
        group_schedule["スタート時刻"] = current_time.strftime("%H:%M")
        
        for hole in range(1, num_holes + 1):
            group_schedule[f"ホール {hole}"] = current_time.strftime("%H:%M")
            current_time += datetime.timedelta(minutes=hole_duration)
        
        schedule.append(group_schedule)

    return pd.DataFrame(schedule)

# 計算実行
if st.button("🚀 スケジュールを計算") or auto_calculate:
    try:
        if num_groups < 1 or num_holes < 1:
            st.error("⚠️ 組数とホール数は1以上に設定してください。")
        else:
            # 計算
            df = calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes)
            st.success("スケジュールが計算されました！以下の表をご確認ください。")
            
            # 結果表示
            st.dataframe(df, use_container_width=True)

            # スケジュール保存
            if 'saved_schedules' not in st.session_state:
                st.session_state.saved_schedules = []

            st.session_state.saved_schedules.append(df)
            
            # 保存したスケジュールの選択
            st.header("💾 保存されたスケジュール")
            if len(st.session_state.saved_schedules) > 0:
                for idx, schedule in enumerate(st.session_state.saved_schedules):
                    st.write(f"**スケジュール {idx + 1}**")
                    st.dataframe(schedule)
                    st.download_button(
                        label=f"📥 スケジュール {idx + 1} をダウンロード",
                        data=schedule.to_csv(index=False, encoding="utf-8-sig"),  # BOM付きUTF-8エンコーディングを使用
                        file_name=f"golf_schedule_{idx + 1}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("保存されたスケジュールはありません。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
