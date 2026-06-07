# OrbStack 部署 FastMOSS 报告

这个配置会让 OrbStack 用 Nginx 托管项目里的报告目录：

```text
/Users/jianing/Ning's Git/tiktok-product-intel/orbstack-www/ning_mac
```

启动后访问：

```text
http://localhost:8090/FastMOSS-Report/
```

## 启动

在项目目录执行：

```bash
cd "/Users/jianing/Ning's Git/tiktok-product-intel"
docker compose -f docker-compose.fastmoss.yml up -d
```

## 停止

```bash
docker compose -f docker-compose.fastmoss.yml down
```

## 更新报告

只要 `orbstack-www/ning_mac/FastMOSS-Report/` 里的文件更新，页面会自动读取新文件，不需要重启容器。

## 如果 8090 冲突

把 `docker-compose.fastmoss.yml` 里的：

```yaml
- "8090:80"
```

改成：

```yaml
- "8091:80"
```

然后访问：

```text
http://localhost:8091/FastMOSS-Report/
```
