#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习教练 (Learning Coach)
基于元认知监控模型的学习辅助系统

核心功能：
1. 元认知监控循环
2. 断点续学
3. 多目标管理
4. 认知循环记录
5. 思维导图生成
6. 苏格拉底式追问（嵌入式）
"""

import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path
import uuid

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
PROFILES_FILE = DATA_DIR / "profiles.json"
RECORDS_FILE = DATA_DIR / "records.json"
MINDMAPS_DIR = Path(__file__).parent.parent / "mindmaps"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
MINDMAPS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== 苏格拉底追问配置 ====================

SOCRATIC_CONFIG = {
    "max_rounds": 3,  # 每个学习目标最多追问轮数
    "dimensions_order": ["clarify", "assumption", "evidence", "perspective", "consequence", "reflection"],
    "exit_options": {
        "explain": "直接解释",
        "continue": "继续追问"
    }
}

SOCRATIC_DIMENSIONS = {
    "clarify": {
        "name": "澄清",
        "question": "你具体指的是什么？",
        "prompts": [
            "能举个例子吗？",
            "哪个部分让你困惑？",
            "这个概念的核心是什么？",
            "用你自己的话说说看？"
        ]
    },
    "assumption": {
        "name": "假设",
        "question": "这个结论背后有哪些前提？",
        "prompts": [
            "你基于什么做出这个判断？",
            "有什么隐含的假设？",
            "这些前提成立吗？",
            "有没有前提被忽略了？"
        ]
    },
    "evidence": {
        "name": "证据",
        "question": "你依据的事实来自哪里？",
        "prompts": [
            "有数据支持吗？",
            "这个信息可靠吗？",
            "能找到反例吗？",
            "来源是什么？"
        ]
    },
    "perspective": {
        "name": "视角",
        "question": "还有谁可能持不同立场？",
        "prompts": [
            "从另一个角度看会怎样？",
            "反对意见是什么？",
            "为什么会有分歧？",
            "有没有其他解释？"
        ]
    },
    "consequence": {
        "name": "后果",
        "question": "如果这是真的会带来什么结果？",
        "prompts": [
            "接下来会发生什么？",
            "有什么影响？",
            "这会导致什么？",
            "短期和长期各有什么影响？"
        ]
    },
    "reflection": {
        "name": "反思",
        "question": "有什么被忽略或需要修正的地方？",
        "prompts": [
            "我们遗漏了什么？",
            "哪里可能有误解？",
            "需要重新思考什么？",
            "这个理解完整吗？"
        ]
    }
}


class SocraticQuestioner:
    """苏格拉底式追问引擎"""
    
    def __init__(self, config=None):
        self.config = config or SOCRATIC_CONFIG
        self.history = []  # 追问历史记录
        self.current_round = 0
        self.used_dimensions = set()
    
    def reset(self):
        """重置追问状态"""
        self.history = []
        self.current_round = 0
        self.used_dimensions = set()
    
    def get_next_dimension(self):
        """获取下一个追问维度"""
        available = [d for d in self.config["dimensions_order"] 
                     if d not in self.used_dimensions]
        if not available:
            # 所有维度都用过了，重置
            self.used_dimensions = set()
            available = self.config["dimensions_order"]
        return available[0] if available else None
    
    def generate_question(self, task_name, context=None):
        """
        生成苏格拉底式追问
        
        Args:
            task_name: 学习任务名称
            context: 上下文信息（上次回答等）
        
        Returns:
            dict: {
                "dimension": 维度名称,
                "main_question": 主问题,
                "prompt": 引导语,
                "round": 当前轮数,
                "options": 可选操作
            }
        """
        if self.current_round >= self.config["max_rounds"]:
            return None  # 达到上限
        
        dimension = self.get_next_dimension()
        if not dimension:
            return None
        
        dim_config = SOCRATIC_DIMENSIONS[dimension]
        prompt = random.choice(dim_config["prompts"])
        
        self.current_round += 1
        self.used_dimensions.add(dimension)
        
        question = {
            "dimension": dimension,
            "dimension_name": dim_config["name"],
            "main_question": dim_config["question"],
            "prompt": prompt,
            "round": self.current_round,
            "max_rounds": self.config["max_rounds"],
            "options": self.config["exit_options"],
            "task_name": task_name
        }
        
        self.history.append({
            "round": self.current_round,
            "dimension": dimension,
            "question": question
        })
        
        return question
    
    def process_answer(self, answer, auto_continue=True):
        """
        处理用户回答
        
        Args:
            answer: 用户回答（可以是文本或选项）
            auto_continue: 是否自动判断是否继续
        
        Returns:
            dict: {
                "action": "continue" | "explain" | "complete",
                "reason": 原因说明
            }
        """
        # 检查是否请求直接解释
        if isinstance(answer, str):
            if "直接解释" in answer or answer.lower() == "explain":
                return {"action": "explain", "reason": "用户选择直接解释"}
        
        # 记录回答
        if self.history:
            self.history[-1]["answer"] = answer
        
        # 检查是否达到上限
        if self.current_round >= self.config["max_rounds"]:
            return {"action": "explain", "reason": "已达到最大追问轮数"}
        
        # 判断回答质量（简单启发式）
        if isinstance(answer, str):
            # 短回答可能需要继续追问
            if len(answer) < 10:
                return {"action": "continue", "reason": "回答较短，继续深入"}
            # 包含疑问可能需要澄清
            if "?" in answer or "？" in answer:
                return {"action": "continue", "reason": "回答中包含疑问"}
        
        # 默认继续
        if auto_continue and self.current_round < self.config["max_rounds"]:
            return {"action": "continue", "reason": "继续深入探索"}
        
        return {"action": "complete", "reason": "评估完成"}
    
    def should_continue(self):
        """判断是否应该继续追问"""
        return self.current_round < self.config["max_rounds"]
    
    def get_summary(self):
        """获取追问总结"""
        return {
            "total_rounds": self.current_round,
            "dimensions_explored": list(self.used_dimensions),
            "history": self.history
        }
    
    def format_question(self, question):
        """格式化问题用于显示"""
        if not question:
            return ""
        
        lines = [
            f"🤔 【苏格拉底式追问 · 第{question['round']}/{question['max_rounds']}轮】",
            f"",
            f"📍 维度：{question['dimension_name']}",
            f"",
            f"❓ {question['main_question']}",
            f"",
            f"💭 提示：{question['prompt']}",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"[直接解释] 跳过追问，直接讲解",
            f"[继续追问] 继续深入探索",
            f"━━━━━━━━━━━━━━━━━━━━"
        ]
        return "\n".join(lines)


class LearningCoach:
    """学习教练主类"""
    
    def __init__(self):
        self.profiles = self._load_profiles()
        self.records = self._load_records()
        self.current_profile = None
        self.socratic_questioner = SocraticQuestioner()  # 苏格拉底追问引擎
        self.socratic_mode = False  # 当前是否处于苏格拉底模式
    
    # ==================== 数据管理 ====================
    
    def _load_profiles(self):
        """加载学习档案"""
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"profiles": []}
    
    def _save_profiles(self):
        """保存学习档案"""
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
    
    def _load_records(self):
        """加载认知循环日志"""
        if RECORDS_FILE.exists():
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"records": []}
    
    def _save_records(self):
        """保存认知循环日志"""
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    # ==================== 学习档案管理 ====================
    
    def create_profile(self, topic, level, goal, time_budget=None):
        """创建学习档案"""
        # 判断是否启用苏格拉底优先模式
        socratic_mode = "SOCRATIC_PRIORITY" if level == "零基础" else None
        
        profile = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "level": level,
            "goal": goal,
            "time_budget": time_budget,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "tasks": [],
            "current_task": None,
            "overall_progress": 0.0,
            "socratic_mode": socratic_mode,  # 苏格拉底模式标志
            "socratic_round_count": 0  # 当前追问轮数
        }
        
        self.profiles["profiles"].append(profile)
        self._save_profiles()
        
        self.current_profile = profile
        
        # 如果启用苏格拉底优先模式，重置追问引擎
        if socratic_mode == "SOCRATIC_PRIORITY":
            self.socratic_questioner.reset()
            self.socratic_mode = True
        
        return profile
    
    def get_profile(self, topic=None):
        """获取学习档案"""
        if topic:
            for p in self.profiles["profiles"]:
                if p["topic"] == topic:
                    return p
            return None
        elif self.current_profile:
            return self.current_profile
        elif self.profiles["profiles"]:
            # 返回最近更新的档案
            return sorted(
                self.profiles["profiles"],
                key=lambda x: x["updated_at"],
                reverse=True
            )[0]
        return None
    
    def list_profiles(self):
        """列出所有学习档案"""
        return self.profiles["profiles"]
    
    def switch_profile(self, topic):
        """切换学习目标"""
        profile = self.get_profile(topic)
        if profile:
            self.current_profile = profile
            # 根据档案的苏格拉底模式设置状态
            if profile.get("socratic_mode") == "SOCRATIC_PRIORITY":
                self.socratic_mode = True
                self.socratic_questioner.reset()
            else:
                self.socratic_mode = False
            return profile
        return None
    
    def toggle_socratic_mode(self, enable=True):
        """切换苏格拉底模式"""
        self.socratic_mode = enable
        if enable:
            self.socratic_questioner.reset()
        if self.current_profile:
            self.current_profile["socratic_mode"] = "SOCRATIC_PRIORITY" if enable else None
            self._save_profiles()
        return self.socratic_mode
    
    def update_profile(self, profile_id, updates):
        """更新学习档案"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                p.update(updates)
                p["updated_at"] = datetime.now().isoformat()
                self._save_profiles()
                return p
        return None
    
    # ==================== 任务管理 ====================
    
    def add_task(self, profile_id, task_name, importance=3):
        """添加学习任务"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                task = {
                    "name": task_name,
                    "mastery": 0.0,
                    "time_spent": "0h",
                    "status": "not_started",
                    "importance": importance,
                    "last_study": None
                }
                p["tasks"].append(task)
                p["updated_at"] = datetime.now().isoformat()
                self._save_profiles()
                return task
        return None
    
    def update_task(self, profile_id, task_name, mastery, time_spent=None):
        """更新任务进度"""
        for p in self.profiles["profiles"]:
            if p["id"] == profile_id:
                for t in p["tasks"]:
                    if t["name"] == task_name:
                        t["mastery"] = mastery
                        t["status"] = "in_progress" if mastery < 0.8 else "completed"
                        if time_spent:
                            t["time_spent"] = time_spent
                        t["last_study"] = datetime.now().isoformat()
                        
                        # 更新整体进度
                        if p["tasks"]:
                            p["overall_progress"] = sum(t["mastery"] for t in p["tasks"]) / len(p["tasks"])
                        
                        p["updated_at"] = datetime.now().isoformat()
                        self._save_profiles()
                        return t
        return None
    
    def select_task(self, profile):
        """选择最重要的任务"""
        if not profile or not profile.get("tasks"):
            return None
        
        # 过滤未完成的任务
        incomplete = [t for t in profile["tasks"] if t["mastery"] < 0.8]
        
        if not incomplete:
            return None
        
        # 按重要性和掌握度排序
        incomplete.sort(key=lambda t: (
            -t.get("importance", 3),
            t["mastery"]
        ))
        
        return incomplete[0]
    
    # ==================== 认知循环 ====================
    
    def create_record(self, profile_id, task, assessment, decision, time_spent):
        """创建认知循环记录"""
        record = {
            "id": str(uuid.uuid4()),
            "profile_id": profile_id,
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "assessment": assessment,
            "decision": decision,
            "time_spent": time_spent
        }
        
        self.records["records"].append(record)
        self._save_records()
        
        return record
    
    def get_records(self, profile_id=None, task_name=None):
        """获取认知循环记录"""
        records = self.records["records"]
        
        if profile_id:
            records = [r for r in records if r["profile_id"] == profile_id]
        
        if task_name:
            records = [r for r in records if r["task"]["name"] == task_name]
        
        return records
    
    # ==================== 评估与策略 ====================
    
    def calculate_mastery(self, answers):
        """
        计算掌握度
        answers: {"surface": 0-1, "semantic": 0-1, "intuitive": 0-1}
        """
        mastery = {
            "surface": answers.get("surface", 0),
            "semantic": answers.get("semantic", 0),
            "intuitive": answers.get("intuitive", 0)
        }
        
        overall = (
            mastery["surface"] * 0.2 +
            mastery["semantic"] * 0.3 +
            mastery["intuitive"] * 0.5
        )
        
        return {"overall": overall, "breakdown": mastery}
    
    def recommend_strategy(self, mastery_level):
        """推荐学习策略"""
        if mastery_level < 0.3:
            return [
                "观看入门视频教程",
                "阅读基础概念文章",
                "寻找前置知识补充"
            ]
        elif mastery_level < 0.6:
            return [
                "阅读进阶文章",
                "完成练习题",
                "动手实践"
            ]
        else:
            return [
                "完成项目实践",
                "尝试教给他人",
                "应用到新场景"
            ]
    
    # ==================== 苏格拉底式评估 ====================
    
    def start_socratic_assessment(self, task_name):
        """
        开始苏格拉底式评估
        
        Args:
            task_name: 要评估的学习任务名称
        
        Returns:
            dict: 第一个追问问题
        """
        if not self.current_profile:
            return None
        
        # 重置追问引擎
        self.socratic_questioner.reset()
        self.socratic_mode = True
        
        # 更新档案中的追问计数
        self.current_profile["socratic_round_count"] = 0
        self._save_profiles()
        
        # 生成第一个问题
        question = self.socratic_questioner.generate_question(task_name)
        
        return question
    
    def continue_socratic_assessment(self, answer):
        """
        继续苏格拉底式评估
        
        Args:
            answer: 用户回答
        
        Returns:
            dict: {
                "action": "continue" | "explain" | "complete",
                "question": 下一问题（如果继续）,
                "summary": 总结（如果结束）,
                "reason": 原因说明
            }
        """
        result = self.socratic_questioner.process_answer(answer)
        
        # 更新追问计数
        if self.current_profile:
            self.current_profile["socratic_round_count"] = self.socratic_questioner.current_round
            self._save_profiles()
        
        if result["action"] == "continue":
            # 生成下一个问题
            task_name = self.current_profile.get("current_task") if self.current_profile else "当前任务"
            next_question = self.socratic_questioner.generate_question(task_name)
            if next_question:
                return {
                    "action": "continue",
                    "question": next_question,
                    "reason": result["reason"]
                }
            else:
                # 无法生成更多问题，转为解释
                return {
                    "action": "explain",
                    "summary": self.socratic_questioner.get_summary(),
                    "reason": "追问完成"
                }
        
        elif result["action"] == "explain":
            # 用户请求直接解释或达到上限
            self.socratic_mode = False
            return {
                "action": "explain",
                "summary": self.socratic_questioner.get_summary(),
                "reason": result["reason"]
            }
        else:
            return {
                "action": "complete",
                "summary": self.socratic_questioner.get_summary(),
                "reason": result["reason"]
            }
    
    def socratic_mastery_from_history(self):
        """
        基于苏格拉底追问历史计算掌握度
        
        分析用户回答的深度和完整性，评估理解程度
        """
        summary = self.socratic_questioner.get_summary()
        history = summary.get("history", [])
        
        if not history:
            return {"overall": 0.0, "breakdown": {"surface": 0, "semantic": 0, "intuitive": 0}}
        
        # 基于回答数量和维度覆盖计算掌握度
        dimensions_explored = len(summary.get("dimensions_explored", []))
        rounds = summary.get("total_rounds", 0)
        
        # 简化评估逻辑（可后续扩展）
        # 维度覆盖越多，理解越全面
        coverage_score = min(dimensions_explored / 6, 1.0) * 0.4
        
        # 回答深度（基于回答字数和是否包含疑问）
        depth_score = 0.3  # 默认中等深度
        for h in history:
            answer = h.get("answer", "")
            if isinstance(answer, str):
                if len(answer) > 50:
                    depth_score += 0.1
                if "?" not in answer and "？" not in answer:
                    depth_score += 0.05
        depth_score = min(depth_score, 0.6)
        
        # 完整性（基于是否主动请求直接解释）
        completeness = 0.3 if rounds < 3 else 0.2  # 早退出表示有一定自信
        
        overall = coverage_score * 0.3 + depth_score * 0.5 + completeness * 0.2
        
        return {
            "overall": overall,
            "breakdown": {
                "surface": coverage_score,
                "semantic": depth_score,
                "intuitive": completeness
            }
        }
    
    # ==================== 思维导图生成 ====================
    
    def generate_mindmap(self, profile):
        """生成思维导图（Mermaid格式）"""
        if not profile or not profile.get("tasks"):
            return None
        
        topic = profile["topic"]
        tasks = profile["tasks"]
        
        # 生成 Mermaid 代码
        lines = [f"mindmap", f"  root(({topic}))"]
        
        for task in tasks:
            mastery = task["mastery"]
            mastery_pct = int(mastery * 100)
            status = "✅" if mastery >= 0.8 else "⏳" if mastery > 0 else "⭕"
            lines.append(f"    {task['name']} {status} {mastery_pct}%")
        
        mindmap = "\n".join(lines)
        
        # 保存到文件
        filename = f"{topic}_mindmap_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = MINDMAPS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {topic} 学习思维导图\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("```mermaid\n")
            f.write(mindmap)
            f.write("\n```\n")
        
        return {"mindmap": mindmap, "file": str(filepath)}
    
    # ==================== 学习报告 ====================
    
    def generate_report(self, profile):
        """生成学习报告"""
        if not profile:
            return None
        
        records = self.get_records(profile["id"])
        
        report = {
            "topic": profile["topic"],
            "level": profile["level"],
            "goal": profile["goal"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
            "overall_progress": profile["overall_progress"],
            "tasks": profile["tasks"],
            "current_task": profile["current_task"],
            "total_records": len(records),
            "total_time": self._calculate_total_time(records)
        }
        
        return report
    
    def _calculate_total_time(self, records):
        """计算总学习时间"""
        total_minutes = 0
        for r in records:
            time_str = r.get("time_spent", "0h")
            # 简单解析（支持 "30min", "1h", "1h30min" 等格式）
            if "h" in time_str:
                parts = time_str.split("h")
                total_minutes += int(parts[0]) * 60
                if len(parts) > 1 and "min" in parts[1]:
                    total_minutes += int(parts[1].replace("min", ""))
            elif "min" in time_str:
                total_minutes += int(time_str.replace("min", ""))
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours}h{minutes}min" if minutes > 0 else f"{hours}h"
    
    # ==================== 导出功能 ====================
    
    def export_data(self):
        """导出所有数据"""
        return {
            "profiles": self.profiles,
            "records": self.records,
            "exported_at": datetime.now().isoformat()
        }


# ==================== 命令行接口 ====================

def print_help():
    """打印帮助信息"""
    help_text = """
