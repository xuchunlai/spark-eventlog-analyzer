#!/usr/bin/env python3
"""
Spark Event Log分析脚本示例
用于提取关键指标和生成分析数据
"""

import json
import sys
from datetime import datetime

def analyze_eventlog(file_path):
    """分析Spark event log文件"""
    
    results = {
        "app_info": {},
        "jobs": {"total": 0, "succeeded": 0, "failed": 0},
        "stages": {"total": 0},
        "tasks": {"total": 0, "succeeded": 0, "failed": 0},
        "sqls": []
    }
    
    with open(file_path, 'r') as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                event_type = event.get("Event", "")
                
                # 应用信息
                if event_type == "SparkListenerApplicationStart":
                    results["app_info"]["app_id"] = event.get("App ID", "")
                    results["app_info"]["app_name"] = event.get("App Name", "")
                    results["app_info"]["start_time"] = event.get("Timestamp", 0)
                    
                elif event_type == "SparkListenerApplicationEnd":
                    results["app_info"]["end_time"] = event.get("Timestamp", 0)
                    
                # Job统计
                elif event_type == "SparkListenerJobStart":
                    results["jobs"]["total"] += 1
                elif event_type == "SparkListenerJobEnd":
                    job_result = event.get("Job Result", {}).get("Result", "")
                    if job_result == "JobSucceeded":
                        results["jobs"]["succeeded"] += 1
                    else:
                        results["jobs"]["failed"] += 1
                        
                # Stage统计
                elif event_type == "SparkListenerStageSubmitted":
                    results["stages"]["total"] += 1
                    
                # Task统计
                elif event_type == "SparkListenerTaskEnd":
                    results["tasks"]["total"] += 1
                    task_info = event.get("Task Info", {})
                    if task_info.get("Failed", False):
                        results["tasks"]["failed"] += 1
                    else:
                        results["tasks"]["succeeded"] += 1
                        
                # SQL执行
                elif event_type == "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart":
                    sql_info = {
                        "execution_id": event.get("executionId", 0),
                        "description": event.get("description", ""),
                        "time": event.get("time", 0)
                    }
                    results["sqls"].append(sql_info)
                    
            except json.JSONDecodeError:
                continue
    
    # 计算执行时间
    if "start_time" in results["app_info"] and "end_time" in results["app_info"]:
        duration_ms = results["app_info"]["end_time"] - results["app_info"]["start_time"]
        results["app_info"]["duration_sec"] = duration_ms / 1000
    
    return results

def print_report(results):
    """打印分析报告"""
    print("=" * 60)
    print("Spark Event Log 分析报告")
    print("=" * 60)
    
    print("\n【应用信息】")
    print(f"  应用ID: {results['app_info'].get('app_id', 'N/A')}")
    print(f"  应用名称: {results['app_info'].get('app_name', 'N/A')}")
    if 'duration_sec' in results['app_info']:
        print(f"  执行时长: {results['app_info']['duration_sec']:.2f} 秒")
    
    print("\n【Job统计】")
    print(f"  总Jobs: {results['jobs']['total']}")
    print(f"  成功: {results['jobs']['succeeded']}")
    print(f"  失败: {results['jobs']['failed']}")
    
    print("\n【Stage统计】")
    print(f"  总Stages: {results['stages']['total']}")
    
    print("\n【Task统计】")
    print(f"  总Tasks: {results['tasks']['total']}")
    print(f"  成功: {results['tasks']['succeeded']}")
    print(f"  失败: {results['tasks']['failed']}")
    
    print("\n【SQL执行】")
    print(f"  SQL语句数: {len(results['sqls'])}")
    for sql in results['sqls'][:5]:  # 只显示前5个
        print(f"    - [{sql['execution_id']}] {sql['description'][:50]}...")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 analyze_eventlog.py <event_log_file.json>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    results = analyze_eventlog(file_path)
    print_report(results)
