import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from stock_analyzer import StockAnalyzer
from data_cache import DataCache
import requests
import time
from config import SYSTEM_CONFIG, API_CONFIG

# 初始化缓存系统
cache = DataCache()

def check_network():
    """检查网络连接状态"""
    try:
        requests.get(f"https://{SYSTEM_CONFIG['DOMAIN']}", timeout=3)
        return True
    except:
        return False

def plot_stock_chart(data, indicators):
    """绘制股票图表"""
    # 创建子图
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # 添加K线图
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['开盘'],
            high=data['最高'],
            low=data['最低'],
            close=data['收盘'],
            name='K线'
        ),
        row=1, col=1
    )
    
    # 添加均线
    for ma in ['MA5', 'MA10', 'MA20', 'MA60']:
        fig.add_trace(
            go.Scatter(x=data.index, y=data[ma], name=ma),
            row=1, col=1
        )
    
    # 添加MACD
    fig.add_trace(
        go.Bar(x=data.index, y=data['MACD_Hist'], name='MACD柱'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=data['MACD'], name='MACD'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=data['MACD_Signal'], name='Signal'),
        row=2, col=1
    )
    
    # 添加RSI
    fig.add_trace(
        go.Scatter(x=data.index, y=data['RSI6'], name='RSI6'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=data['RSI12'], name='RSI12'),
        row=3, col=1
    )
    
    # 添加成交量
    colors = ['red' if row['收盘'] >= row['开盘'] else 'green' for _, row in data.iterrows()]
    fig.add_trace(
        go.Bar(x=data.index, y=data['成交量'], name='成交量', marker_color=colors),
        row=4, col=1
    )
    
    # 更新布局
    fig.update_layout(
        title='股票技术分析图表',
        xaxis_title='日期',
        yaxis_title='价格',
        height=1000,
        showlegend=True
    )
    
    return fig

def main():
    # 配置页面基本设置
    st.set_page_config(
        page_title=SYSTEM_CONFIG['SITE_NAME'],
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 添加CSS样式
    st.markdown(f"""
        <style>
        .main {{
            padding: 20px;
        }}
        .stApp {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .site-header {{
            background-color: #1f77b4;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # 检查网络状态
    is_online = check_network()
    if not is_online:
        st.warning("⚠️ 当前处于离线模式，使用演示数据进行展示")
    
    # 添加系统标题和说明
    st.markdown(f"""
    <div class='site-header'>
        <h1>{SYSTEM_CONFIG['SITE_NAME']} 📊</h1>
        <p>{SYSTEM_CONFIG['SITE_DESCRIPTION']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 初始化分析器
        analyzer = StockAnalyzer()
        
        # 侧边栏
        st.sidebar.title("功能选择")
        page = st.sidebar.radio("选择功能", ["股票分析", "股票推荐"])
        
        if page == "股票分析":
            # 股票分析页面
            st.header("股票分析")
            
            # 创建两列布局
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 添加股票搜索功能
                search_term = st.text_input("搜索股票名称或代码", help="输入股票名称或代码进行搜索")
                if search_term:
                    # 这里可以添加股票搜索逻辑
                    st.info(f"正在搜索: {search_term}")
                
                # 输入股票代码
                stock_code = st.text_input("请输入股票代码（例如：000001）", help="输入6位股票代码")
            
            with col2:
                # 添加示例按钮
                if st.button("使用示例股票"):
                    stock_code = "000001"
                    st.write("已选择示例股票：平安银行(000001)")
            
            # 选择时间范围
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期", datetime.now() - timedelta(days=365))
            with col2:
                end_date = st.date_input("结束日期", datetime.now())
            
            # 添加技术指标选择
            st.subheader("技术指标选择")
            indicators = st.multiselect(
                "选择要显示的技术指标",
                ["MACD", "RSI", "KDJ", "布林带", "成交量"],
                default=["MACD", "RSI"]
            )
            
            if st.button("开始分析", type="primary"):
                if stock_code:
                    with st.spinner("正在分析中..."):
                        # 尝试从缓存获取数据
                        cached_data = cache.get_cached_data(
                            stock_code,
                            start_date.strftime("%Y%m%d"),
                            end_date.strftime("%Y%m%d")
                        )
                        
                        if cached_data is not None:
                            result = cached_data
                        else:
                            # 获取新数据
                            result = analyzer.analyze_stock(
                                stock_code,
                                start_date.strftime("%Y%m%d"),
                                end_date.strftime("%Y%m%d")
                            )
                            # 保存到缓存
                            if result:
                                cache.save_to_cache(
                                    stock_code,
                                    start_date.strftime("%Y%m%d"),
                                    end_date.strftime("%Y%m%d"),
                                    result
                                )
                        
                        if result:
                            # 显示分析结果
                            st.success("分析完成！")
                            
                            # 显示图表
                            st.plotly_chart(
                                plot_stock_chart(result['data'], result['indicators']),
                                use_container_width=True
                            )
                            
                            # 显示分析结果
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.info("趋势分析")
                                tech = result['technical_analysis']
                                st.metric("趋势", tech['trend'])
                                st.metric("动量", tech['momentum'])
                                st.metric("波动性", tech['volatility'])
                            
                            with col2:
                                st.info("技术指标")
                                for indicator in indicators:
                                    if indicator in result['indicators']:
                                        st.write(f"{indicator}指标分析结果")
                            
                            with col3:
                                st.info("投资建议")
                                st.write(result['recommendation'])
                            
                            # 添加风险提示
                            st.warning("⚠️ 投资有风险，入市需谨慎")
                        else:
                            st.error("获取数据失败，请检查股票代码是否正确")
                else:
                    st.warning("请输入股票代码")
        
        elif page == "股票推荐":
            # 股票推荐页面
            st.header("股票推荐")
            st.info("🚧 该功能正在开发中，敬请期待...")
            
        # 添加页脚
        st.markdown("""
        <div style='text-align: center; padding: 20px; margin-top: 50px; border-top: 1px solid #eee;'>
            <p style='color: #666;'>© 2025 余氏股票分析系统 | 专业、智能、可靠的股票分析工具</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"系统出现错误: {str(e)}")
        st.info("请刷新页面重试")

if __name__ == "__main__":
    main() 