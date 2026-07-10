# main.py
import json
import subprocess
import sys
import os
import locale

def get_disk_info():
    """
    获取磁盘信息，修复 Windows 编码问题
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_diskInfoServer.py")
    
    if not os.path.exists(script_path):
        return {
            "status": "error",
            "message": f"找不到 mcp_diskInfoServer.py: {script_path}"
        }
    
    try:
        # 使用 --call 参数直接调用
        result = subprocess.run(
            [sys.executable, script_path, "--call", "get_disk_info"],
            capture_output=True,
            text=False,  # 使用 bytes 模式，避免编码问题
            timeout=30
        )
        
        if result.returncode != 0:
            # 尝试解码错误信息
            try:
                error_msg = result.stderr.decode('gbk' if sys.platform == 'win32' else 'utf-8')
            except:
                error_msg = str(result.stderr)
            return {
                "status": "error",
                "message": f"执行失败: {error_msg}"
            }
        
        # 尝试多种编码解码 stdout
        stdout_text = None
        encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1']
        
        for encoding in encodings:
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
        
        # 解析 JSON
        try:
            return json.loads(stdout_text)
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"解析 JSON 失败: {str(e)}",
                "raw": stdout_text[:200]
            }
        
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

def print_disk_info(result):
    """格式化打印磁盘信息"""
    if result.get("status") != "success":
        print(f"❌ 错误: {result.get('message', '未知错误')}")
        if "raw" in result:
            print(f"原始输出: {result['raw']}")
        return
    
    data = result.get("data", {})
    
    print("\n" + "=" * 70)
    print("💻 系统硬盘信息报告")
    print("=" * 70)
    
    # 系统信息
    sys_info = data.get("system_info", {})
    print(f"\n🖥️  系统: {sys_info.get('os', '未知')}")
    print(f"   主机: {sys_info.get('hostname', '未知')}")
    print(f"   时间: {sys_info.get('timestamp', '未知')}")
    
    # 分区信息
    partitions = data.get("partitions", [])
    if partitions:
        print(f"\n📁 分区 ({len(partitions)} 个):")
        for part in partitions:
            total = part.get('size_gb', 0)
            used = part.get('used_gb', 0)
            free = part.get('free_gb', 0)
            percent = part.get('usage_percent', 0)
            drive = part.get('drive_letter', part.get('device', '未知'))
            
            bar_len = 20
            filled = int(bar_len * percent / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            
            print(f"\n   💿 {drive}:")
            print(f"      总大小: {total:.2f} GB")
            print(f"      已使用: {used:.2f} GB")
            print(f"      剩余: {free:.2f} GB")
            print(f"      使用率: {percent:.1f}% [{bar}]")
    
    # 汇总信息
    summary = data.get("total_summary", {})
    if summary:
        print(f"\n📊 汇总:")
        print(f"   总容量: {summary.get('total_size_gb', 0):.2f} GB")
        print(f"   已使用: {summary.get('total_used_gb', 0):.2f} GB")
        print(f"   剩余: {summary.get('total_free_gb', 0):.2f} GB")
        print(f"   使用率: {summary.get('total_usage_percent', 0):.1f}%")
        print(f"   分区数: {summary.get('partition_count', 0)} 个")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    # 设置控制台编码
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("📊 正在获取磁盘信息...")
    print("=" * 60)
    
    result = get_disk_info()
    print_disk_info(result)
    
    # 可选：显示完整 JSON
    show_json = input("\n显示完整 JSON? (y/n): ").strip().lower()
    if show_json == 'y':
        print("\n📄 完整 JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))