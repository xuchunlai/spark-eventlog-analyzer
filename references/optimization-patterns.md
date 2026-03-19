# Spark SQL 优化模式与最佳实践

## 1. 日期与分区优化

### 问题: 动态日期函数导致分区裁剪失效

**反模式**:
```sql
WHERE dt = regexp_replace(date_sub(CURRENT_DATE(),1),'-','')
```

**优化方案**:
```sql
-- 方案1: 使用固定值
WHERE dt = '20260309'

-- 方案2: 使用变量（参数化查询）
WHERE dt = ${biz_date}

-- 方案3: 如果必须使用动态日期，确保Spark配置支持
SET spark.sql.optimizer.dynamicPartitionPruning.enabled = true;
```

**预期收益**: 减少30-50%数据扫描量

---

## 2. Join优化

### 问题: LEFT JOIN + WHERE过滤产生大量空行

**反模式**:
```sql
LEFT JOIN so ON emp.emp_id = so.emp_id
WHERE so.sign_amount > 0
```

**优化方案**:
```sql
-- 改为INNER JOIN，减少中间数据量
INNER JOIN so ON emp.emp_id = so.emp_id 
    AND so.sign_amount > 0
```

**预期收益**: 减少Shuffle数据量，提升20-30%性能

---

### 问题: 大表Join数据倾斜

**反模式**:
```sql
-- 某些Key的数据量特别大，导致单Task执行缓慢
SELECT * FROM big_table a
JOIN small_table b ON a.key = b.key
```

**优化方案**:
```sql
-- 方案1: 加盐打散倾斜Key
SELECT 
    a.*,
    b.*
FROM (
    SELECT 
        CASE WHEN key IN ('hot_key1', 'hot_key2') 
             THEN concat(key, '_', rand() * 10)
             ELSE key END as salted_key,
        *
    FROM big_table
) a
JOIN (
    SELECT 
        key,
        explode(array(0,1,2,3,4,5,6,7,8,9)) as salt
    FROM small_table
    WHERE key IN ('hot_key1', 'hot_key2')
    UNION ALL
    SELECT key, null as salt FROM small_table
    WHERE key NOT IN ('hot_key1', 'hot_key2')
) b ON a.salted_key = concat(b.key, '_', b.salt)
   OR (a.key = b.key AND a.salted_key = a.key)

-- 方案2: 使用AQE自动处理倾斜
SET spark.sql.adaptive.skewJoin.enabled = true;
SET spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes = 64MB;
```

---

## 3. 窗口函数优化

### 问题: 全局窗口函数单点瓶颈

**反模式**:
```sql
ROW_NUMBER() OVER (ORDER BY amount DESC) AS rank
```

**优化方案**:
```sql
-- 添加PARTITION BY实现并行化
ROW_NUMBER() OVER (PARTITION BY area_name ORDER BY amount DESC) AS area_rank,
ROW_NUMBER() OVER (ORDER BY amount DESC) AS global_rank
```

**预期收益**: 分布式执行，性能提升N倍（取决于分区数）

---

## 4. 聚合优化

### 问题: 聚合数据倾斜

**反模式**:
```sql
SELECT key, count(*) 
FROM big_table
GROUP BY key
```

**优化方案**:
```sql
-- 两阶段聚合
SELECT key, sum(cnt) as total_cnt
FROM (
    SELECT key, count(*) as cnt
    FROM big_table
    GROUP BY key, rand() * 10  -- 加盐
) t
GROUP BY key
```

---

## 5. 代码规范优化

### 问题: 使用数字别名

**反模式**:
```sql
GROUP BY 1, 2, 3
```

**优化方案**:
```sql
GROUP BY area_name, comp_name, team_name
```

---

### 问题: 隐式类型转换

**反模式**:
```sql
WHERE flag1 + flag2 + flag3 = 0
```

**优化方案**:
```sql
WHERE flag1 = 0 AND flag2 = 0 AND flag3 = 0
```

---

## 6. 空值处理

### 问题: NULL值导致计算错误

**反模式**:
```sql
SELECT amount - discount AS net_amount
```

**优化方案**:
```sql
SELECT COALESCE(amount, 0) - COALESCE(discount, 0) AS net_amount
```

---

## 7. Spark配置优化

### 推荐配置

```sql
-- 启用AQE（自适应查询执行）
SET spark.sql.adaptive.enabled = true;
SET spark.sql.adaptive.coalescePartitions.enabled = true;
SET spark.sql.adaptive.skewJoin.enabled = true;

-- 动态分区裁剪
SET spark.sql.optimizer.dynamicPartitionPruning.enabled = true;

-- 广播Join阈值
SET spark.sql.autoBroadcastJoinThreshold = 100MB;

-- 文件合并
SET spark.sql.adaptive.coalescePartitions.minPartitionSize = 32MB;
SET spark.sql.adaptive.advisoryPartitionSizeInBytes = 128MB;
```

---

## 8. 优先级分类

### P0 - 立即处理（性能瓶颈）
- 全表扫描（无分区过滤）
- 数据倾斜严重的Join
- 笛卡尔积
- 单点全局窗口函数

### P1 - 本周处理（重要优化）
- 不合理的Join类型
- 缺少两阶段聚合
- 动态日期函数
- 广播Join未启用

### P2 - 本月处理（规范改进）
- 数字别名改为列名
- 添加必要注释
- 统一代码格式
- 规范命名

### P3 - 长期规划（架构优化）
- 表结构优化
- 数据治理
- 建立SQL Review机制
- 自动化测试

---

## 9. 优化前后对比模板

```markdown
## 优化案例: [功能名称]

### 优化前
```sql
[原始SQL]
```
**问题**:
- 问题1
- 问题2

**性能**:
- 执行时间: XX秒
- 扫描数据量: XX GB

### 优化后
```sql
[优化后的SQL]
```
**改进**:
- 改进1
- 改进2

**性能**:
- 执行时间: XX秒 (提升XX%)
- 扫描数据量: XX GB (减少XX%)
```
