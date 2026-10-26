# FX / 格力高分销系统项目上下文

更新时间：2026-10-26（Asia/Shanghai）

## 1. 项目目标

为格力高搭建内部使用的经销商订货系统：

经销商下单 → 运营审核 → 采购/到货状态关联 → 推送旺店通原始销售订单 → 旺店通继续完成审核、销售出库和仓库发货。

系统重点是：

- 经销商账号和订货入口
- 商品、SKU、价格和可订数量
- 运营订单审核
- 订单状态跟踪
- 旺店通接口对接
- 订单、SKU、旺店通单号之间的可追溯关系

“分配到货”不是当前核心难点，不要因为这一点重复建设完整 ERP/WMS。

## 2. 已确定的技术决策

| 项目 | 决策 |
|---|---|
| 基础平台 | Odoo Community 19.0 |
| GitHub 仓库 | https://github.com/jinfenghua1990/FX |
| 当前分支 | main |
| 本地运行 | Docker Desktop |
| Web | Odoo 19.0，端口 8069 |
| 数据库 | PostgreSQL 16 |
| 自定义代码 | `custom-addons/` |
| 当前业务模块 | `gele_distribution` |
| 配置安全 | 密码只放本地 `.env`，不提交 GitHub |
| 使用范围 | 公司内部使用，不对外销售软件 |
| 当前外部 ERP | 旺店通企业版 |

开源协议不是当前阻塞点。即使内部使用，也应保留上游许可证和版权声明；不要删除 Odoo 或第三方依赖的许可信息。

## 3. 系统职责划分

### Odoo / FX 负责

- 经销商档案
- 经销商登录和权限
- 商品与 SKU 目录
- 经销商价格
- 经销商订单
- 运营审核
- 订单备注、审核记录和异常记录
- 旺店通推送队列
- 旺店通原始单号和同步状态
- 面向运营的查询和督办界面

### 旺店通负责

- 采购订单
- 采购入库
- ERP 库存
- 销售订单后续处理
- 销售出库
- 仓库拣货和发货

不要默认 Odoo 和旺店通同时维护同一份库存。库存主数据和出库结果应以双方确认的边界为准。

## 4. 旺店通订单流程

1. 经销商在 FX 提交订单。
2. 运营在 FX 审核订单。
3. FX 生成唯一原始单号 `tid` 和子订单号 `oid`。
4. FX 调用企业版 `trade_push.php` 创建或更新原始订单。
5. 记录旺店通响应：`code`、`message`、`new_count`、`chg_count`。
6. 原始订单递交/审核后，由旺店通生成销售出库单。
7. FX 后续读取旺店通状态，展示给运营和经销商。

当前确认的关键点：

- 不能直接通过这个接口创建销售出库单。
- 原始订单推送成功后，订单货品数量不能随意修改；数量变化应产生补单、变更单或新的推送记录。
- 同一个店铺编号下，`tid` 必须唯一；`oid` 也必须唯一。
- `shop_no` 对应旺店通中“自有/其它”平台店铺。
- `buyer_nick` 不能只使用一个固定值，否则不同客户订单可能被旺店通拒绝。
- API 服务端允许的最大请求时间误差为 5 分钟，项目统一使用 `Asia/Shanghai` 生成签名时间。

### 主要请求字段

订单级：

- `tid`：FX 原始订单号
- `trade_status`：平台订单状态
- `pay_status`：付款状态
- `delivery_term`：发货条件
- `trade_time`、`pay_time`
- `buyer_nick`、`buyer_email`
- `receiver_name`、`receiver_mobile`、收货地址
- `post_amount`、`paid`
- `buyer_message`、`seller_memo`
- `order_list`：货品明细

货品级：

- `oid`：FX 子订单号
- `num`：数量
- `price`：标价
- `goods_id`、`spec_id`
- `goods_no`、`spec_no`
- `goods_name`、`spec_name`
- `adjust_amount`、`discount`、`share_discount`
- `status`、`refund_status`

### 关于自动审核

曾查到旗舰版开放平台的 `composite.Composite.checkOrderByApi` 方向，但当前使用的是企业版开放平台。没有旺店通官方确认前，不能把它当作企业版可用功能，也不能在 UI 中宣称“自动审核已完成”。

## 5. 当前代码状态

仓库已经包含：

- `docker-compose.yml)：PostgreSQL 16 + Odoo 19.0
- `config/odoo.conf)：Odoo 基础配置
- `.env.example)：本地密码模板
- `custom-addons/gele_distribution/`：第一版分销模块

当前模块模型：

- `gele.distributor`
  - 经销商名称、编码、联系人、邮箱、电话、启用状态
- `gele.distributor.order`
  - 订单号、经销商、下单时间、状态、金额、旺店通原始单号、备注
- `gele.distributor.order.line`
  - 产品、数量、单价、小计

当前订单状态：

- Draft
- Submitted
- Approved
- Pushed to WDT
- Cancelled

当前还没有完成：

- 经销商门户登录
- 正式商品/SKU同步
- 价格体系
- 旺店通签名客户端
- `trade_push.php` 生产接口
- 旺店通状态回写
- 订单审核权限细分
- 采购/入库状态展示
- 正式部署

## 6. 重要限制

- 当前 GitHub 仓库只保存 Odoo 配置和自定义 addon，不把完整 Odoo 上游源码复制进 FX。
- Docker 实际启动需要用户自己的 Mac 安装并运行 Docker Desktop。
- 当前代码已做静态检查和仓库文件核验，但不能把用户 Mac 上的 Docker 启动说成已验证。
- 任何机器人都不能擅自把旺店通、支付、短信、邮件等生产凭证写入仓库。
