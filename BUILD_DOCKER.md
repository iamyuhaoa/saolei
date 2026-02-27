# GitHub Actions 打包指南

## 方法1: 使用GitHub Actions自动打包（推荐）

### 步骤

1. **将代码推送到GitHub**

   ```bash
   cd /Users/iamyuhaha/mine/saolei

   # 初始化git仓库（如果还没有）
   git init
   git add .
   git commit -m "Initial commit"

   # 创建GitHub仓库后
   git remote add origin https://github.com/YOUR_USERNAME/saolei.git
   git branch -M main
   git push -u origin main
   ```

2. **触发自动构建**

   推送代码后会自动触发构建，或手动触发：
   - 访问 GitHub仓库
   - 点击 "Actions" 标签
   - 选择 "Build Windows EXE"
   - 点击 "Run workflow"

3. **下载打包好的EXE**

   构建完成后（约5-10分钟）：
   - 进入 "Actions" → 选择最新的构建
   - 在 "Artifacts" 部分下载 `MinesweeperAI-Windows`
   - 解压后得到 `MinesweeperAI.exe`

### 优势

- ✅ 完全免费
- ✅ 无需Windows电脑
- ✅ 每次push自动构建
- ✅ 可下载历史版本

---

## 方法2: 使用Docker Windows容器

### 前提条件

需要一台Windows宿主机或Windows Server。

### Dockerfile示例

```dockerfile
# Windows Server Core 基础镜像
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# 安装Python
RUNpowershell -Command \
    $ProgressPreference = 'SilentlyContinue'; \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe -OutFile python.exe; \
    Start-Process python.exe -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait; \
    Remove-Item python.exe

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 安装依赖
RUN pip install -r requirements.txt
RUN pip install pyinstaller

# 构建EXE
RUN pyinstaller build.spec

# 输出目录
VOLUME ["/app/dist"]
```

### 使用方法

```bash
# 在Windows上构建
docker build -t minesweeperai-build .
docker run --rm -v %cd%\dist:/app/dist minesweeperai-build
```

---

## 方法3: 使用虚拟机

### 在Mac上使用Parallels Desktop或VMware

1. 安装Windows 11虚拟机
2. 在虚拟机中安装Python
3. 运行 `build.bat`

### 下载Windows 11虚拟机镜像

- **Microsoft Dev VM**: https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/
- 支持Parallels、VMware、VirtualBox

---

## 方法4: 使用Wine（不推荐）

⚠️ **注意**: Wine无法打包真正的Windows exe，只能测试Linux版本。

```bash
# 在Mac上安装Wine
brew install --cask wine-stable

# Wine主要用于运行Windows程序，不适合打包
# PyInstaller在Wine下生成的不是真正的Windows exe
```

---

## 推荐方案对比

| 方案 | 难度 | 成本 | Windows电脑需求 | 推荐度 |
|------|------|------|----------------|--------|
| GitHub Actions | ⭐ | 免费 | ❌ 不需要 | ⭐⭐⭐⭐⭐ |
| Parallels/VMware | ⭐⭐⭐ | 付费 | ❌ 不需要 | ⭐⭐⭐ |
| Windows Docker | ⭐⭐⭐⭐ | 需要 | ✅ 需要 | ⭐⭐ |
| 借用Windows电脑 | ⭐ | 免费 | ✅ 需要 | ⭐⭐⭐⭐ |

---

## 快速开始（GitHub Actions）

1. 在GitHub创建新仓库
2. 上传代码：
   ```bash
   cd /Users/iamyuhaha/mine/saolei
   git init
   git add .
   git commit -m "Add Minesweeper AI"
   git hub create  # 如果安装了gh CLI
   git push -u origin main
   ```
3. 等待5-10分钟
4. 从Actions下载EXE

就这么简单！🎉
