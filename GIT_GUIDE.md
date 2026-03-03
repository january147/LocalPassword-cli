# 密码管理器 Git 仓库

Git 仓库已成功初始化！

## 📋 提交历史

```
a5e59b9 Initial commit: Password Manager with GUI
```

## 🔧 Git 配置

```bash
cd /workspace/projects/workspace/password-manager

# 查看配置
git config --list

# 查看远程仓库（如果已添加）
git remote -v

# 查看分支
git branch -a

# 查看状态
git status
```

## 🚀 常用命令

### 查看状态

```bash
git status
```

### 查看日志

```bash
git log --oneline
git log --graph --all
```

### 创建新分支

```bash
git checkout -b feature/new-feature
```

### 提交更改

```bash
git add .
git commit -m "描述更改"
```

### 合并分支

```bash
git checkout main
git merge feature/new-feature
```

## 📦 分支策略

### main
- 主分支，稳定版本
- 只包含经过测试的代码

### feature/*
- 功能开发分支
- 从 main 分支创建
- 开发完成后合并回 main

### fix/*
- Bug 修复分支
- 从 main 分支创建
- 修复完成后合并回 main

## 🌐 远程仓库

### 添加远程仓库

```bash
git remote add origin <repository-url>
```

### 推送到远程仓库

```bash
git push -u origin main
```

### 从远程仓库拉取

```bash
git pull origin main
```

## 🏷️ 标签管理

### 创建标签

```bash
# 轻量级标签
git tag v1.0.0

# 带注释的标签
git tag -a v1.0.0 -m "版本 1.0.0"
```

### 推送标签

```bash
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 查看标签

```bash
git tag
```

## 📝 提交信息规范

### 格式

```
<type>(<scope>): <subject>

<body>
```

### 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(gui): add password search functionality

fix(database): handle concurrent access issues

docs(readme): update installation instructions
```

## 🔄 工作流

### 功能开发流程

1. 从 main 创建新分支
   ```bash
   git checkout -b feature/awesome-feature
   ```

2. 开发功能
   ```bash
   # 进行代码修改
   git add .
   git commit -m "feat: add awesome feature"
   ```

3. 测试和修复
   ```bash
   git checkout -b fix/bug-in-awesome-feature
   # 修复 bug
   git add .
   git commit -m "fix: resolve bug in awesome feature"
   git checkout feature/awesome-feature
   git merge fix/bug-in-awesome-feature
   ```

4. 合并到 main
   ```bash
   git checkout main
   git merge feature/awesome-feature
   ```

5. 推送到远程
   ```bash
   git push origin main
   ```

## 📊 仓库统计

```bash
# 查看代码行数统计
git log --numstat --pretty=format: -- . | awk '{add+=$1; subs+=$2} END {print "Added:", add, "Removed:", subs}'

# 查看提交统计
git shortlog --numbered --summary

# 查看最活跃的文件
git log --name-only --pretty=format: | sort | uniq -c | sort -rn
```

## 🔧 故障排除

### 撤销提交

```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD~1
```

### 恢复已删除的文件

```bash
# 从暂存区恢复
git checkout -- filename

# 从特定提交恢复
git checkout <commit> -- filename
```

### 忽略文件更改

```bash
# 忽略已跟踪文件的更改
git update-index --assume-unchanged filename

# 取消忽略
git update-index --no-assume-unchanged filename
```

---

**Git 仓库已配置完成！** 🎉
