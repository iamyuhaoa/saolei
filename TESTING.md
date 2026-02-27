# Windows EXE 测试指南

## 准备工作

### 1. 下载EXE

**方式A: 通过GitHub Actions**
1. 访问: https://github.com/iamyuhaoa/saolei/actions
2. 点击最新的 "Build Windows EXE" 构建记录
3. 滚动到 "Artifacts" 区域
4. 下载 `MinesweeperAI-Windows.zip`
5. 解压得到 `MinesweeperAI.exe`

**方式B: 使用命令行**
```bash
# 在项目目录运行
./download_exe.sh
```

### 2. 准备测试环境

- Windows 10/11 电脑
- Windows扫雷游戏（内置或Microsoft Store版本）
- 无需安装Python或其他依赖

## 测试步骤

### 测试1: 基本启动测试

```
1. 双击 MinesweeperAI.exe
2. 应该看到控制台窗口打开
3. 显示日志信息：
   ============================================
   Minesweeper AI Bot - Starting
   ============================================
```

**预期结果**: ✓ 程序正常启动，无错误提示

---

### 测试2: 窗口检测测试

```
1. 先不要打开扫雷游戏
2. 运行 MinesweeperAI.exe
```

**预期结果**:
```
✗ ERROR: Failed to connect to Minesweeper window
```

**说明**: 这是正常的，程序应该检测不到窗口

---

### 测试3: 完整游戏测试

```
1. 打开Windows扫雷游戏（初级难度）
   - 开始菜单 → 搜索 "Minesweeper" → 打开
   - 或从Microsoft Store安装

2. 运行 MinesweeperAI.exe

3. 观察控制台输出：
```

**预期输出**:
```
INFO: Initializing Minesweeper AI Bot...
INFO: Connected to window: (left, top, right, bottom)
INFO: Board size: 9x9
INFO: Starting game loop...
INFO: Making first move...
INFO: Executing 1 move(s)...
INFO: Found X deterministic moves
```

**观察AI行为**:
- AI会自动点击第一个格子（角落）
- 然后读取棋盘状态
- 计算并执行下一步移动
- 重复直到胜利或失败

---

### 测试4: 日志检查

程序运行后会生成 `minesweeper_ai.log` 文件。

**检查日志内容**:
```
2026-02-27 12:00:00 - __main__ - INFO - ========================================
2026-02-27 12:00:00 - __main__ - INFO - Minesweeper AI Bot - Starting
2026-02-27 12:00:00 - __main__ - INFO - ========================================
2026-02-27 12:00:01 - window_manager - INFO - Connected to window
2026-02-27 12:00:02 - board_manager - INFO - Detected grid: cell_size=(30, 30)
2026-02-27 12:00:03 - solver - INFO - Found 2 deterministic moves
...
```

---

## 测试检查清单

### 功能测试

- [ ] EXE能正常启动
- [ ] 能检测到扫雷窗口
- [ ] 能识别棋盘大小
- [ ] 能读取棋盘状态
- [ ] 能计算并执行移动
- [ ] 游戏结束时有提示
- [ ] 生成日志文件

### 兼容性测试

- [ ] Windows 10 64位
- [ ] Windows 11 64位
- [ ] 初级难度 (9x9, 10雷)
- [ ] 中级难度 (16x16, 40雷)
- [ ] 高级难度 (30x16, 99雷)

### 性能测试

- [ ] 每次移动响应时间 < 1秒
- [ ] 内存占用 < 500MB
- [ ] 不会卡死或崩溃

---

## 常见问题排查

### Q1: 提示 "找不到扫雷窗口"

**解决方案**:
1. 确保扫雷游戏已打开
2. 确保扫雷窗口标题包含 "Minesweeper"
3. 尝试以管理员权限运行EXE

### Q2: 提示 "无法识别棋盘"

**解决方案**:
1. 确保扫雷游戏完全可见（不要被其他窗口遮挡）
2. 调整扫雷窗口大小
3. 尝试不同的扫雷版本

### Q3: 杀毒软件报毒

**解决方案**:
1. 添加到白名单
2. PyInstaller打包的程序常被误报
3. 代码是开源的，可以安全使用

### Q4: EXE文件很大

**说明**:
- 包含OpenCV、numpy等大型库
- 正常大小约200-300MB
- 可以接受的范围

---

## 性能基准

根据测试，预期性能：

| 指标 | 预期值 |
|------|--------|
| 启动时间 | < 3秒 |
| 窗口检测 | < 1秒 |
| 棋盘识别 | < 2秒 |
| 每次移动 | < 0.5秒 |
| 初级游戏 | < 30秒 |
| 中级游戏 | < 2分钟 |
| 高级游戏 | < 5分钟 |

---

## 回报测试结果

如果发现任何问题，请记录以下信息：

1. Windows版本
2. 扫雷游戏版本
3. 错误信息（截图）
4. minesweeper_ai.log 内容
5. 重现步骤

提交到: https://github.com/iamyuhaoa/saolei/issues
