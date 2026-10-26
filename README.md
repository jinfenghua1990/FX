# FX · 格力高分销系统

Odoo Community 19.0 本地基础工程，面向内部经销商订货、运营审核和后续旺店通对接。

当前包含：

- Odoo 19.0 Community Docker 启动配置
- PostgreSQL 16 数据库服务
- 格力高分销商与分销订单基础模块
- 后续可扩展旺店通 `trade_push.php` 对接
- 面向其他 AI/开发机器人的项目上下文和协作规则

## 先读项目文档

- [AGENTS.md](AGENTS.md)：机器人协作规则
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md)：项目背景、已确定决策、旺店通流程和当前状态
- [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)：P0/P1/P2 实施计划

## 启动

需要 Docker Desktop：

```bash
cp .env.example .env
# 编辑 .env，设置两个强密码
docker compose up -d
```

打开 http://localhost:8069，新建数据库后安装 **Gele Distribution** 模块。

密码只放在本地 `.env`，不要提交到 GitHub。
