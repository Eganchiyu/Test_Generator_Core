import time
from config import Config
from errors import *


# =========================
# 主流程
# =========================

def paper_generation():
    # 加载配置
    config = Config()

# =========================
# 入口
# =========================
if __name__ == "__main__":
    sys_start_time = time.time()
    try:
        paper_generation()
    except ConfigError as e:
        print("[Generator] 配置文件不合规，请检查输入")
    print(f"\n===程序结束===\n系统总用时{time.time() - sys_start_time:.3f}s")

