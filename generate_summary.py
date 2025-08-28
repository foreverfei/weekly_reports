#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成学生周报进度分析简化版总结报告
专门针对导师需要快速了解学生情况的场景
"""

import os
import json
from pathlib import Path
from analyze_progress import WeeklyReportAnalyzer


def generate_quick_summary():
    """生成快速总结报告"""
    
    # 创建分析器并运行分析
    analyzer = WeeklyReportAnalyzer('.')
    analyzer.scan_reports()
    
    print("=" * 60)
    print("学生研究进度快速总结 - 导师指导参考")
    print("=" * 60)
    
    # 按综合表现排序学生
    student_scores = []
    for student_name in analyzer.student_reports:
        reports = analyzer.student_reports[student_name]
        if reports:
            avg_score = sum([
                sum(r.work_volume_score for r in reports),
                sum(r.progress_quality_score for r in reports),
                sum(r.problem_handling_score for r in reports)
            ]) / (3 * len(reports))
            student_scores.append((student_name, avg_score, len(reports)))
    
    student_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 需要重点关注的学生（评分<60分）
    concern_students = [s for s in student_scores if s[1] < 60]
    excellent_students = [s for s in student_scores if s[1] >= 85]
    
    if concern_students:
        print("\n🚨 【需要重点关注的学生】")
        print("-" * 40)
        for name, score, reports_count in concern_students:
            analysis = analyzer.analyze_student_progress(name)
            recent = analysis['recent_performance']
            
            print(f"👤 {name} (综合评分: {score:.1f}分)")
            print(f"   📊 报告数量: {reports_count}份")
            print(f"   📈 最近表现: 工作量{recent['average_work_volume']:.0f} | "
                  f"规划{recent['average_progress_quality']:.0f} | "
                  f"问题处理{recent['average_problem_handling']:.0f}")
            
            if recent['recent_concerns']:
                print(f"   ⚠️  关注点: {'; '.join(recent['recent_concerns'][:2])}")
            
            # 显示最紧急的建议
            recommendations = analysis['recommendations'][:2]
            for rec in recommendations:
                print(f"   💡 建议: {rec}")
            print()
    
    print("\n✅ 【表现优秀的学生】")
    print("-" * 40)
    for name, score, reports_count in excellent_students[:5]:  # 显示前5名
        analysis = analyzer.analyze_student_progress(name)
        work_patterns = analysis['work_patterns']
        
        print(f"🌟 {name} (综合评分: {score:.1f}分)")
        print(f"   📊 {reports_count}份报告 | 高产周数: {work_patterns['productivity_weeks']}")
        
        # 显示主要工作类型
        primary_work = dict(work_patterns['primary_work_types'].most_common(2))
        if primary_work:
            work_types = ', '.join([f"{k}({v})" for k, v in primary_work.items()])
            print(f"   🔬 主要工作: {work_types}")
        print()
    
    print("\n📋 【整体情况分析】")
    print("-" * 40)
    
    total_reports = len(analyzer.reports)
    total_students = len(analyzer.student_reports)
    
    # 计算整体指标
    all_work_scores = [r.work_volume_score for r in analyzer.reports]
    all_quality_scores = [r.progress_quality_score for r in analyzer.reports]
    empty_reports = sum(1 for score in all_work_scores if score == 0)
    
    print(f"📊 总体数据: {total_students}名学生，{total_reports}份周报")
    print(f"📈 平均工作量评分: {sum(all_work_scores)/len(all_work_scores):.1f}")
    print(f"📋 平均规划质量: {sum(all_quality_scores)/len(all_quality_scores):.1f}")
    
    if empty_reports > 0:
        print(f"⚠️  发现 {empty_reports} 份空白/极简报告 ({empty_reports/total_reports*100:.1f}%)")
    
    # 活跃度分布
    high_volume_weeks = sum(1 for score in all_work_scores if score >= 70)
    low_volume_weeks = sum(1 for score in all_work_scores if score <= 30)
    
    print(f"📊 活跃度分布: 高活跃{high_volume_weeks}周 ({high_volume_weeks/total_reports*100:.1f}%), "
          f"低活跃{low_volume_weeks}周 ({low_volume_weeks/total_reports*100:.1f}%)")
    
    print("\n💡 【总体指导建议】")
    print("-" * 40)
    
    if empty_reports > total_reports * 0.1:  # 超过10%的空报告
        print("• 建议建立更严格的周报监督机制，确保报告质量")
    
    if len(concern_students) > 0:
        print(f"• {len(concern_students)}名学生需要个别指导，建议安排面谈")
    
    if low_volume_weeks > total_reports * 0.3:  # 超过30%的低活跃周
        print("• 整体研究活跃度偏低，建议检查研究方向和资源配置")
    else:
        print("• 整体研究活跃度良好，继续保持")
    
    print("\n" + "=" * 60)


def generate_individual_alerts():
    """生成个别学生预警信息"""
    
    analyzer = WeeklyReportAnalyzer('.')
    analyzer.scan_reports()
    
    print("\n🔔 【个别学生预警提醒】")
    print("-" * 50)
    
    alert_count = 0
    
    for student_name in sorted(analyzer.student_reports.keys()):
        reports = analyzer.student_reports[student_name]
        if len(reports) < 3:  # 数据不足
            continue
            
        analysis = analyzer.analyze_student_progress(student_name)
        recent = analysis['recent_performance']
        
        alerts = []
        
        # 检查最近工作量
        if recent['average_work_volume'] < 30:
            alerts.append(f"工作量严重不足({recent['average_work_volume']:.0f}分)")
        
        # 检查连续空报告
        recent_scores = analysis['score_trends']['work_volume'][-5:]  # 最近5周
        zero_count = recent_scores.count(0)
        if zero_count >= 3:
            alerts.append(f"连续{zero_count}周无实质工作")
        
        # 检查下降趋势
        consistency = analysis['consistency']
        if not consistency.get('insufficient_data'):
            work_trend = consistency.get('work_volume', {}).get('trend', 'stable')
            if work_trend == 'declining':
                alerts.append("工作量呈下降趋势")
        
        # 检查问题处理能力
        problem_patterns = analysis['problem_patterns']
        if problem_patterns['problem_solving_rate'] < 0.3 and problem_patterns['weeks_with_problems'] >= 3:
            alerts.append("问题解决能力较弱")
        
        if alerts:
            alert_count += 1
            print(f"⚠️  {student_name}:")
            for alert in alerts:
                print(f"    • {alert}")
            
            # 给出具体的行动建议
            if "工作量严重不足" in str(alerts) or "连续" in str(alerts):
                print(f"    🎯 建议: 尽快安排一对一面谈，了解具体困难")
            elif "下降趋势" in str(alerts):
                print(f"    🎯 建议: 关注状态变化，适当调整研究计划")
            print()
    
    if alert_count == 0:
        print("✅ 暂无需要特别关注的异常情况")
    else:
        print(f"📊 共发现 {alert_count} 名学生需要关注")


def main():
    """主函数"""
    print("正在分析学生周报数据...")
    
    # 生成快速总结
    generate_quick_summary()
    
    # 生成预警信息
    generate_individual_alerts()
    
    print(f"\n💾 详细数据已保存在 analysis_results/ 文件夹")
    print(f"📄 完整报告请查看: analysis_results/综合分析报告.md")


if __name__ == "__main__":
    main()