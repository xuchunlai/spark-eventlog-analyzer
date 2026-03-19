---
name: spark-eventlog-analyzer
description: |
  专业的Spark Event Log分析工具，用于深入分析Spark SQL任务的执行日志，提取SQL语句、物理执行计划、任务运行状况，并给出性能评分和优化建议。
  
  适用场景：
  1. 分析Spark任务event log文件（application_*.json）
  2. 诊断Spark SQL性能问题
  3. 生成任务健康报告和优化建议
  4. 评估SQL代码质量
  
  当用户上传Spark event log文件、询问"分析Spark任务"、提到"eventlog"、"Spark任务性能"时触发此skill。
---

# Spark Event Log 分析器

专业的Spark SQL任务分析工具，从event log中提取关键信息，评估任务健康度，并给出优化建议。

## 快速开始

```bash
# 分析单个event log文件
分析Spark任务: /path/to/application_xxx.json

# 获取分析报告
分析完成后生成报告，包含：
- 任务执行概览
- SQL语句提取
- 物理执行计划
- 健康状态评估
- 性能评分
- 优化建议
```

## 分析流程

### 步骤1：文件识别与加载

确认用户提供的文件是Spark event log：
- 文件名格式：`application_xxxxxxxxxxxxx.json`
- 文件内容包含：`SparkListener` 事件

### 步骤2：基本信息提取

使用grep/jq提取关键元数据：
```bash
# 获取应用信息
grep "SparkListenerApplicationStart" eventlog.json
grep "SparkListenerEnvironmentUpdate" eventlog.json

# 统计Jobs/Stages/Tasks
grep -c "SparkListenerJob" eventlog.json
grep -c "SparkListenerStage" eventlog.json
grep -c "SparkListenerTask" eventlog.json
```

### 步骤3：SQL分析

提取SQL执行相关信息：
```bash
# 提取SQL语句
grep "SparkListenerSQLExecutionStart" eventlog.json

# 提取物理执行计划
grep "physicalPlanDescription" eventlog.json

# 分析数据源
grep -E "(HiveTableRelation|LogicalRelation)" eventlog.json
```

### 步骤4：执行状况评估

检查任务执行结果：
```bash
# 成功/失败统计
grep "SparkListenerJobEnd" eventlog.json | grep -c "JobSucceeded"
grep "SparkListenerJobEnd" eventlog.json | grep -c "JobFailed"

# 检查任务失败原因
grep -A5 "Task Failed" eventlog.json
```

### 步骤5：性能评分

参考 [references/scoring-rubric.md](references/scoring-rubric.md) 进行多维度评分：
- 性能优化 (40%)
- 代码规范 (30%)
- 可维护性 (20%)
- 健壮性 (10%)

### 步骤6：生成优化建议

参考 [references/optimization-patterns.md](references/optimization-patterns.md) 生成针对性建议：
- P0 (立即处理): 严重性能问题
- P1 (本周处理): 重要优化项
- P2 (本月处理): 规范改进
- P3 (长期规划): 架构优化

## 输出格式

### 报告结构

```markdown
# Spark任务分析报告

## 一、任务概述
- 应用ID、名称、版本
- 执行时间、资源配置

## 二、SQL分析
- 执行的SQL语句清单
- 核心业务SQL提取

## 三、物理执行计划
- 数据源统计
- 执行算子流程

## 四、任务运行状况
- Job/Stage/Task统计
- 成功率分析

## 五、健康状态评估
- 整体评分
- 风险识别

## 六、SQL质量评分
- 多维度评分
- 问题清单

## 七、优化建议
- 关键优化点
- 优化后SQL示例
- 预期收益

## 八、结论与行动项
- 总体结论
- 优先级行动建议
```

## 安全注意事项

⚠️ **隐私保护**: 
- 报告中不得包含邮箱、手机号、卡号等敏感信息
- 服务器地址、IP地址需脱敏处理
- Token/密码等凭证信息必须隐藏

## 参考文档

- [评分标准](references/scoring-rubric.md) - SQL质量评分细则
- [优化模式](references/optimization-patterns.md) - 常见优化方案
- [Spark指标](references/spark-metrics.md) - Spark性能指标说明

## 示例用法

**示例1: 分析event log文件**
```
用户: 分析这个Spark任务: application_1769020467751_1751613.json
AI: [执行分析流程，生成完整报告]
```

**示例2: 诊断性能问题**
```
用户: 我的Spark任务运行很慢，帮我看看event log
AI: [提取执行计划，识别瓶颈，给出优化建议]
```

**示例3: SQL质量评估**
```
用户: 评估这个Spark SQL的质量
AI: [多维度评分，列出问题，提供优化后的SQL]
```
