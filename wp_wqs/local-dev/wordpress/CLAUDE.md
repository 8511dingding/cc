# WordPress WQS 项目

## 当前环境

- 网站：`http://localhost:8081/wp_wqs/`
- 当前 WordPress：本目录
- 数据库：OrbStack MySQL `127.0.0.1:3306`
- 数据库名：`wqs_wordpress`
- 当前主题：`wp-content/themes/wqs-portfolio/`
- 站点级后台增强：`wp-content/mu-plugins/`

ServBay 和旧的 `local_portal/wp_wqs/` 均不是当前运行或部署目录。

## 开发规范

1. 主题展示功能优先修改 `wqs-portfolio`。
2. 站点专用的后台功能优先放入 MU 插件，避免修改第三方插件核心。
3. 修改 PHP 后进行语法检查。
4. 使用 `http://localhost:8081/wp_wqs/` 做页面和接口验证。
5. 谨慎处理 WordPress 序列化配置和 Polylang 翻译关系。

## 启动

从仓库根目录运行：

```bash
./local-dev/start-wp8081.sh
```
