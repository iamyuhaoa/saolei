# Windows 打包说明

## 方法一：使用批处理脚本（推荐）

1. 将整个项目文件夹复制到Windows电脑
2. 双击运行 `build.bat`
3. 等待打包完成
4. 在 `dist` 文件夹中找到 `MinesweeperAI.exe`

## 方法二：手动打包

### 1. 安装依赖

在Windows命令提示符中运行：

```cmd
pip install -r requirements.txt
```

### 2. 安装PyInstaller

```cmd
pip install pyinstaller
```

### 3. 运行打包命令

```cmd
pyinstaller build.spec
```

或者使用命令行参数：

```cmd
pyinstaller --onefile --console --name MinesweeperAI --add-data "resources;resources" src/main.py
```

### 4. 查找输出

打包完成后，在 `dist` 文件夹中会生成 `MinesweeperAI.exe`

## 运行EXE

1. 打开Windows扫雷游戏
2. 双击运行 `dist\MinesweeperAI.exe`
3. 程序会自动开始玩扫雷

## 常见问题

### Q: EXE文件太大（>200MB）
A: 这是正常的，因为包含了OpenCV、numpy等库。可以考虑使用虚拟环境来减小体积。

### Q: 运行时提示缺少DLL
A: 确保目标Windows系统安装了：
- Microsoft Visual C++ Redistributable
- 或使用虚拟环境打包

### Q: 杀毒软件报毒
A: PyInstaller打包的程序可能被误报。添加到白名单即可。

## 高级配置

### 隐藏控制台窗口

修改 `build.spec` 中的 `console=True` 为 `console=False`

### 添加图标

1. 准备一个 `.ico` 文件放在 `resources/` 目录
2. 取消 `build.spec` 中 `icon='resources/icon.ico'` 的注释

### 优化体积

在 `build.spec` 的 `excludes` 中添加不需要的模块。
