import streamlit as st
import pandas as pd
import plotly.express as px
import os
from utils.lottery_data import LotteryData
from dashscope import Generation
#from dotenv import load_dotenv

#load_dotenv()
# 设置通义千问API密钥
#os.environ['DASHSCOPE_API_KEY'] = 'sk-9ba1cc2cb3fc47bfba260c6e795f6931'  # 替换为你的实际API密钥

def get_prediction(history_data):
    """调用通义千问API获取预测结果"""
    prompt = f"""作为一个数据分析专家，请分析以下数据并预测下一期可能出现的号码。
    
    {history_data}
    
    请给出下一期的预测号码，格式要求：
    1. 红球6个号码（01-33）
    2. 蓝球1个号码（01-16）
    3. 只需要给出号码，格式如：01,02,03,04,05,06|07
    """
    
    try:
        response = Generation.call(
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            model='qwen-plus',  # 或 'qwen-plus'
            prompt=prompt,
            temperature=0.7,
            top_p=0.8,
            result_format='message'
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content.strip()
        else:
            st.error(f"API调用失败: {response.code} - {response.message}")
            return None
            
    except Exception as e:
        st.error(f"预测出错: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="双色球数据分析与预测", page_icon="🎯", layout="wide")
    
    st.title("🎯 双色球数据分析与预测系统")
    
    lottery = LotteryData()
    
    # 获取历史数据
    with st.spinner('正在获取最新开奖数据...'):
        df = lottery.fetch_history(30)
    
    if df is not None:
        # 显示最新一期开奖结果
        st.subheader("📊 最新开奖结果")
        latest = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("期号", latest['期号'])
        with col2:
            st.metric("开奖日期", latest['开奖日期'])
        with col3:
            st.metric("中奖号码", f"红球: {latest['红球']} 蓝球: {latest['蓝球']}")
        
        # 显示历史数据表格
        st.subheader("📜 历史开奖记录")
        st.dataframe(df[['期号', '开奖日期', '红球', '蓝球']], use_container_width=True)
        
        # 号码频率分析
        st.subheader("📈 号码出现频率分析")
        col1, col2 = st.columns(2)
        
        with col1:
            # 红球频率统计
            red_numbers = ','.join(df['红球'].tolist()).split(',')
            red_freq = pd.Series(red_numbers).value_counts().sort_index()
            fig_red = px.bar(red_freq, 
                           title='红球出现频率',
                           labels={'index': '号码', 'value': '出现次数'})
            st.plotly_chart(fig_red, use_container_width=True)
            
        with col2:
            # 蓝球频率统计
            blue_freq = df['蓝球'].value_counts().sort_index()
            fig_blue = px.bar(blue_freq, 
                            title='蓝球出现频率',
                            labels={'index': '号码', 'value': '出现次数'})
            st.plotly_chart(fig_blue, use_container_width=True)
        
        # AI预测
        st.subheader("🤖 AI预测下期号码")
        if st.button("获取预测"):
            with st.spinner('正在分析历史数据，生成预测结果...'):
                history_text = lottery.format_numbers_for_prompt(df)
                prediction = get_prediction(history_text)
                if prediction:
                    st.success(f"预测号码: {prediction}")
                    st.caption("⚠️ 声明：此预测仅供参考，不构成购彩建议。彩票有风险，投注需谨慎。")
    else:
        st.error("获取数据失败，请稍后重试")

if __name__ == "__main__":
    main() 