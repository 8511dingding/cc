# VPS x-ui 管理工具

远程管理美国 VPS 上的 x-ui VPN 控制面板。

## 完整搭建教程

👉 [查看完整搭建教程](./SETUP_GUIDE.md)

包含从购买 VPS 到配置 Clash Verge 客户端的每一步详细说明。

## x-ui 是什么？

x-ui 是一个开源的 Xray/V2Ray 控制面板，支持：
- 多协议管理 (VMess, VLESS, Trojan, Shadowsocks 等)
- Web 图形界面
- 流量统计
- 证书管理
- 多用户管理

## 准备工作

### 1. 获取 VPS 信息

你需要美国 VPS 的：
- IP 地址
- SSH 端口（默认 22）
- SSH 密码或私钥

### 2. 配置连接

```bash
# 复制配置文件
cp config.example.sh config.sh

# 编辑配置文件，填入你的 VPS 信息
vim config.sh
```

配置示例：
```bash
VPS_HOST="123.456.789.012"
VPS_PORT="22"
VPS_USER="root"
VPS_PASSWORD="your-vps-password"
XUI_PORT="2053"
XUI_USERNAME="admin"
XUI_PASSWORD="your-panel-password"
```

### 3. 安装 sshpass（Mac）

```bash
brew install sshpass
```

## 使用方法

```bash
# 赋予执行权限
chmod +x xui-manager.sh

# 安装 x-ui
./xui-manager.sh install

# 查看控制面板信息
./xui-manager.sh panel

# 其他命令
./xui-manager.sh start      # 启动
./xui-manager.sh stop       # 停止
./xui-manager.sh restart     # 重启
./xui-manager.sh status      # 状态
./xui-manager.sh logs        # 日志
./xui-manager.sh backup      # 备份配置
./xui-manager.sh uninstall   # 卸载
```

## 防火墙设置

安装完成后，需要在 VPS 上开放端口：

```bash
# Ubuntu/Debian
ufw allow 2053/tcp
ufw allow 443/tcp   # 如果使用 TLS

# CentOS
firewall-cmd --permanent --add-port=2053/tcp
firewall-cmd --reload
```

## 访问控制面板

安装并启动后，访问：
```
http://你的VPS_IP:2053
```

使用配置的用户名密码登录。

## 常用 x-ui 命令（直接在 VPS 上执行）

```bash
x-ui start      # 启动
x-ui stop       # 停止
x-ui restart    # 重启
x-ui status     # 状态
x-ui logs       # 日志
x-ui update     # 更新
x-ui uninstall  # 卸载
```

## 目录结构

```
vps-xui-tool/
├── config.example.sh    # 配置模板
├── config.sh            # 你的配置（不提交到 git）
├── xui-manager.sh       # 管理脚本
├── backups/             # 配置文件备份
└── README.md
```

## 安全建议

1. 修改默认端口（2053）和强密码
2. 使用 SSH Key 认证而非密码
3. 定期备份配置
4. 开启防火墙，只开放必要端口
