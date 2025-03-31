import os
import json
import time
from config import SYSTEM_CONFIG

class DataCache:
    def __init__(self):
        """初始化缓存系统"""
        self.cache_dir = SYSTEM_CONFIG['CACHE_DIR']
        self.expiry = SYSTEM_CONFIG['CACHE_EXPIRY']
        
        # 创建缓存目录
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, stock_code, start_date, end_date):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{stock_code}_{start_date}_{end_date}.json")
    
    def get_cached_data(self, stock_code, start_date, end_date):
        """获取缓存数据"""
        cache_path = self._get_cache_path(stock_code, start_date, end_date)
        
        if os.path.exists(cache_path):
            # 检查缓存是否过期
            if time.time() - os.path.getmtime(cache_path) < self.expiry:
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return None
        return None
    
    def save_to_cache(self, stock_code, start_date, end_date, data):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(stock_code, start_date, end_date)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False 