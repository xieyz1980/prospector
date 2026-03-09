# Prospector

OpenClaw Skill - 潜在客户挖掘器，自动搜索潜在客户并提取联系方式

## 功能特性

- 🔍 **多搜索引擎支持**：DuckDuckGo、Bing、百度
- 📧 **智能邮箱提取**：官网爬取 + WHOIS查询
- ✅ **邮箱验证**：格式验证 + DNS检查
- 💾 **本地缓存**：自动缓存，避免重复搜索
- 🔄 **智能排重**：跳过已存在的公司
-  **数据统计**：查看累计数据
- 📤 **多格式导出**：JSON / CSV

## 快速开始

### 安装依赖

```bash
cd scripts
pip install -r requirements.txt
```

### 基本使用

```bash
# 搜索客户
python scripts/find_customers.py "软件开发" --region "上海" --limit 20

# 查看统计
python scripts/query_customers.py stats

# 导出数据
python scripts/query_customers.py export --csv customers.csv
```

### 安装到OpenClaw

```bash
# 复制到OpenClaw的skills目录
cp -r . ~/.openclaw/workspace/skills/prospector

# 重启Gateway
openclaw gateway restart
```

## 命令详解

### find_customers.py - 找客户

```bash
# 基本搜索
python scripts/find_customers.py "关键词"

# 指定地区
python scripts/find_customers.py "软件开发" --region "上海"

# 限制数量
python scripts/find_customers.py "软件开发" --limit 50

# 翻页搜索（获取更多不同结果）
python scripts/find_customers.py "软件开发" --page 10

# 导出结果
python scripts/find_customers.py "软件开发" --output results.json --csv results.csv

# 不使用缓存
python scripts/find_customers.py "软件开发" --no-cache

# 不跳过已存在的公司
python scripts/find_customers.py "软件开发" --no-skip

# 查看缓存统计
python scripts/find_customers.py --stats
```

### query_customers.py - 查询客户

```bash
# 列出客户
python scripts/query_customers.py list --limit 20

# 只显示有邮箱的客户
python scripts/query_customers.py list --has-email

# 只显示无邮箱的客户
python scripts/query_customers.py list --no-email

# JSON格式输出
python scripts/query_customers.py list --json

# 按关键词搜索
python scripts/query_customers.py search "阿里"

# 按邮箱搜索
python scripts/query_customers.py email "sales"

# 查看统计
python scripts/query_customers.py stats

# 导出数据
python scripts/query_customers.py export --output export.json --csv export.csv
```

### search_companies.py - 搜索公司

```bash
# 基本搜索
python scripts/search_companies.py "software company"

# 指定地区和数量
python scripts/search_companies.py "软件开发" --region "上海" --limit 50

# 导出结果
python scripts/search_companies.py "软件开发" --output search_results.json
```

### extract_emails.py - 提取邮箱

```bash
# 提取单个域名
python scripts/extract_emails.py example.com

# 不使用WHOIS
python scripts/extract_emails.py example.com --no-whois

# 导出结果
python scripts/extract_emails.py example.com --output emails.json
```

### validate_email.py - 验证邮箱

```bash
# 验证单个邮箱
python scripts/validate_email.py test@example.com

# 批量验证
python scripts/validate_email.py --batch emails.json

# 跳过DNS验证
python scripts/validate_email.py test@example.com --no-dns
```

## 输出格式

### JSON格式

```json
{
  "query": "软件开发",
  "region": "上海",
  "total_companies": 50,
  "total_emails": 35,
  "email_coverage": "70.0%",
  "results": [
    {
      "name": "XX科技有限公司",
      "domain": "xx.com",
      "url": "https://xx.com",
      "emails": ["contact@xx.com", "sales@xx.com"],
      "description": "专业软件开发服务"
    }
  ]
}
```

### CSV格式

```csv
公司名称,域名,邮箱,网址,简介
XX科技有限公司,xx.com,contact@xx.com,https://xx.com,专业软件开发服务
YY信息技术有限公司,yy.com,sales@yy.com,https://yy.com,IT解决方案
```

