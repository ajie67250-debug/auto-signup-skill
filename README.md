# Auto Signup Skill

Codex / AI 智能体技能：驱动已登录的 Chrome 自主完成网站注册、填写资料，并读取邮箱验证码。

## 安装

克隆到技能目录，目录名即技能名：

```bash
git clone https://github.com/ajie67250-debug/auto-signup-skill.git ~/.codex/skills/auto-signup
```

## 配置

打开 `SKILL.md`，在「身份档案」表格里填入你自己的真实资料：邮箱、姓名、出生日期、密码基串、手机号。

如需用 IMAP 通道读取验证码，再设置两个环境变量：

```bash
export GMAIL_USER="you@example.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

## 使用

对智能体说：

```text
用 auto-signup 帮我在 <平台名> 注册账号
```

## 边界与合规

- 仅用于你有权注册的账号，并遵守目标网站的服务条款。
- 不绕过 CAPTCHA、人机验证或风控；遇到验证会停下来请你手动完成。
- 不做批量注册、养号或刷量。
- 身份证、银行卡、税务信息、人脸等敏感信息一律不编造，会停下来向你索要。
- 凭据只在对话里回报，不写入仓库文件。

## 目录

```text
SKILL.md                 主流程与字段填写规则
agents/openai.yaml       智能体接口描述
references/platforms.md  平台踩坑记录
scripts/fetch_code.py    Gmail 验证码读取脚本
```
