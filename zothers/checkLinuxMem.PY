import paramiko

# 检查是否已授权使用root用户登录（如你提供的密码）
#hostname = "104.168.125.34"
hostname = "192.168.1.119"

port = 22
username = "root"
password = "86868686mM"

# 初始化 SSH 客户端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        timeout=10
    )

    # 脚本内容：查询内存、进程、日志等（不执行修改）
    script = """
    # 查看系统内存使用情况
    echo "=== 系统内存使用情况 ==="
    free -h
    echo ""
    echo ""
    # 查看内存占用高的进程
    echo "=== 内存占用高的进程 ==="
    ps aux --sort=-%mem | head -n 15
    echo ""
    echo ""
    # 查看内存相关系统日志
    echo "=== 系统日志（内存相关） ==="
    sudo grep -i 'oom\\|memory' /var/log/syslog
    echo ""
    echo ""
    # 检查是否有僵尸进程
    echo "=== 僵尸进程检查 ==="
    sudo ps aux | grep 'defunct'
    echo ""
    echo ""
    # 查看运行中的服务及内存使用情况
    echo "=== 系统运行中的服务内存使用 ==="
    systemctl list-units --type=service --load-state=running | awk '{print $1\n, $2\n, $3\n, $4\n}\n' | while read line; do
        service_name=$(echo $line | awk '{print $1}\n')
        if [ -n "$service_name" ]; then
            echo "Service: $service_name"
            sudo grep "Memory" /var/log/$service_name.log || true
        fi
    done
    """

    # 执行脚本
    stdin, stdout, stderr = ssh.exec_command(script)
    print("===== 远程诊断结果 =====")
    print(stdout.read().decode())
    print("===== 错误信息 =====")
    print(stderr.read().decode())

finally:
    ssh.close()
    print("SSH 连接已断开")