## 缓存机制

### 缓存内容

| 缓存类型 | 文件 | 有效期 | 说明 |
|----------|------|--------|------|
| 搜索缓存 | `cache/searches.json` | 7天 | 按关键词+地区缓存搜索结果 |
| 公司缓存 | `cache/companies.json` | 永久 | 已收集的公司信息 |
| 邮箱缓存 | `cache/emails.json` | 永久 | 已提取的邮箱地址 |

### 缓存管理

```bash
# 查看缓存统计
python scripts/query_customers.py stats

# 清理过期缓存
python scripts/cache_manager.py clear

# 导出所有缓存数据
python scripts/cache_manager.py export
```

## 在OpenClaw中使用

### 找客户

```
用户：帮我找上海地区的软件外包公司
用户：搜索北京的人工智能企业，需要50家
用户：继续找更多软件公司
```

### 查询客户

```
用户：查看已收集的客户列表
用户：搜索包含"阿里"的客户
用户：查找包含"sales"的邮箱
用户：查看数据统计
用户：导出所有客户数据
```

### 配合其他Skill

```
用户：帮我找上海的外贸公司，然后给每家公司发一封开发信

Agent会：
1. 调用 prospector Skill 找客户
2. 调用 send-email Skill 发邮件
```

## 职责边界

### ✅ 负责

- 搜索潜在客户
- 提取联系方式
- 验证邮箱格式
- 简单查询客户数据
- 导出客户数据
- 数据统计

### ❌ 不负责

- 发送邮件（由其他Skill处理）
- 复杂客户管理（标签、分类、跟进状态）
- 客户备注记录
- 发送历史追踪
- 回复状态管理

## 技术实现

### 搜索引擎

| 引擎 | 优先级 | 说明 |
|------|--------|------|
| DuckDuckGo | 高 | 无反爬限制，结果准确 |
| Bing | 中 | 需要处理重定向链接 |
| 百度 | 低 | 国内搜索，有时效性 |

### 邮箱提取

| 来源 | 说明 |
|------|------|
| 官网首页 | 提取页面中的邮箱 |
| 联系页面 | 访问/contact等页面 |
| WHOIS | 查询域名注册信息 |

### 邮箱验证

- 格式验证：正则匹配
- 域名验证：MX记录检查
- 一次性邮箱：黑名单过滤

## 注意事项

1. **搜索速度**：受网络影响，建议控制并发
2. **网站访问**：部分网站可能无法访问，会自动跳过
3. **邮箱准确率**：约60-70%，建议人工复核
4. **缓存数据**：会累积形成客户资产
5. **翻页搜索**：使用 `--page` 参数获取更多不同结果
6. **合规使用**：数据来源于公开信息，请遵守当地法规

## 项目结构

```
prospector/
├── SKILL.md                      # OpenClaw Skill配置
├── README.md                     # 本文档
├── scripts/
│   ├── find_customers.py         # 找客户（主入口）
│   ├── query_customers.py        # 查询客户
│   ├── search_companies.py       # 搜索公司
│   ├── extract_emails.py         # 提取邮箱
│   ├── validate_email.py         # 验证邮箱
│   ├── cache_manager.py          # 缓存管理
│   └── requirements.txt          # Python依赖
└── cache/                        # 缓存数据（自动生成）
    ├── companies.json            # 公司数据库
    ├── searches.json             # 搜索缓存
    └── emails.json               # 邮箱缓存
```

## 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| requests | >=2.28.0 | HTTP请求 |
| beautifulsoup4 | >=4.11.0 | HTML解析 |
| python-whois | >=0.8.0 | WHOIS查询 |
| dnspython | >=2.3.0 | DNS验证 |

## 更新日志

### v1.0.0 (2026-03-09)

- 初始版本
- 支持多搜索引擎搜索
- 支持邮箱提取和验证
- 支持本地缓存和排重
- 支持查询和导出功能

## License

MIT
