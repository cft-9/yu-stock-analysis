import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta

class StockAnalyzer:
    def __init__(self):
        """初始化股票分析器"""
        pass
    
    def get_stock_data(self, stock_code, start_date, end_date):
        """获取股票数据"""
        try:
            # 使用akshare获取A股数据
            df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date)
            
            # 重命名列
            df.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            
            # 设置日期索引
            df['日期'] = pd.to_datetime(df['日期'])
            df.set_index('日期', inplace=True)
            
            # 计算技术指标
            self._calculate_indicators(df)
            
            return df
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def _calculate_indicators(self, df):
        """计算技术指标"""
        # 计算移动平均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        
        # 计算MACD
        exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
        exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 计算RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI6'] = 100 - (100 / (1 + rs))
        df['RSI12'] = 100 - (100 / (1 + rs.rolling(window=12).mean()))
    
    def analyze_stock(self, stock_code, start_date, end_date):
        """分析股票"""
        # 获取数据
        data = self.get_stock_data(stock_code, start_date, end_date)
        if data is None:
            return None
        
        # 进行技术分析
        technical = self._analyze_technical(data)
        
        # 生成分析结果
        result = {
            'data': data,
            'technical_analysis': technical,
            'indicators': {
                'MACD': True,
                'RSI': True,
                'KDJ': False,
                '布林带': False,
                '成交量': True
            },
            'recommendation': self._generate_recommendation(technical)
        }
        
        return result
    
    def _analyze_technical(self, data):
        """进行技术分析"""
        latest = data.iloc[-1]
        ma5, ma10, ma20, ma60 = latest['MA5'], latest['MA10'], latest['MA20'], latest['MA60']
        
        # 趋势分析
        trend = "上升" if ma5 > ma20 else "下降"
        
        # 动量分析
        momentum = "强" if latest['RSI6'] > 70 else "弱" if latest['RSI6'] < 30 else "中性"
        
        # 波动性分析
        volatility = "高" if data['振幅'].mean() > 3 else "低"
        
        return {
            'trend': trend,
            'momentum': momentum,
            'volatility': volatility
        }
    
    def _generate_recommendation(self, technical):
        """生成投资建议"""
        if technical['trend'] == "上升" and technical['momentum'] == "强":
            return "建议买入"
        elif technical['trend'] == "下降" and technical['momentum'] == "弱":
            return "建议卖出"
        else:
            return "建议观望" 