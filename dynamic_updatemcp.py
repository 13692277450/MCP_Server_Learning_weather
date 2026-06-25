import os
import glob

def discover_servers(servers_dir="servers"):
    """自动发现指定目录下的所有 server.py 文件"""
    pattern = os.path.join(servers_dir, "*_server.py")
    server_files = glob.glob(pattern)
    
    servers = {}
    for file in server_files:
        name = os.path.basename(file).replace("_server.py", "")
        servers[name] = {
            "script": file,
            "enabled": True,
            "description": f"Auto-discovered server: {name}"
        }
    return servers