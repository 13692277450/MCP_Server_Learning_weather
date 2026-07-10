# server.py
import json
import sys
import platform
from datetime import datetime
from typing import Dict, Any
import psutil


# 忽略 wmi 警告
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Windows 特定导入
if platform.system() == "Windows":
    import wmi
    import pythoncom

from mcp.server.fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("DiskInfo Server")

# ============ 核心功能函数 ============
def get_disk_info_windows() -> Dict[str, Any]:
    """获取 Windows 系统的详细硬盘信息"""
    pythoncom.CoInitialize() # type: ignore
    c = wmi.WMI() # type: ignore
    
    disk_info: Dict[str, Any] = {
        "physical_disks": [],
        "partitions": [],
        "total_summary": {}
    }
    
    # 获取物理硬盘信息
    physical_disks = c.Win32_DiskDrive()
    total_size = 0
    
    for disk in physical_disks:
        disk_data: Dict[str, Any] = {
            "index": disk.Index if disk.Index else 0,
            "model": disk.Model if disk.Model else "未知",
            "serial_number": disk.SerialNumber if disk.SerialNumber else "未知",
            "interface_type": disk.InterfaceType if disk.InterfaceType else "未知",
            "media_type": disk.MediaType if disk.MediaType else "未知",
            "size_gb": round(int(disk.Size) / (1024**3), 2) if disk.Size else 0,
            "size_bytes": int(disk.Size) if disk.Size else 0,
            "manufacturer": disk.Manufacturer if disk.Manufacturer else "未知",
            "status": disk.Status if disk.Status else "未知",
            "partitions": disk.Partitions if disk.Partitions else 0,
            "firmware_revision": disk.FirmwareRevision if disk.FirmwareRevision else "未知",
        }
        disk_info["physical_disks"].append(disk_data)
        
        if disk.Size:
            total_size += int(disk.Size)
    
    # 获取分区信息
    partitions = c.Win32_LogicalDisk()
    total_used = 0
    total_free = 0
    
    for partition in partitions:
        if partition.DriveType == 3:
            size_bytes = int(partition.Size) if partition.Size else 0
            free_bytes = int(partition.FreeSpace) if partition.FreeSpace else 0
            used_bytes = size_bytes - free_bytes if size_bytes > 0 else 0
            
            partition_data: Dict[str, Any] = {
                "drive_letter": partition.DeviceID if partition.DeviceID else "未知",
                "volume_name": partition.VolumeName if partition.VolumeName else "未命名",
                "file_system": partition.FileSystem if partition.FileSystem else "未知",
                "size_gb": round(size_bytes / (1024**3), 2) if size_bytes > 0 else 0,
                "size_bytes": size_bytes,
                "used_gb": round(used_bytes / (1024**3), 2) if used_bytes > 0 else 0,
                "used_bytes": used_bytes,
                "free_gb": round(free_bytes / (1024**3), 2) if free_bytes > 0 else 0,
                "free_bytes": free_bytes,
                "usage_percent": round((used_bytes / size_bytes * 100), 2) if size_bytes > 0 else 0,
                "drive_type": "本地磁盘",
            }
            disk_info["partitions"].append(partition_data)
            
            total_used += used_bytes
            total_free += free_bytes
    
    # 汇总信息
    disk_info["total_summary"] = {
        "total_size_gb": round(total_size / (1024**3), 2),
        "total_size_bytes": total_size,
        "total_used_gb": round(total_used / (1024**3), 2),
        "total_used_bytes": total_used,
        "total_free_gb": round(total_free / (1024**3), 2),
        "total_free_bytes": total_free,
        "total_usage_percent": round((total_used / total_size * 100), 2) if total_size > 0 else 0,
        "physical_disk_count": len(disk_info["physical_disks"]),
        "partition_count": len(disk_info["partitions"]),
    }
    
    # IO 统计
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io:
            disk_info["io_stats"] = {
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
                "read_bytes_gb": round(disk_io.read_bytes / (1024**3), 2),
                "write_bytes_gb": round(disk_io.write_bytes / (1024**3), 2),
            }
    except:
        pass
    
    return disk_info

def get_disk_info_fallback() -> Dict[str, Any]:
    """使用 psutil 作为回退方案"""
    disk_info: Dict[str, Any] = {
        "partitions": [],
        "total_summary": {}
    }
    
    partitions = psutil.disk_partitions()
    total_size = 0
    total_used = 0
    total_free = 0
    
    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            size_bytes = usage.total
            used_bytes = usage.used
            free_bytes = usage.free
            
            partition_data: Dict[str, Any] = {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "file_system": part.fstype,
                "size_gb": round(size_bytes / (1024**3), 2),
                "size_bytes": size_bytes,
                "used_gb": round(used_bytes / (1024**3), 2),
                "used_bytes": used_bytes,
                "free_gb": round(free_bytes / (1024**3), 2),
                "free_bytes": free_bytes,
                "usage_percent": round((used_bytes / size_bytes * 100), 2) if size_bytes > 0 else 0,
            }
            disk_info["partitions"].append(partition_data)
            
            total_size += size_bytes
            total_used += used_bytes
            total_free += free_bytes
        except:
            pass
    
    disk_info["total_summary"] = {
        "total_size_gb": round(total_size / (1024**3), 2),
        "total_size_bytes": total_size,
        "total_used_gb": round(total_used / (1024**3), 2),
        "total_used_bytes": total_used,
        "total_free_gb": round(total_free / (1024**3), 2),
        "total_free_bytes": total_free,
        "total_usage_percent": round((total_used / total_size * 100), 2) if total_size > 0 else 0,
        "partition_count": len(disk_info["partitions"]),
    }
    
    return disk_info

# ============ MCP 工具函数 ============
@mcp.tool()
def get_disk_info() -> str:
    """获取电脑硬盘分区和硬件的详细信息"""
    system = platform.system()
    
    if system == "Windows":
        try:
            disk_info = get_disk_info_windows()
        except:
            disk_info = get_disk_info_fallback()
    else:
        disk_info = get_disk_info_fallback()
    
    disk_info["system_info"] = {
        "os": system,
        "os_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat()
    }
    
    output = {
        "status": "success",
        "data": disk_info
    }
    
    return json.dumps(output, indent=2, ensure_ascii=False)

# ============ JSON-RPC 支持 ============
def handle_rpc_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理 JSON-RPC 请求"""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # 处理工具调用
    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "get_disk_info":
            try:
                result = get_disk_info()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {tool_name}"
                }
            }
    
    # 处理初始化
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "DiskInfo Server",
                    "version": "1.0.0"
                }
            }
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

# ============ 主入口 ============
if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--call":
        # 直接调用模式
        func_name = sys.argv[2] if len(sys.argv) > 2 else "get_disk_info"
        if func_name == "get_disk_info":
            print(get_disk_info())
        else:
            print(json.dumps({"error": f"Unknown function: {func_name}"}))
        sys.exit(0)
    
    # 标准输入模式 (用于 MCP 客户端)
    try:
        # 读取 stdin
        input_data = sys.stdin.read()
        if input_data.strip():
            request = json.loads(input_data)
            response = handle_rpc_request(request)
            print(json.dumps(response, ensure_ascii=False))
        else:
            # 没有输入时运行 MCP 服务器
            mcp.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }
        print(json.dumps(error_response))