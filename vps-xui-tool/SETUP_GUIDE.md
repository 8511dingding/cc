# x-ui + Clash Verge 完整搭建教程

## 目录
1. [概述](#概述)
2. [购买 VPS 主机](#购买-vps-主机)
3. [初始化 VPS](#初始化-vps)
4. [安装 x-ui](#安装-x-ui)
5. [配置 VLESS + Reality](#配置-vless--reality)
6. [配置 LA-ISP SOCKS5 出站代理](#配置-la-isp-socks5-出站代理)
7. [配置路由规则](#配置路由规则)
8. [配置 Clash Verge 客户端](#配置-clash-verge-客户端)
9. [常见问题与解决](#常见问题与解决)
10. [维护命令参考](#维护命令参考)

---

## 概述

### 系统架构
```
用户浏览器 → Clash Verge (Mac) → VPS (95.169.8.33:443)
                                     ↓
                              x-ui (VLESS+Reality)
                                     ↓
                              LA-ISP SOCKS5 (205.196.8.5:43635)
                                     ↓
                              互联网 (OpenAI/Google/GitHub等)
```

### 组件说明
- **VPS**: 位于洛杉矶的 x-ui 面板服务器
- **x-ui**: 可视化 Xray/V2Ray 管理面板
- **VLESS + Reality**: 抗审查的翻墙协议
- **LA-ISP SOCKS5**: LA 机房的 ISP 提供的高速 SOCKS5 代理
- **Clash Verge**: Mac 上的代理客户端

---

## 购买 VPS 主机

### 推荐配置
- **地区**: 洛杉矶（LA）优先，延迟低
- **系统**: Debian 11/12 或 Ubuntu 20/22
- **配置**: 1核1GB 起步
- **推荐商家**: 搬瓦工、HostDare、CloudCone

### 购买后记录
```
IP: 95.169.8.33
SSH端口: 22
root密码: TWr029ORumhQ
```

---

## 初始化 VPS

### 1. SSH 连接
```bash
ssh root@95.169.8.33
# 输入密码: TWr029ORumhQ
```

### 2. 更新系统
```bash
apt update && apt upgrade -y
```

### 3. 安装必要工具
```bash
apt install -y curl wget vim git unzip socat
```

### 4. 设置时区
```bash
timedatectl set-timezone Asia/Shanghai
```

---

## 安装 x-ui

### 1. 一键安装
```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

### 2. 安装过程
- 选择语言: cn (中文)
- 设置用户名密码
- 配置面板端口

### 3. 安装完成后的信息
```
面板地址: https://95.169.8.33:12122
用户名: 8PMMUEDgp0
密码: l5dyiSgb4Y
```

### 4. 修改面板监听地址（允许外网访问）
```bash
# 登录数据库修改
sqlite3 /etc/x-ui/x-ui.db
UPDATE settings SET value='0.0.0.0' WHERE key='webListen';
.quit
```

### 5. 重启服务
```bash
systemctl restart x-ui
```

---

## 配置 VLESS + Reality

### 1. 登录 x-ui 面板
```
URL: https://95.169.8.33:12122/AEooQ0SPRHywWoDU4k/
用户名: 8PMMUEDgp0
密码: l5dyiSgb4Y
```

### 2. 添加入站连接
- 协议: VLESS
- 端口: 443
- UUID: e0e302bd-5b7d-45a5-ab9c-398cde42a735
- 流控: xtls-rprx-vision
- 传输: TCP
- 安全: Reality

### 3. Reality 设置
- SNI: www.apple.com
- Public Key: HnlrL6XiCpP73NKz9XDLbJ0GTIVdKrKzCxJycXScBwg
- Short ID: 4cd34f

### 4. 生成私钥和公钥（可选）
如果需要重新生成密钥对：
```bash
xray x25519
# 输出:
# Private key: eE-QAvOE-c1NdZtMhgLuvD5SLolTmp84e7dJ5qoKqHU
# Public key: HnlrL6XiCpP73NKz9XDLbJ0GTIVdKrKzCxJycXScBwg
```

---

## 配置 LA-ISP SOCKS5 出站代理

### LA-ISP 信息
```
Host: 205.196.8.5
Port: 43635
Username: Ej9kyDhWM8XIcvL
Password: cxGFUJBl1FbCcxm
```

### 在 x-ui 中配置出站代理
1. 进入「出站节点」设置
2. 添加 SOCKS5 代理
3. 填入上面的信息
4. Tag 设为: LA-ISP

### 订阅配置
- Sub Port: 2096
- Sub Path: /clash/
- Sub Listen: 0.0.0.0 (重要!)
- 订阅URL: https://95.169.8.33:2096/clash/irye3mvgr0h4q8ck

---

## 配置路由规则

### 路由规则（共6条）

#### 规则1: API管理流量
```json
{
  "type": "field",
  "inboundTag": ["api"],
  "outboundTag": "api"
}
```

#### 规则2: BT下载拦截
```json
{
  "type": "field",
  "protocol": ["bittorrent"],
  "outboundTag": "blocked"
}
```

#### 规则3: 国内IP直连
```json
{
  "type": "field",
  "ip": ["geoip:cn", "geoip:private"],
  "outboundTag": "direct"
}
```

#### 规则4: 国内域名直连（34条）
```json
{
  "type": "field",
  "domain": [
    "geosite:cn",
    "geosite:private",
    "domain:safebrowsing.googleapis.com",
    "domain:font.ssl.cr2.top",
    "domain:mtalk.google.com",
    "domain:baidu.com",
    "domain:ns1.net",
    "domain:ns2.net",
    "domain:dns.weicloud.me",
    "domain:apiclient.baicu.com",
    "domain:clientservices.googleapis.com",
    "domain:dl.google.com",
    "domain:gvt1.com",
    "domain:gvt1.cn.com",
    "domain:gvt2.com",
    "domain:gvt3.com",
    "domain:ms.cn.com",
    "domain:ms.unchs.126.net",
    "domain:12308.cn",
    "domain:moegirl.org.cn",
    "domain:bing.com",
    "domain:msftconnecttest.com",
    "domain:msftncsi.com",
    "domain-suffix:126.com",
    "domain-suffix:163.com",
    "domain-suffix:live.com",
    "domain-suffix:wikipedia.org",
    "domain-suffix:tldrnewsletter.com",
    "domain-suffix:simplenote.com",
    "domain-keyword:baidu",
    "domain-keyword:google",
    "domain-keyword:blogspot",
    "domain-keyword:126",
    "domain-keyword:163"
  ],
  "outboundTag": "direct"
}
```

#### 规则5: AI/Google/GitHub代理（12条）
```json
{
  "type": "field",
  "domain": [
    "geosite:openai",
    "geosite:anthropic",
    "geosite:google",
    "domain:claude.ai",
    "domain:chat.openai.com",
    "domain:chatgpt.com",
    "domain:openai.com",
    "domain:github.com",
    "domain:githubusercontent.com",
    "domain:google.com",
    "domain:googleapis.com",
    "domain:googlevideo.com"
  ],
  "outboundTag": "LA-ISP"
}
```

#### 规则6: 微软/腾讯IP直连（56条）
```json
{
  "type": "field",
  "ip": [
    "123.58.180.0/24",
    "180.163.248.0/24",
    "223.167.166.0/24",
    "13.104.176.0/14",
    "40.64.0.0/10",
    "52.224.0.0/12",
    "104.44.192.0/18",
    "111.221.64.0/22",
    "131.253.32.0/15",
    "142.251.0.0/16",
    "157.54.0.0/15",
    "157.56.0.0/14",
    "191.234.0.0/16",
    "204.79.195.0/24",
    "204.79.197.0/24",
    "207.46.192.0/19",
    "23.100.0.0/14",
    "23.104.0.0/15",
    "4.150.0.0/16",
    "4.208.0.0/15",
    "52.128.0.0/13",
    "52.136.0.0/13",
    "52.152.0.0/16",
    "52.160.0.0/11",
    "65.200.0.0/15",
    "65.204.0.0/14",
    "72.14.192.0/18",
    "74.114.0.0/15",
    "74.125.0.0/16",
    "74.208.0.0/15",
    "76.223.0.0/17"
  ],
  "outboundTag": "direct"
}
```

### 通过数据库更新路由规则

由于 x-ui 重启会覆盖 config.json，需要修改数据库：

```bash
ssh root@95.169.8.33

# 创建Python脚本更新路由
python3 << 'PYEOF'
import sqlite3, json

conn = sqlite3.connect('/etc/x-ui/x-ui.db')
cursor = conn.cursor()

cursor.execute("SELECT value FROM settings WHERE key='xrayTemplateConfig'")
result = cursor.fetchone()

if result:
    template = json.loads(result[0])
    # 在这里添加路由规则...
    template['routing']['rules'] = [你的规则列表]
    cursor.execute("UPDATE settings SET value=? WHERE key='xrayTemplateConfig'", (json.dumps(template),))
    conn.commit()
    print('路由规则已更新')

conn.close()
PYEOF

# 重启x-ui
systemctl restart x-ui
```

---

## 配置 Clash Verge 客户端

### 1. 安装 Clash Verge
从 https://github.com/clash-verge-rev/clash-verge-rev 下载安装

### 2. 订阅配置
- 订阅URL: https://95.169.8.33:2096/clash/irye3mvgr0h4q8ck
- 更新间隔: 720分钟

### 3. 本地路由规则
```yaml
port: 7897
socks-port: 7898
allow-lan: false
mode: rule
log-level: warning

proxies:
  - name: "LA-VLESS"
    type: vless
    server: 95.169.8.33
    port: 443
    uuid: e0e302bd-5b7d-45a5-ab9c-398cde42a735
    flow: xtls-rprx-vision
    network: tcp
    tls: true
    client-fingerprint: chrome
    udp: true
    sni: www.apple.com
    servername: www.apple.com
    reality-opts:
      public-key: HnlrL6XiCpP73NKz9XDLbJ0GTIVdKrKzCxJycXScBwg
      short-id: "4cd34f"

proxy-groups:
  - name: "LA-ISP"
    type: select
    proxies:
      - LA-VLESS
      - DIRECT

rules:
  - GEOSITE,openai,LA-ISP
  - GEOSITE,anthropic,LA-ISP
  - GEOSITE,google,LA-ISP
  - DOMAIN,claude.ai,LA-ISP
  - DOMAIN,chat.openai.com,LA-ISP
  - DOMAIN,chatgpt.com,LA-ISP
  - DOMAIN,openai.com,LA-ISP
  - DOMAIN,github.com,LA-ISP
  - DOMAIN,githubusercontent.com,LA-ISP
  - DOMAIN,google.com,LA-ISP
  - DOMAIN,googleapis.com,LA-ISP
  - DOMAIN,googlevideo.com,LA-ISP
  - GEOIP,CN,DIRECT
  - MATCH,DIRECT
```

### 4. 系统代理设置（重要！）
**不要使用 PAC 模式**，会导致连接不稳定。

手动设置系统代理：
```bash
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7897
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7897
```

关闭 PAC：
- Clash Verge → 设置 → 关闭 PAC 模式

### 5. Clash Verge 进程清理
如果出现多个 verge-mihomo 进程残留：
```bash
# 查看进程
ps aux | grep verge

# 杀掉所有旧进程
pkill -9 -f "Clash Verge"

# 重启
open -a "Clash Verge"
```

---

## 常见问题与解决

### 问题1: 连接只能维持几秒就断开

**原因**: PAC 配置错误，端口号丢失

**解决**: 
1. 关闭 PAC 模式
2. 使用手动系统代理设置

### 问题2: 端口7897被占用

**原因**: 多个 verge-mihomo 进程残留

**解决**:
```bash
lsof -i :7897
kill -9 <PID>
```

### 问题3: x-ui 重启后配置被重置

**原因**: x-ui 使用数据库模板覆盖 config.json

**解决**: 修改数据库中的 xrayTemplateConfig
```bash
sqlite3 /etc/x-ui/x-ui.db
# 然后用 Python 修改
```

### 问题4: xray-core 启动失败

**原因**: 路由规则有空规则（无匹配字段）

**解决**: 确保每条规则都有有效的 domain/ip/inboundTag

### 问题5: Clash Verge 无法连接服务器

**原因**: ML-KEM 加密不被支持

**解决**: 在 x-ui 面板中移除 ML-KEM 设置

### 问题6: Google 无法访问

**原因**: 路由规则没有包含 Google 相关域名

**解决**: 在路由规则中添加 geosite:google 和相关域名

---

## 维护命令参考

### VPS 端
```bash
# SSH连接
ssh root@95.169.8.33

# 重启x-ui
systemctl restart x-ui

# 查看x-ui状态
systemctl status x-ui

# 查看x-ui日志
journalctl -u x-ui --no-pager -n 50

# 查看端口监听
ss -tlnp | grep -E '443|2096|12122'

# 查看路由规则说明
cat /etc/x-ui/routing_rules_remarks.txt

# 重启后重新应用路由规则
python3 /tmp/update_routing.py
```

### 本地 Mac 端
```bash
# 查看代理端口占用
lsof -i :7897

# 设置系统代理
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7897
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7897

# 关闭系统代理
sudo networksetup -setwebproxystate "Wi-Fi" off
sudo networksetup -setsecurewebproxystate "Wi-Fi" off

# 查看代理状态
networksetup -getwebproxy "Wi-Fi"
networksetup -getsecurewebproxy "Wi-Fi"

# 测试代理
curl -s --proxy http://127.0.0.1:7897 http://httpbin.org/ip
```

---

## 服务器信息汇总

| 项目 | 值 |
|------|-----|
| VPS IP | 95.169.8.33 |
| SSH端口 | 22 |
| root密码 | TWr029ORumhQ |
| x-ui面板端口 | 12122 |
| x-ui用户名 | 8PMMUEDgp0 |
| x-ui密码 | l5dyiSgb4Y |
| WebBasePath | AEooQ0SPRHywWoDU4k |
| 订阅端口 | 2096 |
| VLESS端口 | 443 |
| VLESS UUID | e0e302bd-5b7d-45a5-ab9c-398cde42a735 |
| Reality公钥 | HnlrL6XiCpP73NKz9XDLbJ0GTIVdKrKzCxJycXScBwg |
| LA-ISP代理 | 205.196.8.5:43635 |
| LA-ISP用户名 | Ej9kyDhWM8XIcvL |
| LA-ISP密码 | cxGFUJBl1FbCcxm |

---

*文档创建时间: 2026-06-26*
*最后更新: 2026-06-26*
