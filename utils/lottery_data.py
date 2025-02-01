import requests
import pandas as pd
from datetime import datetime

class LotteryData:
    def __init__(self):
        self.base_url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def fetch_history(self, limit=30):
        params = {
            'name': 'ssq',
            'pageNo': 1,
            'pageSize': limit,
            'systemType': 'PC'
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data['result']:
                red_balls = [int(n) for n in item['red'].split(',')]
                blue_ball = int(item['blue'])
                
                result = {
                    '期号': item['code'],
                    '开奖日期': item['date'],
                    '红球': item['red'],
                    '蓝球': item['blue'],
                    '红球列表': red_balls,
                    '蓝球数字': blue_ball
                }
                results.append(result)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"获取数据时发生错误: {e}")
            return None

    def format_numbers_for_prompt(self, df, limit=5):
        """将最近几期的开奖号码格式化为提示文本"""
        recent_draws = df.head(limit)
        formatted_text = "最近几期双色球开奖号码：\n"
        for _, row in recent_draws.iterrows():
            formatted_text += f"第{row['期号']}期: 红球:{row['红球']} 蓝球:{row['蓝球']}\n"
        return formatted_text 