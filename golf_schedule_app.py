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
    time_options = [datetime.time(h, m) for h in range(7, 11) for m in range(0, 60, 1)]  # 7時〜10時59分まで1分刻み
    start_time = st.selectbox("⏱️ スタート時刻", time_options, index=time_options.index(datetime.time(7, 0)))
    start_interval = st.number_input("⏳ スタート間隔（分）", min_value=1, max_value=60, value=8)
with col2:
    hole_duration = st.number_input("⛳ ホール所要時間（分）", min_value=1, max_value=60, value=9)
    num_holes = st.number_input("🏌️‍♂️ ホール数", min_value=1, max_value=18, value=18)
with col3:
    num_groups = st.number_input("👥 組数", min_value=1, max_value=40, value=10)

auto_calculate = st.checkbox("入力後に自動計算を有効化", value=False)
special_mode = st.checkbox("🎯 特別スタート時間（手動リスト）を使う", value=False)

# スケジュール計算関数
def calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes, special_mode=False):
    schedule = []
    today = datetime.date.today()

    # 特別モード：手動スタート時間リスト
    if special_mode:
        manual_times = [
            datetime.time(7, 0),
            datetime.time(7, 8),
            datetime.time(7, 15),
            datetime.time(7, 23),
            datetime.time(7, 30),
            datetime.time(7, 38),
            # 必要ならここにさらに追加！
        ]
    else:
        manual_times = []

    for group in range(1, num_groups + 1):
        group_schedule = {"組番号": f"{group}組"}

        if special_mode:
            if group <= len(manual_times):
                group_start = datetime.datetime.combine(today, manual_times[group - 1])
            else:
                st.error(f"⚠️ 組数が手動リスト({len(manual_times)}個)を超えています！手動リストを増やしてください。")
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
            df = calculate_schedule(start_time, start_interval, hole_duration, num_groups, num_holes, special_mode=special_mode)
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
                        data=schedule.to_csv(index=False, encoding="utf-8-sig"),
                        file_name=f"golf_schedule_{idx + 1}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("保存されたスケジュールはありません。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
