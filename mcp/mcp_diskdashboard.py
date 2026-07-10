import streamlit as st
import json
import subprocess
import sys
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import streamlit.components.v1 as components

# ============ 页面配置 ============
st.set_page_config(
    page_title="磁盘信息仪表盘",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 获取磁盘信息的函数 ============
def get_disk_info():
    """调用 MCP Server 获取磁盘信息"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_diskInfoServer.py")
    
    if not os.path.exists(script_path):
        return {
            "status": "error",
            "message": f"找不到 server.py: {script_path}"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, "--call", "get_disk_info"],
            capture_output=True,
            text=False,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"执行失败 (code {result.returncode})"
            }
        
        # 解码输出
        stdout_text = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'cp936']:
            try:
                stdout_text = result.stdout.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if stdout_text is None:
            return {
                "status": "error",
                "message": "无法解码服务器输出"
            }
        
        return json.loads(stdout_text)
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "调用超时 (30秒)"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"调用失败: {str(e)}"
        }

# ============ 自定义 CSS ============
def load_css():
    st.markdown("""
    <style>
        /* 弹窗样式 */
        .popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeIn 0.3s ease;
        }
        
        .popup-content {
            background: #1e1e2e;
            border-radius: 16px;
            padding: 30px;
            max-width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: slideUp 0.3s ease;
        }
        
        .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 15px;
        }
        
        .popup-title {
            font-size: 24px;
            font-weight: 600;
            color: #ffffff;
        }
        
        .popup-close-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: #ffffff;
            font-size: 24px;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .popup-close-btn:hover {
            background: rgba(255, 0, 0, 0.3);
            transform: scale(1.05);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-label {
            color: #a0a0b0;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .disk-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .disk-name {
            font-weight: 600;
            color: #ffffff;
            font-size: 16px;
        }
        
        .disk-detail {
            color: #a0a0b0;
            font-size: 13px;
        }
        
        .progress-bar-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            height: 8px;
            margin-top: 8px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 20px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
        }
        
        .progress-bar-danger {
            background: linear-gradient(90deg, #f093fb, #f5576c);
        }
        
        .progress-bar-warning {
            background: linear-gradient(90deg, #f6d365, #fda085);
        }
    </style>
    """, unsafe_allow_html=True)

# ============ 创建弹窗 HTML ============
def create_popup_html(data):
    """创建弹窗的 HTML 内容"""
    partitions = data.get("partitions", [])
    summary = data.get("total_summary", {})
    physical_disks = data.get("physical_disks", [])
    system_info = data.get("system_info", {})
    
    # 构建分区卡片
    partitions_html = ""
    for part in partitions:
        drive = part.get('drive_letter', '未知')
        total = part.get('size_gb', 0)
        used = part.get('used_gb', 0)
        free = part.get('free_gb', 0)
        percent = part.get('usage_percent', 0)
        volume_name = part.get('volume_name', '未命名')
        fs = part.get('file_system', '未知')
        
        # 根据使用率决定颜色
        bar_class = "progress-bar"
        if percent > 90:
            bar_class = "progress-bar progress-bar-danger"
        elif percent > 70:
            bar_class = "progress-bar progress-bar-warning"
        
        partitions_html += f"""
        <div class="disk-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="disk-name">💿 {drive}</span>
                    <span class="disk-detail" style="margin-left: 10px;">{volume_name}</span>
                </div>
                <span class="disk-detail">{used:.1f}GB / {total:.1f}GB</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                <span class="disk-detail">文件系统: {fs}</span>
                <span class="disk-detail" style="color: {'#f5576c' if percent > 90 else '#fda085' if percent > 70 else '#a0a0b0'}">
                    {percent:.1f}%
                </span>
            </div>
            <div class="progress-bar-container">
                <div class="{bar_class}" style="width: {percent}%;"></div>
            </div>
        </div>
        """
    
    # 构建物理磁盘信息
    disks_html = ""
    for disk in physical_disks:
        disks_html += f"""
        <div class="disk-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="disk-name">📀 {disk.get('model', '未知')}</span>
                </div>
                <span class="disk-detail">{disk.get('size_gb', 0):.1f} GB</span>
            </div>
            <div style="display: flex; gap: 20px; margin-top: 4px;">
                <span class="disk-detail">品牌: {disk.get('manufacturer', '未知')}</span>
                <span class="disk-detail">接口: {disk.get('interface_type', '未知')}</span>
                <span class="disk-detail">状态: {disk.get('status', '未知')}</span>
            </div>
        </div>
        """
    
    return f"""
    <div class="popup-overlay" id="popupOverlay">
        <div class="popup-content">
            <div class="popup-header">
                <div>
                    <span class="popup-title">💾 磁盘信息仪表盘</span>
                    <span style="color: #a0a0b0; font-size: 14px; margin-left: 15px;">
                        {system_info.get('hostname', '未知')} @ {system_info.get('timestamp', '')[:10]}
                    </span>
                </div>
                <button class="popup-close-btn" onclick="closePopup()">✕</button>
            </div>
            
            <!-- 汇总指标 -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_size_gb', 0):.1f}</div>
                    <div class="metric-label">总容量 (GB)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_used_gb', 0):.1f}</div>
                    <div class="metric-label">已使用 (GB)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_free_gb', 0):.1f}</div>
                    <div class="metric-label">剩余 (GB)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: {'#f5576c' if summary.get('total_usage_percent', 0) > 90 else '#667eea'}; -webkit-text-fill-color: {'#f5576c' if summary.get('total_usage_percent', 0) > 90 else '#667eea'};">
                        {summary.get('total_usage_percent', 0):.1f}%
                    </div>
                    <div class="metric-label">总使用率</div>
                </div>
            </div>
            
            <!-- 分区信息 -->
            <div style="margin-bottom: 25px;">
                <h3 style="color: #ffffff; margin-bottom: 15px;">📁 分区详情</h3>
                {partitions_html}
            </div>
            
            <!-- 物理磁盘信息 -->
            <div>
                <h3 style="color: #ffffff; margin-bottom: 15px;">💾 物理磁盘</h3>
                {disks_html}
            </div>
        </div>
    </div>
    
    <script>
        function closePopup() {{
            const overlay = document.getElementById('popupOverlay');
            if (overlay) {{
                overlay.style.display = 'none';
            }}
        }}
    </script>
    """

# ============ 主页面 ============
def main():
    load_css()
    
    # 标题
    st.title("💾 磁盘信息仪表盘")
    st.markdown("点击下方按钮查看详细的磁盘信息")
    
    # 创建两列布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 刷新按钮
        if st.button("📊 打开磁盘信息仪表盘", width='stretch', type="primary"):
            with st.spinner("正在获取磁盘信息..."):
                result = get_disk_info()
                
                if isinstance(result, dict) and result.get("status") == "success":
                    data = result.get("data", {})
                    # 生成弹窗 HTML
                    popup_html = create_popup_html(data)
                    # 使用 components.html 显示弹窗
                    components.html(popup_html, height=600, scrolling=True)
                else:
                    msg = result.get('message', '未知错误') if isinstance(result, dict) else str(result)
                    st.error(f"获取磁盘信息失败: {msg}")
    
    # 显示快速摘要
    with st.expander("📊 快速查看摘要", expanded=False):
        result = get_disk_info()
        if isinstance(result, dict) and result.get("status") == "success":
            data = result.get("data", {})
            if not isinstance(data, dict):
                data = {}
            summary = data.get("total_summary", {})
            partitions = data.get("partitions", [])
            
            # 创建 DataFrame
            df_data = []
            for part in partitions:
                df_data.append({
                    "分区": part.get('drive_letter', '未知'),
                    "卷标": part.get('volume_name', '未命名'),
                    "总大小 (GB)": part.get('size_gb', 0),
                    "已使用 (GB)": part.get('used_gb', 0),
                    "剩余 (GB)": part.get('free_gb', 0),
                    "使用率 (%)": part.get('usage_percent', 0)
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, width='stretch', hide_index=True)
            
            # 显示汇总
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总容量", f"{summary.get('total_size_gb', 0):.1f} GB")
            with col2:
                st.metric("已使用", f"{summary.get('total_used_gb', 0):.1f} GB")
            with col3:
                st.metric("剩余", f"{summary.get('total_free_gb', 0):.1f} GB")
            with col4:
                st.metric("使用率", f"{summary.get('total_usage_percent', 0):.1f}%")

# ============ 使用 Plotly 创建更丰富的可视化（可选） ============
def create_plotly_dashboard(data):
    """创建 Plotly 可视化仪表盘"""
    partitions = data.get("partitions", [])
    summary = data.get("total_summary", {})
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("分区使用率", "磁盘容量分布", "使用情况对比", "使用率详情"),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "indicator"}]]
    )
    
    # 1. 分区使用率饼图
    labels = [f"{p.get('drive_letter', '未知')}" for p in partitions]
    values = [p.get('used_gb', 0) for p in partitions]
    
    fig.add_trace(
        go.Pie(labels=labels, values=values, hole=0.4,
               textinfo='label+percent', textposition='inside'),
        row=1, col=1
    )
    
    # 2. 磁盘容量分布
    total = summary.get('total_size_gb', 0)
    used = summary.get('total_used_gb', 0)
    free = summary.get('total_free_gb', 0)
    
    fig.add_trace(
        go.Bar(x=['已使用', '剩余'], y=[used, free],
               marker_color=['#667eea', '#a0a0b0'],
               text=[f'{used:.1f}GB', f'{free:.1f}GB'],
               textposition='outside'),
        row=1, col=2
    )
    
    # 3. 各分区使用详情
    fig.add_trace(
        go.Bar(x=labels, y=values, name='已使用',
               marker_color='#667eea', text=[f'{v:.1f}GB' for v in values],
               textposition='outside'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=labels, y=[p.get('free_gb', 0) for p in partitions],
               name='剩余', marker_color='#a0a0b0',
               text=[f'{v:.1f}GB' for v in [p.get('free_gb', 0) for p in partitions]],
               textposition='outside'),
        row=2, col=1
    )
    
    # 4. 总使用率指示器
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=summary.get('total_usage_percent', 0),
            title={'text': "总使用率"},
            domain={'row': 0, 'column': 0},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# 如果需要显示 Plotly 图表，取消注释以下代码
# if __name__ == "__main__":
#     main()
#     
#     # 在侧边栏显示 Plotly 图表
#     with st.sidebar:
#         st.markdown("### 📈 可视化图表")
#         result = get_disk_info()
#         if result.get("status") == "success":
#             fig = create_plotly_dashboard(result["data"])
#             st.plotly_chart(fig, width='stretch')

if __name__ == "__main__":
    main()