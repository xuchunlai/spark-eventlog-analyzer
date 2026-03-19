# Spark性能指标参考

## 1. Event Log关键事件类型

| 事件类型 | 说明 | 提取命令 |
|---------|------|----------|
| SparkListenerApplicationStart | 应用启动 | `grep "SparkListenerApplicationStart"` |
| SparkListenerApplicationEnd | 应用结束 | `grep "SparkListenerApplicationEnd"` |
| SparkListenerJobStart | Job开始 | `grep "SparkListenerJobStart"` |
| SparkListenerJobEnd | Job结束 | `grep "SparkListenerJobEnd"` |
| SparkListenerStageSubmitted | Stage提交 | `grep "SparkListenerStageSubmitted"` |
| SparkListenerStageCompleted | Stage完成 | `grep "SparkListenerStageCompleted"` |
| SparkListenerTaskStart | Task开始 | `grep "SparkListenerTaskStart"` |
| SparkListenerTaskEnd | Task结束 | `grep "SparkListenerTaskEnd"` |
| SparkListenerSQLExecutionStart | SQL执行开始 | `grep "SparkListenerSQLExecutionStart"` |
| SparkListenerSQLExecutionEnd | SQL执行结束 | `grep "SparkListenerSQLExecutionEnd"` |

---

## 2. 关键指标提取

### 2.1 应用基本信息

```bash
# 应用ID
grep "SparkListenerApplicationStart" eventlog.json | grep -o '"App ID":"[^"]*"'

# 应用名称
grep "SparkListenerApplicationStart" eventlog.json | grep -o '"App Name":"[^"]*"'

# Spark版本
grep '"Spark Version"' eventlog.json | head -1

# 执行时间（毫秒时间戳转换）
grep "SparkListenerApplicationStart" eventlog.json | grep -o '"Timestamp":[0-9]*'
grep "SparkListenerApplicationEnd" eventlog.json | grep -o '"Timestamp":[0-9]*'
```

### 2.2 资源信息

```bash
# Executor配置
grep "SparkListenerResourceProfileAdded" eventlog.json

# 内存设置
grep -o '"spark.executor.memory":"[^"]*"' eventlog.json | head -1
grep -o '"spark.driver.memory":"[^"]*"' eventlog.json | head -1

# 核心数
grep -o '"spark.executor.cores":"[^"]*"' eventlog.json | head -1
```

### 2.3 Job/Stage/Task统计

```bash
# Job统计
grep -c "SparkListenerJobStart" eventlog.json
grep -c "SparkListenerJobEnd" eventlog.json
grep "SparkListenerJobEnd" eventlog.json | grep -c "JobSucceeded"
grep "SparkListenerJobEnd" eventlog.json | grep -c "JobFailed"

# Stage统计
grep -c "SparkListenerStageSubmitted" eventlog.json
grep -c "SparkListenerStageCompleted" eventlog.json

# Task统计
grep -c "SparkListenerTaskStart" eventlog.json
grep -c '"Reason":"Success"' eventlog.json
grep -c '"Failed":true' eventlog.json
```

---

## 3. SQL执行信息

### 3.1 SQL语句提取

```bash
# SQL描述
grep "SparkListenerSQLExecutionStart" eventlog.json | grep -o '"description":"[^"]*"'

# 物理执行计划
grep "physicalPlanDescription" eventlog.json

# SQL执行时间
grep "SparkListenerSQLExecutionStart" eventlog.json | grep -o '"time":[0-9]*'
grep "SparkListenerSQLExecutionEnd" eventlog.json | grep -o '"time":[0-9]*'
```

### 3.2 数据源信息

```bash
# 读取的表
grep -o '"tableName":"[^"]*"' eventlog.json | sort | uniq

# 分区信息
grep -o '"PartitionFilters":\[[^\]]*\]' eventlog.json

# 扫描的数据量
grep '"numOutputRows"' eventlog.json
```

---

## 4. Task执行指标

### 4.1 时间指标

| 指标 | 说明 | 单位 |
|------|------|------|
| Executor Deserialize Time | 反序列化时间 | ms |
| Executor Run Time | 执行时间 | ms |
| Result Serialization Time | 结果序列化时间 | ms |
| JVM GC Time | GC时间 | ms |

```bash
# 提取示例
grep '"Executor Run Time"' eventlog.json | head -5
```

