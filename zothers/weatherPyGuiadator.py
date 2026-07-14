import os.path
from pyguiadapter.adapter.adapter import GUIAdapter

# 1. 定义一个带有类型注解的函数，这就是你的核心业务逻辑
def create_file(path: str, filename: str, content: str, overwrite: bool = False):
    """一个简单的文件创建工具"""
    full_path = os.path.join(path, filename)
    text = "TEST ONLY"
    if not os.path.isfile(full_path) or overwrite:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件已创建: {full_path}"
    return "文件已存在，且未选择覆盖。"

if __name__ == "__main__":
    # 2. 创建适配器
    gui_adapter = GUIAdapter()
    # 3. 添加你的函数
    gui_adapter.add(create_file)
    # 4. 运行 GUI 应用
    gui_adapter.run()