# 我的超能力

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一款随机生成超能力的 ASTRBOT 插件（适用于 OneBot V11）。

## 简介

从四个素材文件夹（超能力/但是/主义/万圣节）中各随机选取一张图片，垂直拼接成一张超能力卡片并发送到群聊。

## 安装

- 使用仓库链接https://github.com/Venti-XingLanCiJiang-BiLiBiLi/astrbot_plugin_mypower以获取最新版本插件

- 或下载source code.zip并导入AstrBot以安装


## 配置

插件支持通过 ASTRBOT WebUI 管理面板进行配置，重启后生效。

| 配置项 | 类型 | 默认值 | 说明 |
|:---:|:---:|:---:|:---|
| `trigger_keyword` | list | `["我的超能力"]` | 触发指令的唤醒词列表，匹配任意一个即触发 |
| `material_folders` | list | `["超能力","但是","主义","万圣节"]` | 素材文件夹列表（有序，影响拼接顺序） |
| `admin_uids` | list | `[]` | 管理员 QQ 号列表，不受冷却时间限制 |

配置文件路径：`data/config/astrbot_plugin_mypower_config.json`

## 使用

### 指令

| 指令（可配置） | 说明 |
|:---:|:---:|
| 我的超能力 | 随机生成超能力卡片 |

### 冷却机制

- 每次触发后进入 **5 分钟冷却**，冷却期间回复剩余等待时间
- **管理员**（在 `admin_uids` 中配置或 ASTRBOT 全局管理员）不受冷却限制

### 效果

发送默认唤醒词 `我的超能力` 后，机器人将从各素材文件夹中各随机选择一张素材图，按配置顺序合成一张超能力卡片并发送。

## 素材说明

插件包含以下四类素材图片：

| 文件夹 | 说明 | 数量 |
|:---:|:---:|:---:|
| 超能力/ | 超能力主体 | 50 |
| 但是/ | 副作用/转折 | 35 |
| 主义/ | 理念/主义 | 18 |
| 万圣节/ | 万圣节主题 | 15 |

> 如需自定义素材可直接替换对应文件夹中的图片文件（支持 .png/.jpg/.jpeg/.gif 格式）。

## 兼容性

- **ASTRBOT** >= v4.16
- **Python** >= 3.8
- **适配器**: aiocqhttp (OneBot V11)

## 开源

本项目基于 [nonebot_plugin_mypower](https://github.com/tianyisama/nonebot_plugin_mypower) 移植，遵循 MIT 协议。

来源与致谢

- 参考仓库： https://github.com/tianyisama/nonebot_plugin_mypower
- 本项目在保留原作者贡献的同时，遵循 MIT 许可证要求，已在仓库中包含 LICENSE 文件以示声明。

## 更新日志

### v1.1.0

- **唤醒词**：`trigger_keyword` 改为列表类型，可配置多个唤醒词，匹配任意一个即可触发
- **冷却机制**：新增 5 分钟冷却时间（CD），冷却期间回复剩余等待时间
- **管理员豁免**：新增 `admin_uids` 配置项，管理员不受 CD 限制
- **素材清理**：已按照平台合规要求清理不适宜的素材图片

### v1.0.0

- 从 Hoshino 移植至 ASTRBOT 的初始版本
- 支持 `我的超能力` 指令随机生成超能力卡片
- 四类素材：超能力 / 但是 / 主义 / 万圣节
