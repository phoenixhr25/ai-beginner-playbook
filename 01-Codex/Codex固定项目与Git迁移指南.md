# Codex 固定项目与 Git 迁移指南

> 验证日期：2026-09-30
> 验证环境：macOS，Codex 桌面端
> 状态：迁移过程已验证；Codex 界面入口可能随版本变化

## 适用场景

项目最初放在带日期的 Codex 工作目录或 `outputs` 中，希望迁移到长期目录，并在 Codex 中保存为固定项目。

## 推荐目录

```text
~/Documents/Projects/项目名
```

长期项目不建议放在日期目录或 `outputs` 中，因为这些位置容易被视为一次任务的临时产物。

## 一、在 Finder 中移动整个项目

1. 打开 Finder。
2. 按 `Command + Shift + G`。
3. 输入项目原路径并按回车。
4. 选中整个项目文件夹，按 `Command + C`。
5. 进入 `文稿/Projects`。
6. 按 `Option + Command + V`，把文件夹移动到这里。
7. 根据需要重命名项目文件夹。

必须移动整个文件夹，不能只复制其中的可见文件，否则隐藏的 `.git` 目录可能遗漏。

## 二、确认 Git 信息完整

`.git` 是仓库的隐藏管理目录，保存提交历史、分支、远程地址和文件状态。Finder 中可按 `Command + Shift + .` 显示隐藏文件。

在终端进入新目录后，可以运行：

```bash
git status
git remote -v
git log -1 --oneline
```

应确认：

- 当前分支存在；
- GitHub 远程地址正确；
- 最新提交存在；
- 没有意外的未提交修改。

不要手动编辑或删除 `.git`。

## 三、添加为 Codex 固定项目

1. 在 Codex 左侧找到“项目”。
2. 打开项目管理入口并选择本地文件夹；具体按钮名称可能随版本变化。
3. 在 Finder 选择框中按 `Command + Shift + G`。
4. 粘贴新的项目路径。
5. 选择包含 `.git`、README 和源代码的项目根目录。
6. 添加后点击“编辑项目”，把默认名称改成容易识别的产品名。
7. 以后从该项目右侧的方框铅笔图标新开对话。发送第一条要求后，这个对话就成为该项目中的任务。

如果找不到入口，参见[如何在 Codex 项目中新建任务](如何在项目中新建任务.md)。

## 四、几个容易混淆的概念

### 对话压缩

对话压缩只是把较长的聊天上下文整理成摘要，不会删除电脑文件、`.git`、GitHub 仓库或线上应用。

### 本地 Git

本地 Git 管理电脑上的代码版本，并通过已有凭据向 GitHub 推送。

### GitHub Connector

GitHub Connector 是 Codex 通过 GitHub API 读取或操作仓库的连接。它与本地 Git、浏览器中的 GitHub 登录彼此独立。Connector 没有写权限时，本地 Git 仍可能正常推送。

## 五、问题排查顺序

如果迁移后 Codex 或 Git 找不到项目，依次检查：

1. 新路径是否确实存在；
2. 是否移动了整个项目文件夹；
3. `.git` 是否仍在项目根目录；
4. `git status` 是否正常；
5. `git remote -v` 是否指向正确仓库；
6. Codex 固定项目是否选择了新的根目录；
7. 新任务是否从正确的 Codex 项目下创建。

## 本次“物光”示例

```text
长期目录：~/Documents/Projects/wuguang-inventory
Codex 项目名：物光
GitHub 仓库：phoenixhr25/wuguang-inventory
```

产品代码、个人数据备份和通用操作指南应分别保存：产品代码放产品 Git 仓库；个人物品 JSON 放 iCloud 等个人存储；通用指南放独立的“小白 AI 操作题”知识库（`~/Documents/Projects/ai-beginner-playbook`）。
