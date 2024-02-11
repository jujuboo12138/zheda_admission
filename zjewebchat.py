import streamlit as st
from admission import process_question  # 确保process_question类已经正确导入
import pandas as pd  # 导入pandas库
import os

csv_user_info = '/mnt/qwen_test/zheda_admission/zje_chatset/user_info.csv'

# 如果用户信息 CSV 文件不存在，则创建一个空的 DataFrame 并保存
if not os.path.exists(csv_user_info):
    user_info_df = pd.DataFrame(columns=['Name', 'Age', 'Gender', 'Province'])
    user_info_df.to_csv(csv_user_info, index=False)

# 加载用户信息 DataFrame
user_info_df = pd.read_csv(csv_user_info)

# 弹窗收集用户信息
st.sidebar.title("用户信息")
name = st.sidebar.text_input("姓名")
age = st.sidebar.number_input("年龄", min_value=0, max_value=150)
gender = st.sidebar.selectbox("性别", ["男", "女"])
province = st.sidebar.text_input("省份(如浙江省杭州市)")

# 将新用户信息添加到 DataFrame 中
if st.sidebar.button("保存"):
    new_user_info = pd.DataFrame([[name, age, gender, province]], columns=['Name', 'Age', 'Gender', 'Province'])
    user_info_df = user_info_df.append(new_user_info, ignore_index=True)
    user_info_df.to_csv(csv_user_info, index=False)
    st.sidebar.success("用户信息已保存")
    st.sidebar.title("新用户信息")
    st.sidebar.write("姓名:", name)
    st.sidebar.write("年龄:", age)
    st.sidebar.write("性别:", gender)
    st.sidebar.write("省市:", province)
# st.sidebar.markdown("浙江大学爱丁堡大学联合学院 Chat Interface")

process = process_question()

st.title("ZJE Chat Interface")

# Initialize chat history if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize saved flag if not already initialized
if "saved" not in st.session_state:
    st.session_state.saved = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if message := st.chat_input("请输入您的问题，我会尽力解答  \n(Tips：可以同时提问多个问题，但注意问题之间使用<标点符号>分割开！然后<enter>即可)"):
    st.chat_message("user").markdown(message)
    st.session_state.messages.append({"role": "user", "content": message})

    response = process.answer_question(message)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Reset saved flag to allow saving new interactions
    st.session_state.saved = False

history_csv = '/mnt/qwen_test/zheda_admission/zje_chatset/new_history.csv'

# Only save if there's new messages and they haven't been saved yet during this session
if st.session_state.messages and not st.session_state.saved:
    if not os.path.exists(history_csv):
        pd.DataFrame(columns=['role', 'content']).to_csv(history_csv, index=False)
    df = pd.DataFrame(st.session_state.messages)

    # Since we want to save every interaction but only once per session, we ensure to write only once
    df.to_csv(history_csv, mode='a', index=False, header=not os.path.exists(history_csv))
    # Mark the messages as saved
    st.session_state.saved = True


with st.expander("招生详细信息"):
    st.markdown("更多招生信息请访问[浙江大学官网](https://www.zju.edu.cn)")

df = pd.read_excel('/mnt/qwen_test/zheda_admission/zje_chatset/enrollment.xlsx')

with st.expander("各地区负责招生老师联系方式"):
    st.dataframe(df, use_container_width=True)

feedback_csv = '/mnt/qwen_test/zheda_admission/zje_chatset/feedback.csv'

# 如果用户信息 CSV 文件不存在，则创建一个空的 DataFrame 并保存
if not os.path.exists(feedback_csv):
    user_feedback = pd.DataFrame(columns=['feedback'])
    user_feedback.to_csv(feedback_csv, index=False)

# 加载用户信息 DataFrame
user_feedback = pd.read_csv(feedback_csv)

# 弹窗收集用户信息
st.sidebar.title("用户反馈")
feedback = st.sidebar.text_input("feedback")

# 将新用户信息添加到 DataFrame 中
if st.sidebar.button("提交"):
    new_user_feedback = pd.DataFrame([[feedback]], columns=['feedback'])
    user_feedback = user_feedback.append(new_user_feedback, ignore_index=True)
    user_feedback.to_csv(feedback_csv, index=False)  # Corrected line to save feedback
    st.sidebar.success("反馈提交成功，谢谢您的支持")