学习教练 (Learning Coach) - 基于元认知监控模型的学习辅助系统

可用命令：
  start <主题>           开始学习新主题
  continue [主题]        继续学习（可指定主题）
  list                   列出所有学习目标
  switch <主题>          切换学习目标
  status [主题]          查看学习进度
  report [主题]          生成学习报告
  mindmap [主题]         生成思维导图
  socratic <任务>        开始苏格拉底式评估
  answer <回答>          回答苏格拉底追问
  explain                请求直接解释（退出追问模式）
  export                 导出所有数据
  help                   显示帮助信息

苏格拉底模式说明：
  - 零基础用户自动启用苏格拉底优先模式
  - 使用6维度追问框架引导深度思考
  - 最多3轮追问，可随时输入"直接解释"退出
  - 维度：澄清→假设→证据→视角→后果→反思

示例：
  python coach.py start 机器学习 --level 零基础
  python coach.py socratic 监督学习
  python coach.py continue
  python coach.py status
"""
    print(help_text)


def interactive_mode():
    """交互模式"""
    coach = LearningCoach()
    
    print("=" * 60)
    print("🧠 学习教练 (Learning Coach)")
    print("=" * 60)
    print()
    
    while True:
        try:
            cmd = input("教练> ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None
            
            if action in ["exit", "quit", "q"]:
                print("再见！继续加油学习！")
                break
            
            elif action == "help":
                print_help()
            
            elif action == "start":
                if not args:
                    print("请指定学习主题，例如：start 机器学习")
                    continue
                # 解析可选参数
                parts = args.split()
                topic = parts[0]
                level = "未设置"
                goal = "未设置"
                
                # 检查是否有 --level 参数
                for i, p in enumerate(parts):
                    if p == "--level" and i + 1 < len(parts):
                        level = parts[i + 1]
                    elif p == "--goal" and i + 1 < len(parts):
                        goal = parts[i + 1]
                
                profile = coach.create_profile(topic, level, goal)
                print(f"✅ 已创建学习档案：{topic}")
                print(f"档案ID：{profile['id']}")
                if profile.get('socratic_mode') == "SOCRATIC_PRIORITY":
                    print("🎯 已自动启用苏格拉底优先模式（零基础）")
            
            elif action == "continue":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案，请先用 start 命令创建")
                    continue
                print(f"继续学习：{profile['topic']}")
                print(f"当前进度：{profile['overall_progress']*100:.1f}%")
            
            elif action == "list":
                profiles = coach.list_profiles()
                if not profiles:
                    print("暂无学习档案")
                    continue
                print("📚 学习目标列表：")
                for i, p in enumerate(profiles, 1):
                    progress = p['overall_progress'] * 100
                    print(f"{i}. {p['topic']} - 进度：{progress:.1f}%")
            
            elif action == "status":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                report = coach.generate_report(profile)
                print(f"📊 学习进度报告：{report['topic']}")
                print(f"整体进度：{report['overall_progress']*100:.1f}%")
                print(f"总学习时间：{report['total_time']}")
                if report['tasks']:
                    print("任务列表：")
                    for t in report['tasks']:
                        status = "✅" if t['mastery'] >= 0.8 else "⏳"
                        print(f"  {status} {t['name']} - {t['mastery']*100:.0f}%")
            
            elif action == "report":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                report = coach.generate_report(profile)
                print(json.dumps(report, ensure_ascii=False, indent=2))
            
            elif action == "mindmap":
                profile = coach.get_profile(args)
                if not profile:
                    print("未找到学习档案")
                    continue
                result = coach.generate_mindmap(profile)
                if result:
                    print(f"✅ 思维导图已生成")
                    print(f"文件：{result['file']}")
                    print()
                    print(result['mindmap'])
            
            elif action == "export":
                data = coach.export_data()
                print(json.dumps(data, ensure_ascii=False, indent=2))
            
            elif action == "socratic":
                if not args:
                    print("请指定要评估的任务，例如：socratic 监督学习")
                    continue
                if not coach.current_profile:
                    print("请先选择一个学习档案，使用 start 或 switch 命令")
                    continue
                question = coach.start_socratic_assessment(args)
                if question:
                    print(coach.socratic_questioner.format_question(question))
                else:
                    print("无法生成苏格拉底追问")
            
            elif action == "answer":
                if not args:
                    print("请提供你的回答")
                    continue
                if not coach.socratic_mode:
                    print("当前不在苏格拉底模式，请先使用 socratic 命令开始评估")
                    continue
                result = coach.continue_socratic_assessment(args)
                if result["action"] == "continue":
                    print(f"\n💡 {result['reason']}")
                    print(coach.socratic_questioner.format_question(result["question"]))
                elif result["action"] == "explain":
                    print(f"\n📚 {result['reason']}")
                    summary = result.get("summary", {})
                    print(f"已探索维度：{', '.join(summary.get('dimensions_explored', []))}")
                    print(f"追问轮数：{summary.get('total_rounds', 0)}")
                    print("\n正在生成直接解释...")
                    # 计算基于追问历史的掌握度
                    mastery = coach.socratic_mastery_from_history()
                    print(f"\n📊 估计掌握度：{mastery['overall']*100:.0f}%")
                else:
                    print(f"\n✅ {result['reason']}")
                    summary = result.get("summary", {})
                    print(f"评估完成！")
            
            elif action == "explain":
                if not coach.socratic_mode:
                    print("当前不在苏格拉底模式")
                    continue
                # 用户请求直接解释
                result = coach.continue_socratic_assessment("直接解释")
                print(f"\n📚 {result['reason']}")
                summary = result.get("summary", {})
                print(f"已探索维度：{', '.join(summary.get('dimensions_explored', []))}")
                mastery = coach.socratic_mastery_from_history()
                print(f"\n📊 估计掌握度：{mastery['overall']*100:.0f}%")
                print("\n正在生成直接解释...")
            
            else:
                print(f"未知命令：{action}")
                print("输入 'help' 查看可用命令")
        
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误：{e}")


def main():
    """主函数"""
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    coach = LearningCoach()
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "help"
    # 合并所有后续参数（支持多参数）
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    if action == "help":
        print_help()
    
    elif action == "start":
        if not args:
            print("用法：python coach.py start <主题>")
            print("可选参数：--level <基础等级> --goal <学习目标>")
            return
        # 解析参数
        parts = args.split()
        topic = parts[0]
        level = "未设置"
        goal = "未设置"
        
        for i, p in enumerate(parts):
            if p == "--level" and i + 1 < len(parts):
                level = parts[i + 1]
            elif p == "--goal" and i + 1 < len(parts):
                goal = parts[i + 1]
        
        profile = coach.create_profile(topic, level, goal)
        print(f"✅ 已创建学习档案：{args}")
        if profile.get('socratic_mode') == "SOCRATIC_PRIORITY":
            print("🎯 已自动启用苏格拉底优先模式（零基础）")
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    
    elif action == "list":
        profiles = coach.list_profiles()
        print(json.dumps(profiles, ensure_ascii=False, indent=2))
    
    elif action == "status":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        report = coach.generate_report(profile)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif action == "report":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        report = coach.generate_report(profile)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif action == "mindmap":
        profile = coach.get_profile(args)
        if not profile:
            print("未找到学习档案")
            return
        result = coach.generate_mindmap(profile)
        if result:
            print(f"✅ 思维导图已生成：{result['file']}")
            print()
            print(result['mindmap'])
    
    elif action == "export":
        data = coach.export_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    elif action == "socratic":
        if not args:
            print("用法：python coach.py socratic <任务名称>")
            return
        profile = coach.get_profile()
        if not profile:
            print("请先创建学习档案")
            return
        coach.current_profile = profile
        question = coach.start_socratic_assessment(args)
        if question:
            print(coach.socratic_questioner.format_question(question))
        else:
            print("无法生成苏格拉底追问")
    
    elif action == "answer":
        if not args:
            print("用法：python coach.py answer <你的回答>")
            return
        result = coach.continue_socratic_assessment(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "explain":
        result = coach.continue_socratic_assessment("直接解释")
        mastery = coach.socratic_mastery_from_history()
        print(json.dumps({
            "result": result,
            "mastery": mastery
        }, ensure_ascii=False, indent=2))
    
    elif action == "toggle-socratic":
        enable = args.lower() == "on" if args else True
        mode = coach.toggle_socratic_mode(enable)
        print(f"苏格拉底模式：{'开启' if mode else '关闭'}")
    
    else:
        print(f"未知命令：{action}")
        print_help()


if __name__ == "__main__":
    main()