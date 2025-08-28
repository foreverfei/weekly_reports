#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生周报进度分析系统
分析每个学生每周的工作进度，判断工作量和研究进度是否正常，给出合理的指导建议
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import argparse


@dataclass
class WeeklyReport:
    """周报数据结构"""
    student_name: str
    semester: str
    week: str
    file_path: str
    
    # 工作内容
    experiments: List[str]
    data_processing: List[str]
    algorithm_development: List[str]
    literature_reading: List[str]
    paper_writing: List[str]
    
    # 问题和困难
    technical_difficulties: List[str]
    theoretical_confusion: List[str]
    experiment_problems: List[str]
    other_problems: List[str]
    
    # 解决方案
    problem_analysis: List[str]
    solutions: List[str]
    help_sought: List[str]
    
    # 下周计划
    next_goals: List[str]
    next_tasks: List[str]
    time_arrangement: List[str]
    
    # 支持需求
    mentor_advice_needed: List[str]
    resource_requirements: List[str]
    
    # 其他
    personal_reflection: List[str]
    
    # 评估指标
    work_volume_score: int = 0  # 工作量评分 (0-100)
    progress_quality_score: int = 0  # 进度质量评分 (0-100)
    problem_handling_score: int = 0  # 问题处理评分 (0-100)


class WeeklyReportAnalyzer:
    """周报分析器"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.reports: List[WeeklyReport] = []
        self.student_reports: Dict[str, List[WeeklyReport]] = defaultdict(list)
        
    def scan_reports(self) -> None:
        """扫描所有周报文件"""
        print("正在扫描周报文件...")
        
        pattern = re.compile(r'(.+)_本周进度.*\.md$')
        
        for md_file in self.repo_path.rglob('*.md'):
            if md_file.name in ['README.md', '写作建议.md']:
                continue
                
            match = pattern.match(md_file.name)
            if match and match.group(1) != 'XX':  # 排除模板文件
                student_name = match.group(1)
                semester, week = self._extract_semester_week(md_file)
                
                if semester and week:
                    report = self._parse_report(md_file, student_name, semester, week)
                    if report:
                        self.reports.append(report)
                        self.student_reports[student_name].append(report)
        
        # 按时间排序
        for student_name in self.student_reports:
            self.student_reports[student_name].sort(
                key=lambda r: (r.semester, self._week_to_number(r.week))
            )
        
        print(f"共扫描到 {len(self.reports)} 份周报，涵盖 {len(self.student_reports)} 名学生")
    
    def _extract_semester_week(self, file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """从文件路径提取学期和周次信息"""
        parts = file_path.parts
        
        semester = None
        week = None
        
        for part in parts:
            if '学期' in part:
                semester = part
            elif part.startswith('第') and ('周' in part):
                week = part
        
        # 处理根目录下的第一周
        if not semester and '第一周' in parts:
            semester = '其他'
            week = '第一周'
            
        return semester, week
    
    def _week_to_number(self, week_str: str) -> int:
        """将周次字符串转换为数字，用于排序"""
        if not week_str:
            return 0
        
        # 提取数字
        match = re.search(r'第(\d+)周', week_str)
        if match:
            return int(match.group(1))
        
        # 特殊处理
        week_map = {
            '第一周': 1,
            '第二周': 2,
            '第三周': 3,
            '第四周': 4,
            '第五周': 5,
            '第六周': 6,
            '第七周': 7,
            '第八周': 8,
            '第九周': 9,
            '第十周': 10,
        }
        
        return week_map.get(week_str, 0)
    
    def _parse_report(self, file_path: Path, student_name: str, semester: str, week: str) -> Optional[WeeklyReport]:
        """解析单个周报文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            report = WeeklyReport(
                student_name=student_name,
                semester=semester,
                week=week,
                file_path=str(file_path),
                experiments=[],
                data_processing=[],
                algorithm_development=[],
                literature_reading=[],
                paper_writing=[],
                technical_difficulties=[],
                theoretical_confusion=[],
                experiment_problems=[],
                other_problems=[],
                problem_analysis=[],
                solutions=[],
                help_sought=[],
                next_goals=[],
                next_tasks=[],
                time_arrangement=[],
                mentor_advice_needed=[],
                resource_requirements=[],
                personal_reflection=[]
            )
            
            # 解析各个部分
            sections = self._split_into_sections(content)
            
            # 解析本周完成的工作
            work_section = sections.get('本周完成的工作', '')
            report.experiments = self._extract_items(work_section, '实验设计与实施')
            report.data_processing = self._extract_items(work_section, '数据收集与处理')
            report.algorithm_development = self._extract_items(work_section, '算法开发与优化')
            report.literature_reading = self._extract_items(work_section, '文献阅读')
            report.paper_writing = self._extract_items(work_section, '论文撰写')
            
            # 解析困难和问题
            problems_section = sections.get('遇到的困难和问题', '')
            report.technical_difficulties = self._extract_items(problems_section, '技术难点')
            report.theoretical_confusion = self._extract_items(problems_section, '理论疑惑')
            report.experiment_problems = self._extract_items(problems_section, '实验问题')
            report.other_problems = self._extract_items(problems_section, '其他问题')
            
            # 解析解决方案
            solutions_section = sections.get('解决方案与已采取的措施', '')
            report.problem_analysis = self._extract_items(solutions_section, '问题分析')
            report.solutions = self._extract_items(solutions_section, '解决方法')
            report.help_sought = self._extract_items(solutions_section, '寻求的帮助')
            
            # 解析下周计划
            plan_section = sections.get('下周工作计划', '')
            report.next_goals = self._extract_items(plan_section, '主要目标')
            report.next_tasks = self._extract_items(plan_section, '具体任务')
            report.time_arrangement = self._extract_items(plan_section, '时间安排')
            
            # 解析支持需求
            support_section = sections.get('需要的支持与资源', '')
            report.mentor_advice_needed = self._extract_items(support_section, '导师建议')
            report.resource_requirements = self._extract_items(support_section, '资源需求')
            
            # 解析其他备注
            notes_section = sections.get('其他备注', '')
            report.personal_reflection = self._extract_items(notes_section, '个人心得')
            
            # 计算评估分数
            report.work_volume_score = self._calculate_work_volume_score(report)
            report.progress_quality_score = self._calculate_progress_quality_score(report)
            report.problem_handling_score = self._calculate_problem_handling_score(report)
            
            return report
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return None
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """将内容按部分分割"""
        sections = {}
        
        # 定义部分标题模式
        section_patterns = [
            '本周完成的工作',
            '遇到的困难和问题',
            '解决方案与已采取的措施',
            '下周工作计划',
            '需要的支持与资源',
            '其他备注'
        ]
        
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 检查是否是新部分的开始
            found_section = None
            for pattern in section_patterns:
                if pattern in line and line.startswith('#'):
                    found_section = pattern
                    break
            
            if found_section:
                # 保存之前的部分
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                current_section = found_section
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个部分
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_items(self, section_content: str, subsection_name: str) -> List[str]:
        """从部分内容中提取特定子部分的条目"""
        items = []
        
        if not section_content or not subsection_name:
            return items
        
        lines = section_content.split('\n')
        in_target_section = False
        
        for line in lines:
            line = line.strip()
            
            if subsection_name in line:
                in_target_section = True
                continue
            
            # 检查是否进入了新的子部分
            if in_target_section and line and ':' in line and any(
                keyword in line for keyword in ['实验', '数据', '算法', '文献', '论文', '技术', '理论', '问题', '分析', '方法', '帮助', '目标', '任务', '时间', '建议', '资源', '心得']
            ):
                if subsection_name not in line:
                    break
            
            if in_target_section and line:
                # 清理格式，提取实际内容
                cleaned = self._clean_item_text(line)
                if cleaned and cleaned not in ['无', '暂无', '**无**']:
                    items.append(cleaned)
        
        return items
    
    def _clean_item_text(self, text: str) -> str:
        """清理条目文本"""
        # 移除markdown格式
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'^[-*•]\s*', '', text)  # 移除列表标记
        text = text.strip()
        
        # 移除空的描述
        if text in ['描述已进行的实验及其目的。（没有就空过）', '收集了哪些数据，如何处理和分析。',
                   '开发或改进了哪些算法，性能提升情况。', '阅读了哪些论文或书籍，主要收获与启发。',
                   '已完成的章节或部分，修改了哪些内容。']:
            return ''
        
        return text
    
    def _calculate_work_volume_score(self, report: WeeklyReport) -> int:
        """计算工作量评分"""
        score = 0
        
        # 各项工作的基础分数
        if report.experiments:
            score += min(len(report.experiments) * 15, 25)
        if report.data_processing:
            score += min(len(report.data_processing) * 10, 15)
        if report.algorithm_development:
            score += min(len(report.algorithm_development) * 20, 30)
        if report.literature_reading:
            score += min(len(report.literature_reading) * 8, 20)
        if report.paper_writing:
            score += min(len(report.paper_writing) * 12, 20)
        
        # 内容质量评估（基于字符数）
        total_chars = sum([
            sum(len(item) for item in report.experiments),
            sum(len(item) for item in report.data_processing),
            sum(len(item) for item in report.algorithm_development),
            sum(len(item) for item in report.literature_reading),
            sum(len(item) for item in report.paper_writing)
        ])
        
        if total_chars > 500:
            score += 10
        elif total_chars > 200:
            score += 5
        
        return min(score, 100)
    
    def _calculate_progress_quality_score(self, report: WeeklyReport) -> int:
        """计算进度质量评分"""
        score = 50  # 基础分
        
        # 有具体的下周计划
        if report.next_goals:
            score += 15
        if report.next_tasks:
            score += 15
        if report.time_arrangement:
            score += 10
        
        # 有问题分析和解决方案
        if report.problem_analysis:
            score += 10
        if report.solutions:
            score += 15
        
        # 有个人反思
        if report.personal_reflection:
            score += 10
        
        # 寻求帮助表明积极态度
        if report.help_sought or report.mentor_advice_needed:
            score += 5
        
        # 内容详实度
        total_planning_chars = sum([
            sum(len(item) for item in report.next_goals),
            sum(len(item) for item in report.next_tasks),
            sum(len(item) for item in report.problem_analysis),
            sum(len(item) for item in report.solutions)
        ])
        
        if total_planning_chars > 300:
            score += 10
        elif total_planning_chars > 100:
            score += 5
        
        return min(score, 100)
    
    def _calculate_problem_handling_score(self, report: WeeklyReport) -> int:
        """计算问题处理评分"""
        # 如果没有问题，给予基础分
        has_problems = any([
            report.technical_difficulties,
            report.theoretical_confusion,
            report.experiment_problems,
            report.other_problems
        ])
        
        if not has_problems:
            return 80  # 没有问题的基础分
        
        score = 20  # 有问题的基础分
        
        # 有问题分析
        if report.problem_analysis:
            score += 25
        
        # 有解决方案
        if report.solutions:
            score += 30
        
        # 寻求帮助
        if report.help_sought:
            score += 15
        
        # 问题处理的详细程度
        problem_handling_chars = sum([
            sum(len(item) for item in report.problem_analysis),
            sum(len(item) for item in report.solutions),
            sum(len(item) for item in report.help_sought)
        ])
        
        if problem_handling_chars > 200:
            score += 10
        elif problem_handling_chars > 50:
            score += 5
        
        return min(score, 100)
    
    def analyze_student_progress(self, student_name: str) -> Dict[str, Any]:
        """分析单个学生的整体进度"""
        reports = self.student_reports.get(student_name, [])
        if not reports:
            return {}
        
        analysis = {
            'student_name': student_name,
            'total_reports': len(reports),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'score_trends': {
                'work_volume': [r.work_volume_score for r in reports],
                'progress_quality': [r.progress_quality_score for r in reports],
                'problem_handling': [r.problem_handling_score for r in reports]
            },
            'average_scores': {
                'work_volume': sum(r.work_volume_score for r in reports) / len(reports),
                'progress_quality': sum(r.progress_quality_score for r in reports) / len(reports),
                'problem_handling': sum(r.problem_handling_score for r in reports) / len(reports)
            },
            'work_patterns': self._analyze_work_patterns(reports),
            'problem_patterns': self._analyze_problem_patterns(reports),
            'consistency': self._analyze_consistency(reports),
            'recent_performance': self._analyze_recent_performance(reports),
            'recommendations': self._generate_recommendations(reports)
        }
        
        return analysis
    
    def _analyze_work_patterns(self, reports: List[WeeklyReport]) -> Dict[str, Any]:
        """分析工作模式"""
        patterns = {
            'primary_work_types': Counter(),
            'work_distribution': {
                'experiments': 0,
                'data_processing': 0,
                'algorithm_development': 0,
                'literature_reading': 0,
                'paper_writing': 0
            },
            'productivity_weeks': 0,
            'low_activity_weeks': 0
        }
        
        for report in reports:
            # 统计各类工作的频次
            if report.experiments:
                patterns['primary_work_types']['实验'] += 1
                patterns['work_distribution']['experiments'] += len(report.experiments)
            if report.data_processing:
                patterns['primary_work_types']['数据处理'] += 1
                patterns['work_distribution']['data_processing'] += len(report.data_processing)
            if report.algorithm_development:
                patterns['primary_work_types']['算法开发'] += 1
                patterns['work_distribution']['algorithm_development'] += len(report.algorithm_development)
            if report.literature_reading:
                patterns['primary_work_types']['文献阅读'] += 1
                patterns['work_distribution']['literature_reading'] += len(report.literature_reading)
            if report.paper_writing:
                patterns['primary_work_types']['论文撰写'] += 1
                patterns['work_distribution']['paper_writing'] += len(report.paper_writing)
            
            # 判断周活跃度
            if report.work_volume_score >= 70:
                patterns['productivity_weeks'] += 1
            elif report.work_volume_score <= 30:
                patterns['low_activity_weeks'] += 1
        
        return patterns
    
    def _analyze_problem_patterns(self, reports: List[WeeklyReport]) -> Dict[str, Any]:
        """分析问题模式"""
        patterns = {
            'common_difficulties': Counter(),
            'problem_solving_rate': 0,
            'help_seeking_frequency': 0,
            'weeks_with_problems': 0,
            'weeks_with_solutions': 0
        }
        
        for report in reports:
            has_problems = any([
                report.technical_difficulties,
                report.theoretical_confusion,
                report.experiment_problems,
                report.other_problems
            ])
            
            if has_problems:
                patterns['weeks_with_problems'] += 1
                
                # 统计困难类型
                if report.technical_difficulties:
                    patterns['common_difficulties']['技术难点'] += 1
                if report.theoretical_confusion:
                    patterns['common_difficulties']['理论疑惑'] += 1
                if report.experiment_problems:
                    patterns['common_difficulties']['实验问题'] += 1
                if report.other_problems:
                    patterns['common_difficulties']['其他问题'] += 1
                
                # 检查是否有解决方案
                if report.solutions or report.problem_analysis:
                    patterns['weeks_with_solutions'] += 1
            
            if report.help_sought or report.mentor_advice_needed:
                patterns['help_seeking_frequency'] += 1
        
        # 计算问题解决率
        if patterns['weeks_with_problems'] > 0:
            patterns['problem_solving_rate'] = patterns['weeks_with_solutions'] / patterns['weeks_with_problems']
        
        return patterns
    
    def _analyze_consistency(self, reports: List[WeeklyReport]) -> Dict[str, Any]:
        """分析工作一致性"""
        if len(reports) < 3:
            return {'insufficient_data': True}
        
        scores = {
            'work_volume': [r.work_volume_score for r in reports],
            'progress_quality': [r.progress_quality_score for r in reports],
            'problem_handling': [r.problem_handling_score for r in reports]
        }
        
        consistency = {}
        
        for score_type, score_list in scores.items():
            # 计算标准差作为一致性指标
            mean_score = sum(score_list) / len(score_list)
            variance = sum((x - mean_score) ** 2 for x in score_list) / len(score_list)
            std_dev = variance ** 0.5
            
            consistency[score_type] = {
                'mean': mean_score,
                'std_dev': std_dev,
                'coefficient_of_variation': std_dev / mean_score if mean_score > 0 else 0,
                'trend': self._calculate_trend(score_list)
            }
        
        return consistency
    
    def _calculate_trend(self, scores: List[int]) -> str:
        """计算分数趋势"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # 简单线性趋势计算
        n = len(scores)
        x_sum = sum(range(n))
        y_sum = sum(scores)
        xy_sum = sum(i * scores[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        if slope > 2:
            return 'improving'
        elif slope < -2:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_recent_performance(self, reports: List[WeeklyReport]) -> Dict[str, Any]:
        """分析最近的表现"""
        if len(reports) < 3:
            recent_reports = reports
        else:
            recent_reports = reports[-3:]  # 最近3周
        
        performance = {
            'period': f"最近{len(recent_reports)}周",
            'average_work_volume': sum(r.work_volume_score for r in recent_reports) / len(recent_reports),
            'average_progress_quality': sum(r.progress_quality_score for r in recent_reports) / len(recent_reports),
            'average_problem_handling': sum(r.problem_handling_score for r in recent_reports) / len(recent_reports),
            'recent_highlights': [],
            'recent_concerns': []
        }
        
        # 找出亮点和关注点
        for report in recent_reports:
            if report.work_volume_score >= 80:
                performance['recent_highlights'].append(f"{report.week}: 工作量充实")
            elif report.work_volume_score <= 30:
                performance['recent_concerns'].append(f"{report.week}: 工作量偏少")
            
            if report.progress_quality_score >= 85:
                performance['recent_highlights'].append(f"{report.week}: 规划详细")
            elif report.progress_quality_score <= 40:
                performance['recent_concerns'].append(f"{report.week}: 规划不足")
        
        return performance
    
    def _generate_recommendations(self, reports: List[WeeklyReport]) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        if not reports:
            return ["暂无足够数据生成建议"]
        
        # 基于平均分数的建议
        avg_work = sum(r.work_volume_score for r in reports) / len(reports)
        avg_quality = sum(r.progress_quality_score for r in reports) / len(reports)
        avg_problems = sum(r.problem_handling_score for r in reports) / len(reports)
        
        # 工作量建议
        if avg_work < 50:
            recommendations.append("建议增加每周的工作量，可以考虑制定更具体的工作计划和目标")
        elif avg_work > 85:
            recommendations.append("工作量充足，继续保持，注意劳逸结合")
        
        # 进度质量建议
        if avg_quality < 60:
            recommendations.append("建议提高工作规划的质量，制定更详细的下周计划和时间安排")
            recommendations.append("可以尝试设定具体的、可衡量的目标")
        
        # 问题处理建议
        if avg_problems < 60:
            recommendations.append("遇到问题时，建议更详细地分析问题原因并制定解决方案")
            recommendations.append("不要犹豫寻求导师和同学的帮助")
        
        # 基于工作模式的建议
        work_patterns = self._analyze_work_patterns(reports)
        if work_patterns['work_distribution']['literature_reading'] < 2:
            recommendations.append("建议增加文献阅读，保持对前沿研究的了解")
        
        if work_patterns['low_activity_weeks'] > len(reports) * 0.3:
            recommendations.append("注意保持工作连续性，避免长时间的低活跃期")
        
        # 基于一致性的建议
        consistency = self._analyze_consistency(reports)
        if not consistency.get('insufficient_data'):
            for score_type, data in consistency.items():
                if data['coefficient_of_variation'] > 0.4:  # 变异系数较大
                    recommendations.append(f"建议提高{score_type}的稳定性，保持持续的工作状态")
        
        # 基于趋势的建议
        recent_performance = self._analyze_recent_performance(reports)
        if recent_performance['average_work_volume'] < 40:
            recommendations.append("最近几周工作量偏少，建议调整状态，增加投入")
        
        if len(recent_performance['recent_concerns']) > 1:
            recommendations.append("最近表现需要关注，建议与导师沟通，调整研究方向或方法")
        
        return recommendations if recommendations else ["目前表现良好，请继续保持"]
    
    def generate_comprehensive_report(self) -> str:
        """生成综合分析报告"""
        report_lines = []
        report_lines.append("# 学生周报进度分析综合报告")
        report_lines.append(f"\n**分析时间:** {datetime.now().strftime('%Y年%m月%d日')}")
        report_lines.append(f"**数据范围:** 共分析 {len(self.reports)} 份周报，涵盖 {len(self.student_reports)} 名学生\n")
        
        # 整体统计
        report_lines.append("## 整体统计")
        
        all_work_scores = [r.work_volume_score for r in self.reports]
        all_quality_scores = [r.progress_quality_score for r in self.reports]
        all_problem_scores = [r.problem_handling_score for r in self.reports]
        
        report_lines.append(f"- **平均工作量评分:** {sum(all_work_scores)/len(all_work_scores):.1f}")
        report_lines.append(f"- **平均进度质量评分:** {sum(all_quality_scores)/len(all_quality_scores):.1f}")
        report_lines.append(f"- **平均问题处理评分:** {sum(all_problem_scores)/len(all_problem_scores):.1f}")
        
        # 学生排名
        report_lines.append("\n## 学生表现排名")
        
        student_avg_scores = []
        for student_name, reports in self.student_reports.items():
            if reports:
                avg_score = (
                    sum(r.work_volume_score for r in reports) +
                    sum(r.progress_quality_score for r in reports) +
                    sum(r.problem_handling_score for r in reports)
                ) / (3 * len(reports))
                student_avg_scores.append((student_name, avg_score, len(reports)))
        
        student_avg_scores.sort(key=lambda x: x[1], reverse=True)
        
        report_lines.append("| 排名 | 学生姓名 | 综合评分 | 报告数量 |")
        report_lines.append("|------|----------|----------|----------|")
        
        for i, (name, score, count) in enumerate(student_avg_scores, 1):
            report_lines.append(f"| {i} | {name} | {score:.1f} | {count} |")
        
        # 各学生详细分析
        report_lines.append("\n## 各学生详细分析")
        
        for student_name in sorted(self.student_reports.keys()):
            analysis = self.analyze_student_progress(student_name)
            if analysis:
                report_lines.append(f"\n### {student_name}")
                
                # 基本信息
                report_lines.append(f"**报告数量:** {analysis['total_reports']}")
                
                # 平均分数
                avg_scores = analysis['average_scores']
                report_lines.append(f"**平均分数:**")
                report_lines.append(f"- 工作量: {avg_scores['work_volume']:.1f}")
                report_lines.append(f"- 进度质量: {avg_scores['progress_quality']:.1f}")
                report_lines.append(f"- 问题处理: {avg_scores['problem_handling']:.1f}")
                
                # 工作模式
                work_patterns = analysis['work_patterns']
                if work_patterns['primary_work_types']:
                    report_lines.append(f"**主要工作类型:** {dict(work_patterns['primary_work_types'])}")
                
                report_lines.append(f"**工作活跃度:** 高产周数 {work_patterns['productivity_weeks']}，低活跃周数 {work_patterns['low_activity_weeks']}")
                
                # 问题模式
                problem_patterns = analysis['problem_patterns']
                if problem_patterns['weeks_with_problems'] > 0:
                    report_lines.append(f"**问题处理:** {problem_patterns['weeks_with_problems']}周有问题，{problem_patterns['weeks_with_solutions']}周有解决方案")
                    if problem_patterns['common_difficulties']:
                        report_lines.append(f"**常见困难:** {dict(problem_patterns['common_difficulties'])}")
                
                # 最近表现
                recent = analysis['recent_performance']
                report_lines.append(f"**{recent['period']}表现:**")
                report_lines.append(f"- 工作量: {recent['average_work_volume']:.1f}")
                report_lines.append(f"- 进度质量: {recent['average_progress_quality']:.1f}")
                report_lines.append(f"- 问题处理: {recent['average_problem_handling']:.1f}")
                
                if recent['recent_highlights']:
                    report_lines.append(f"**亮点:** {'; '.join(recent['recent_highlights'])}")
                
                if recent['recent_concerns']:
                    report_lines.append(f"**关注点:** {'; '.join(recent['recent_concerns'])}")
                
                # 建议
                recommendations = analysis['recommendations']
                report_lines.append("**指导建议:**")
                for rec in recommendations:
                    report_lines.append(f"- {rec}")
        
        # 总体建议
        report_lines.append("\n## 总体指导建议")
        
        # 找出需要特别关注的学生
        low_performers = [(name, score) for name, score, _ in student_avg_scores if score < 50]
        if low_performers:
            report_lines.append("### 需要特别关注的学生")
            for name, score in low_performers:
                report_lines.append(f"- **{name}** (综合评分: {score:.1f}) - 建议加强指导和支持")
        
        high_performers = [(name, score) for name, score, _ in student_avg_scores if score >= 80]
        if high_performers:
            report_lines.append("### 表现优秀的学生")
            for name, score in high_performers:
                report_lines.append(f"- **{name}** (综合评分: {score:.1f}) - 可作为榜样，继续保持")
        
        # 全局建议
        report_lines.append("\n### 全局改进建议")
        
        avg_work_volume = sum(all_work_scores) / len(all_work_scores)
        if avg_work_volume < 60:
            report_lines.append("- 整体工作量偏低，建议制定更明确的工作目标和时间规划")
        
        avg_quality = sum(all_quality_scores) / len(all_quality_scores)
        if avg_quality < 70:
            report_lines.append("- 建议统一规范周报格式，要求学生制定更详细的计划")
        
        # 统计有多少空报告
        empty_reports = sum(1 for r in self.reports if r.work_volume_score == 0)
        if empty_reports > 0:
            report_lines.append(f"- 发现 {empty_reports} 份空白或内容极少的报告，建议加强监督")
        
        report_lines.append("\n---")
        report_lines.append("*本报告由学生周报进度分析系统自动生成*")
        
        return '\n'.join(report_lines)
    
    def save_analysis_results(self, output_dir: str = None) -> None:
        """保存分析结果"""
        if output_dir is None:
            output_dir = self.repo_path / "analysis_results"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # 保存综合报告
        comprehensive_report = self.generate_comprehensive_report()
        with open(output_dir / "综合分析报告.md", 'w', encoding='utf-8') as f:
            f.write(comprehensive_report)
        
        # 保存各学生的详细分析
        for student_name in self.student_reports:
            analysis = self.analyze_student_progress(student_name)
            if analysis:
                with open(output_dir / f"{student_name}_详细分析.json", 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        # 保存原始数据
        all_data = []
        for report in self.reports:
            all_data.append(asdict(report))
        
        with open(output_dir / "所有周报数据.json", 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"分析结果已保存到: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='学生周报进度分析系统')
    parser.add_argument('--repo-path', default='.', help='周报仓库路径')
    parser.add_argument('--output-dir', help='分析结果输出目录')
    parser.add_argument('--student', help='分析特定学生（可选）')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = WeeklyReportAnalyzer(args.repo_path)
    
    # 扫描并解析所有报告
    analyzer.scan_reports()
    
    if args.student:
        # 分析特定学生
        analysis = analyzer.analyze_student_progress(args.student)
        if analysis:
            print(f"\n=== {args.student} 的进度分析 ===")
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
        else:
            print(f"未找到学生 {args.student} 的报告")
    else:
        # 生成综合报告
        print("正在生成分析报告...")
        report = analyzer.generate_comprehensive_report()
        print(report)
        
        # 保存结果
        analyzer.save_analysis_results(args.output_dir)


if __name__ == "__main__":
    main()