### 4.2 数据量指标

| 指标 | 说明 | 单位 |
|------|------|------|
| Input Metrics/Bytes Read | 读取字节数 | bytes |
| Input Metrics/Records Read | 读取记录数 | count |
| Output Metrics/Bytes Written | 写入字节数 | bytes |
| Output Metrics/Records Written | 写入记录数 | count |
| Shuffle Read/Local Bytes Read | 本地Shuffle读取 | bytes |
| Shuffle Read/Remote Bytes Read | 远程Shuffle读取 | bytes |
| Shuffle Write/Shuffle Bytes Written | Shuffle写入 | bytes |

```bash
# 提取数据读取量
grep '"Bytes Read"' eventlog.json | awk -F': ' '{sum+=$2} END {print sum}'
```

---

## 5. 性能问题识别

### 5.1 数据倾斜检测

```bash
# 检查Task执行时间差异
grep '"Executor Run Time"' eventlog.json | sort -t: -k2 -n | tail -10

# 如果最大时间远大于平均值，说明有倾斜
```

### 5.2 OOM检测

```bash
# 查找内存溢出错误
grep -i "outofmemory" eventlog.json
grep -i "oom" eventlog.json
```

### 5.3 失败Task检测

```bash
# 查找失败的Task
grep '"Failed":true' eventlog.json | head -10

# 查找失败原因
grep -A10 '"Failed":true' eventlog.json | grep -E "(Reason|StackTrace)"
```

---

## 6. 执行计划分析

### 6.1 Join类型识别

| Join类型 | 说明 | 性能等级 |
|----------|------|----------|
| BroadcastHashJoin | 广播Join，小表广播 | ⭐⭐⭐ |
| SortMergeJoin | 排序合并Join | ⭐⭐ |
| ShuffleHashJoin | Shuffle哈希Join | ⭐ |
| CartesianProduct | 笛卡尔积 | ❌ |

```bash
# 提取Join类型
grep -o '"nodeName":"[^"]*Join[^"]*"' eventlog.json | sort | uniq -c
```

### 6.2 算子识别

| 算子 | 说明 |
|------|------|
| WholeStageCodegen | 全阶段代码生成（优化） |
| HashAggregate | 哈希聚合 |
| SortAggregate | 排序聚合 |
| Exchange | Shuffle交换 |
| Project | 投影（列选择） |
| Filter | 过滤 |
| Scan | 表扫描 |

```bash
# 提取算子
grep '"nodeName"' eventlog.json | sort | uniq -c | sort -rn | head -20
```

---

## 7. AQE（自适应查询执行）指标

```bash
# 检查AQE是否启用
grep -o '"spark.sql.adaptive.enabled":"[^"]*"' eventlog.json

# AQE优化事件
grep "AQEReoptimize" eventlog.json
grep "AQEShuffleRead" eventlog.json
```

---

## 8. 常用分析脚本片段

### 8.1 统计执行时间

```bash
# 应用总执行时间（毫秒转秒）
start_time=$(grep "SparkListenerApplicationStart" eventlog.json | grep -o '"Timestamp":[0-9]*' | head -1 | cut -d: -f2)
end_time=$(grep "SparkListenerApplicationEnd" eventlog.json | grep -o '"Timestamp":[0-9]*' | head -1 | cut -d: -f2)
echo "总执行时间: $(((end_time - start_time) / 1000)) 秒"
```

### 8.2 统计SQL执行数量

```bash
# SQL执行次数
grep -c "SparkListenerSQLExecutionStart" eventlog.json
```

### 8.3 检查Shuffle数据量

```bash
# 总Shuffle读取量
grep -o '"Shuffle Bytes Written":[0-9]*' eventlog.json | awk -F: '{sum+=$2} END {print "Shuffle写入: " sum/1024/1024/1024 " GB"}'
```

---

## 9. 健康度评估标准

| 指标 | 健康 | 警告 | 危险 |
|------|------|------|------|
| Job成功率 | >95% | 90-95% | <90% |
| Task成功率 | >99% | 95-99% | <95% |
| GC时间占比 | <10% | 10-20% | >20% |
| 数据倾斜比例 | <20% | 20-50% | >50% |
| Shuffle数据量 | <1GB | 1-10GB | >10GB |
