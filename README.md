# Spark Event Log Analyzer

OpenClaw Skill - 专业的Spark SQL任务分析工具

## 功能

- 📊 分析Spark Event Log文件
- 🔍 提取SQL语句和执行计划
- 📈 任务运行状况评估
- ⭐ SQL质量评分（4维度）
- 💡 性能优化建议

## 安装

```bash
# 复制到OpenClaw skills目录
cp -r spark-eventlog-analyzer ~/.openclaw/skills/

# 或解压到工作区
tar -xzf spark-eventlog-analyzer.tar.gz -C /path/to/workspace/skills/
```

## 使用

在OpenClaw中：

```
分析这个Spark任务: application_xxx.json
```

或直接运行脚本：

```bash
python3 scripts/analyze_eventlog.py application_xxx.json
```

## 文件结构

```
spark-eventlog-analyzer/
├── SKILL.md                    # 主技能文档
├── references/
│   ├── scoring-rubric.md       # 评分标准
│   ├── optimization-patterns.md # 优化模式
│   └── spark-metrics.md        # Spark指标参考
└── scripts/
    └── analyze_eventlog.py     # 分析脚本
```

## License

MIT
