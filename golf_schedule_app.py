import streamlit as st
import pandas as pd
import datetime

# タイトルと説明
st.title("⛳ ゴルフ巡回スケジュール作成ツール")
st.markdown("""
    スタート時刻や間隔を入力するだけで、組ごとの巡回スケジュールを自動作成します！  
    最大 **40組**、**18ホール** に対応しています。
""")

# 入力セクション
st.header("📋 スケジュール設定")

col1, col2, col3 = st.columns(3)
with col1:
    # 普通モード用
    time_options = [datetime.time(h, m) for h in range(7, 11) for m in range(0, 60)]
    time_options = [t for t in time_options if (t.hour < 10 or (t.hour == 10 and t.minute <= 30))]
    start_time = st.selectbox("⏱️ スタート時刻", time_options, index=0)
    start_interval = st.number_input("⏳ スタート間隔（分）", min_value=1, max_value=60, value=8)
with col2:
    hole_duration = st.number_input("⛳ ホール所要時間（分）", min_value=1, max_value=60, value=9)
    num_holes = st.number_input("🏏️ ホール数", min_value=1, max_value=18, value=18)
with col3:
    num_groups = st.number_input("👥 組数", min_value=1, max_value=40, value=10)

# 特別モード切り替え
special_mode = st.checkbox("🌟 特別スタート時間リストを使う", value=False)
manual_times = []
if special_mode:
    manual_input = st.text_input(
        "📝 スタート時刻リスト（カンマ区切り）",
        value="7:00,7:08,7:15,7:23,7:30,7:38"
    )
    try:
        manual_times = [datetime.datetime.strptime(t.strip(), "%H:%M").time() for t in manual_input.split(",")]
    except ValueError:
        st.error("⚠️ 入力フォーマットが間違っています。HH:MM形式で正しく入力して下さい。")

auto_calculate = st.checkbox("入力後に自動計算を有効化", value=False)

# スケジュール計算関数
def calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes, special_mode=False, manual_times=None):
    schedule = []
    today = datetime.date.today()

    if manual_times is None:
        manual_times = []

    for group in range(1, num_groups + 1):
        group_schedule = {"\u7d44\u756a\u53f7": f"{group}組"}

        if special_mode:
            if group <= len(manual_times):
                group_start = datetime.datetime.combine(today, manual_times[group - 1])
            else:
                st.error(f"⚠️ 組数が手動リスト({len(manual_times)}個)を超えています！")
                break
        else:
            group_start = datetime.datetime.combine(today, start_time) + datetime.timedelta(minutes=(group - 1) * start_interval)

        group_schedule["スタート時刻"] = group_start.strftime("%H:%M")

        current_time = group_start
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
            df = calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes, special_mode, manual_times)
            st.success("スケジュールが計算されました！")
            st.dataframe(df, use_container_width=True)

            if 'saved_schedules' not in st.session_state:
                st.session_state.saved_schedules = []

            st.session_state.saved_schedules.append(df)

            # 保存したスケジュール
            st.header("💾 保存されたスケジュール")
            for idx, schedule in enumerate(st.session_state.saved_schedules):
                st.write(f"**スケジュール {idx + 1}**")
                st.dataframe(schedule)
                st.download_button(
                    label=f"📅 スケジュール {idx + 1} をダウンロード",
                    data=schedule.to_csv(index=False, encoding="utf-8-sig"),
                    file_name=f"golf_schedule_{idx + 1}.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
