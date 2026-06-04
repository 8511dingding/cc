"""
舆情分析系统 - 数据模型
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sentiment.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

# ============== 用户与认证 ==============

class User(Base):
    """用户"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    email = Column(String(100))
    role = Column(String(20), default='user')  # admin/user/viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# ============== 项目与数据 ==============

class Project(Base):
    """项目"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    source_project_id = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    source_file = Column(String(500))
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)

    s1_denominator = Column(Integer, default=0)
    s2_denominator = Column(Integer, default=0)

    clean_rules_config = Column(JSON, default=dict)
    status = Column(String(20), default='active')  # active/archived

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_project_id': self.source_project_id,
            'created_by': self.created_by,
            'total_rows': self.total_rows,
            'valid_rows': self.valid_rows,
            's1_denominator': self.s1_denominator,
            's2_denominator': self.s2_denominator,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RawData(Base):
    """原始数据"""
    __tablename__ = 'raw_data'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    row_index = Column(Integer)

    video_id = Column(String(100))
    video_link = Column(String(500))
    keyword = Column(String(200))
    content = Column(Text)
    topic_tags = Column(String(500))
    publish_time = Column(String(100))
    blogger = Column(String(200))
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comment_id = Column(String(100))
    comment_time = Column(String(100))
    ip_location = Column(String(100))
    comment_content = Column(Text)
    nickname = Column(String(200))
    reply_count = Column(Integer, default=0)
    reply_likes = Column(Integer, default=0)
    content_type = Column(String(50))
    brand_mentions = Column(Text)

    # 清洗标记
    is_pure_at = Column(Boolean, default=False)
    is_pure_emoji = Column(Boolean, default=False)
    is_filler_word = Column(Boolean, default=False)
    is_empty = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    is_garbled = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)

    # 标签
    cognitive_s1 = Column(String(50))
    cognitive_s2 = Column(String(50))
    emotional_s1 = Column(String(50))
    emotional_s2 = Column(String(50))
    action_s1 = Column(String(50))
    action_s2 = Column(String(50))

    # 品牌竞品识别
    brand_detected = Column(String(200))  # 检测到的品牌
    competitor_detected = Column(String(200))  # 检测到的竞品
    product_detected = Column(String(200))  # 检测到的产品

    manual_override = Column(Boolean, default=False)
    labeled_by = Column(Integer, nullable=True)
    labeled_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'row_index': self.row_index,
            'video_id': self.video_id,
            'video_link': self.video_link,
            'keyword': self.keyword,
            'content': self.content,
            'topic_tags': self.topic_tags,
            'publish_time': self.publish_time,
            'blogger': self.blogger,
            'likes': self.likes,
            'comments_count': self.comments_count,
            'favorites': self.favorites,
            'shares': self.shares,
            'comment_id': self.comment_id,
            'comment_content': self.comment_content,
            'comment_time': self.comment_time,
            'content_type': self.content_type,
            'brand_mentions': self.brand_mentions,
            'ip_location': self.ip_location,
            'nickname': self.nickname,
            'reply_count': self.reply_count,
            'reply_likes': self.reply_likes,
            'is_pure_at': self.is_pure_at,
            'is_pure_emoji': self.is_pure_emoji,
            'is_filler_word': self.is_filler_word,
            'is_empty': self.is_empty,
            'is_duplicate': self.is_duplicate,
            'is_garbled': self.is_garbled,
            'is_valid': self.is_valid,
            'cognitive_s1': self.cognitive_s1,
            'cognitive_s2': self.cognitive_s2,
            'emotional_s1': self.emotional_s1,
            'emotional_s2': self.emotional_s2,
            'action_s1': self.action_s1,
            'action_s2': self.action_s2,
            'brand_detected': self.brand_detected,
            'competitor_detected': self.competitor_detected,
            'product_detected': self.product_detected,
            'manual_override': self.manual_override
        }

class DataSubset(Base):
    """数据子集"""
    __tablename__ = 'data_subsets'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    filter_config = Column(JSON, default=dict)
    data_ids = Column(Text)
    record_count = Column(Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'filter_config': self.filter_config or {},
            'data_ids': json.loads(self.data_ids) if self.data_ids else [],
            'record_count': self.record_count
        }

# ============== 品牌与竞品管理 ==============

class Brand(Base):
    """品牌"""
    __tablename__ = 'brands'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    alias = Column(String(200))  # 别名，如 a2=爱他美
    category = Column(String(50))  # 奶粉/辅食/营养品等
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # 优先级
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'alias': self.alias,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
            'priority': self.priority
        }

class CompetitorProduct(Base):
    """竞品"""
    __tablename__ = 'competitor_products'

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    product_line = Column(String(100))  # 产品系列
    keywords = Column(JSON, default=list)  # 识别关键词
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'name': self.name,
            'product_line': self.product_line,
            'keywords': self.keywords or [],
            'description': self.description,
            'is_active': self.is_active
        }

# ============== 规则配置 ==============

class LabelRule(Base):
    """标签规则"""
    __tablename__ = 'label_rules'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=True)  # nullable表示全局规则
    layer = Column(String(20))  # cognitive/emotional/action/brand
    stage = Column(String(10))  # s1/s2
    label = Column(String(50))
    keywords = Column(JSON, default=list)
    priority = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'layer': self.layer,
            'stage': self.stage,
            'label': self.label,
            'keywords': self.keywords or [],
            'priority': self.priority,
            'enabled': self.enabled
        }

class CleanRule(Base):
    """清洗规则"""
    __tablename__ = 'clean_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'enabled': self.enabled,
            'priority': self.priority
        }

# ============== 报告模板 ==============

class ReportTemplate(Base):
    """报告模板"""
    __tablename__ = 'report_templates'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), default='1.0')
    description = Column(Text)
    sections = Column(JSON, default=list)  # 模板配置
    content_template = Column(Text)  # Word模板文件路径
    filename_template = Column(String(300))  # 文件名模板
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_default = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'sections': self.sections or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_default': self.is_default
        }

# ============== 导出记录 ==============

class ExportRecord(Base):
    """导出记录"""
    __tablename__ = 'export_records'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    template_id = Column(Integer, nullable=True)
    template_name = Column(String(200))
    export_type = Column(String(20))  # word/pdf/excel
    filename = Column(String(300))
    file_path = Column(String(500))
    file_size = Column(Integer)
    exported_by = Column(Integer)
    exported_at = Column(DateTime, default=datetime.now)

    # 导出配置
    included_sections = Column(JSON, default=list)
    filename_template = Column(String(300))  # 文件名模板

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'template_name': self.template_name,
            'export_type': self.export_type,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'exported_at': self.exported_at.isoformat() if self.exported_at else None
        }

import json

def init_db():
    Base.metadata.create_all(engine)
    session = Session()

    # 初始化清洗规则
    if session.query(CleanRule).count() == 0:
        default_clean_rules = [
            {"name": "纯@无互动", "code": "pure_at", "description": "仅包含@提及，无有效文字内容", "priority": 10},
            {"name": "纯表情/emoji", "code": "pure_emoji", "description": "仅包含表情符号，无文字内容", "priority": 9},
            {"name": "无意义语气词", "code": "filler_word", "description": "啊啊啊、哈哈、嗯嗯、666等无意义语气词", "priority": 8},
            {"name": "空内容", "code": "empty", "description": "内容为空或仅包含空白字符", "priority": 7},
            {"name": "乱码/异常字符", "code": "garbled", "description": "包含乱码或异常字符的内容", "priority": 6},
            {"name": "重复内容", "code": "duplicate", "description": "与之前内容完全相同的重复评论", "priority": 5},
        ]
        for rule in default_clean_rules:
            cr = CleanRule(name=rule['name'], code=rule['code'], description=rule['description'], priority=rule['priority'], enabled=True)
            session.add(cr)

    # 初始化默认报告模板
    if session.query(ReportTemplate).count() == 0:
        default_template = ReportTemplate(
            name="舆情分析报告模板",
            version="1.0",
            description="默认舆情分析报告模板",
            sections=[
                {"id": "overview", "name": "报告概述", "enabled": True, "order": 1},
                {"id": "content_type", "name": "评论内容类型分布", "enabled": True, "order": 2},
                {"id": "cognitive", "name": "认知分析（Understanding）", "enabled": True, "order": 3},
                {"id": "emotional", "name": "情绪分析（Emotional）", "enabled": True, "order": 4},
                {"id": "action", "name": "行为分析（Action）", "enabled": True, "order": 5},
                {"id": "brand", "name": "品牌竞品提及分析", "enabled": True, "order": 6},
                {"id": "summary", "name": "总结与建议", "enabled": True, "order": 7},
            ],
            filename_template="{project_name}_{date}_{version}",
            is_default=True
        )
        session.add(default_template)

    # 初始化默认品牌（示例）
    if session.query(Brand).count() == 0:
        default_brands = [
            {"name": "a2", "alias": "a2至初|a2紫白金|a2紫曜", "category": "奶粉", "priority": 10},
            {"name": "爱他美", "alias": "爱他美|Aptamil", "category": "奶粉", "priority": 8},
            {"name": "飞鹤", "alias": "飞鹤|飞鹤奶粉", "category": "奶粉", "priority": 7},
            {"name": "金领冠", "alias": "金领冠|伊利金领冠", "category": "奶粉", "priority": 7},
            {"name": "贝拉米", "alias": "贝拉米|Bellamy's", "category": "奶粉", "priority": 6},
            {"name": "美赞臣", "alias": "美赞臣|Enfamil", "category": "奶粉", "priority": 6},
            {"name": "惠氏", "alias": "惠氏|启赋|Wyeth", "category": "奶粉", "priority": 5},
            {"name": "皇家美素力", "alias": "皇家美素力|Friso", "category": "奶粉", "priority": 5},
        ]
        for b in default_brands:
            brand = Brand(name=b['name'], alias=b['alias'], category=b['category'], priority=b['priority'])
            session.add(brand)

    # 初始化标签规则
    if session.query(LabelRule).count() == 0:
        # 情绪层规则 (5分类)
        emotional_rules = [
            # 正面
            {"layer": "emotional", "stage": "s1", "label": "正面", "keywords": ["放心", "没有问题", "可以继续喝", "官方确认安全", "没影响", "未受影响", "没事", "娃从出生就喝", "一直喝", "长高", "长肉", "体重", "健康", "囤奶", "正常喝", "货源稳定", "有货", "补货"], "priority": 4},
            {"layer": "emotional", "stage": "s2", "label": "正面", "keywords": ["放心", "没有问题", "可以继续喝", "官方确认安全", "没影响", "未受影响", "没事", "娃从出生就喝", "一直喝", "长高", "长肉", "体重", "健康", "囤奶", "正常喝", "货源稳定", "有货", "补货"], "priority": 4},
            # 中性
            {"layer": "emotional", "stage": "s1", "label": "中性", "keywords": [], "priority": 2},
            {"layer": "emotional", "stage": "s2", "label": "中性", "keywords": [], "priority": 2},
            # 恐慌焦虑
            {"layer": "emotional", "stage": "s1", "label": "恐慌焦虑", "keywords": ["会不会有事", "有影响吗", "有危害吗", "怎么办", "瑟瑟发抖", "慌", "害怕", "担心", "担忧", "焦虑", "着急", "天哪", "急死人", "揪心", "好担心", "还能喝不", "要不要换", "能不能喝", "咋整", "选什么奶粉", "天塌了", "求推荐", "是不是我娃", "我娃吃了", "宝宝吃了", "潜伏期", "安全吗", "没事吧", "吐奶", "拉肚子", "便血"], "priority": 3},
            {"layer": "emotional", "stage": "s2", "label": "恐慌焦虑", "keywords": ["会不会有事", "有影响吗", "有危害吗", "怎么办", "瑟瑟发抖", "慌", "害怕", "担心", "担忧", "焦虑", "着急", "天哪", "急死人", "揪心", "好担心", "还能喝不", "要不要换", "能不能喝", "咋整", "选什么奶粉", "天塌了", "求推荐", "是不是我娃", "我娃吃了", "宝宝吃了", "潜伏期", "安全吗", "没事吧", "吐奶", "拉肚子", "便血"], "priority": 3},
            # 庆幸旁观
            {"layer": "emotional", "stage": "s1", "label": "庆幸旁观", "keywords": ["还好没买", "幸好没买", "多亏没买", "还好不是", "还好", "好在", "好险", "国产更好", "喝母乳", "不喝外国奶", "幸好没选", "两个娃都喝", "暗自观察", "又出事啦", "希望守住", "洋货", "崇洋", "早就换了", "暗自庆幸", "我机智", "我选对了", "凑热闹", "哭晕", "得亏"], "priority": 3},
            {"layer": "emotional", "stage": "s2", "label": "庆幸旁观", "keywords": ["还好没买", "幸好没买", "多亏没买", "还好不是", "还好", "好在", "好险", "国产更好", "喝母乳", "不喝外国奶", "幸好没选", "两个娃都喝", "暗自观察", "又出事啦", "希望守住", "洋货", "崇洋", "早就换了", "暗自庆幸", "我机智", "我选对了", "凑热闹", "哭晕", "得亏"], "priority": 3},
            # 愤怒背叛
            {"layer": "emotional", "stage": "s1", "label": "愤怒背叛", "keywords": ["该死", "欺骗", "忽悠", "被骗", "上当", "造假", "破产", "恶意", "黑心", "无良", "骗子", "垃圾品牌", "气愤", "失望透顶", "谁还敢喝", "骗人是狗", "转黑", "极其厌恶", "三鹿", "代加工", "代工", "贴牌", "塌房", "步步惊心", "进口信不过", "膈应", "背刺", "资本家", "没人性", "双标", "不负责任", "建议严查", "企业无良", "败絮其中", "气笑了", "没招了", "发怒", "坑中国人", "人傻钱多"], "priority": 5},
            {"layer": "emotional", "stage": "s2", "label": "愤怒背叛", "keywords": ["该死", "欺骗", "忽悠", "被骗", "上当", "造假", "破产", "恶意", "黑心", "无良", "骗子", "垃圾品牌", "气愤", "失望透顶", "谁还敢喝", "骗人是狗", "转黑", "极其厌恶", "三鹿", "代加工", "代工", "贴牌", "塌房", "步步惊心", "进口信不过", "膈应", "背刺", "资本家", "没人性", "双标", "不负责任", "建议严查", "企业无良", "败絮其中", "气笑了", "没招了", "发怒", "坑中国人", "人傻钱多"], "priority": 5},
        ]
        # 认知层规则 (4分类)
        cognitive_rules = [
            {"layer": "cognitive", "stage": "s1", "label": "无明确认知", "keywords": [], "priority": 1},
            {"layer": "cognitive", "stage": "s2", "label": "无明确认知", "keywords": [], "priority": 1},
            {"layer": "cognitive", "stage": "s1", "label": "信息混淆", "keywords": ["国行", "澳洲版", "美版", "版本", "分不清", "搞混", "区别", "到底哪个", "哪个是正版", "a2至初", "至初", "国版", "美版"], "priority": 2},
            {"layer": "cognitive", "stage": "s2", "label": "信息混淆", "keywords": ["国行", "澳洲版", "美版", "版本", "分不清", "搞混", "区别", "到底哪个", "哪个是正版", "a2至初", "至初", "国版", "美版"], "priority": 2},
            {"layer": "cognitive", "stage": "s1", "label": "精准认知", "keywords": ["fda", "检出", "仅限美国", "特定批次", "国标", "配方安全", "海关总署", "检测合格", "召回范围", "官方声明", "美版问题", "区域配方", "单点质控", "美国标准差异"], "priority": 3},
            {"layer": "cognitive", "stage": "s2", "label": "精准认知", "keywords": ["fda", "检出", "仅限美国", "特定批次", "国标", "配方安全", "海关总署", "检测合格", "召回范围", "官方声明", "美版问题", "区域配方", "单点质控", "美国标准差异"], "priority": 3},
            {"layer": "cognitive", "stage": "s1", "label": "泛化抵触", "keywords": ["所有奶粉", "所有品牌", "都不行", "都有问题", "都不安全", "不如母乳", "干脆不喝", "还是母乳好", "所有", "全部", "一律", "阴谋论"], "priority": 4},
            {"layer": "cognitive", "stage": "s2", "label": "泛化抵触", "keywords": ["所有奶粉", "所有品牌", "都不行", "都有问题", "都不安全", "不如母乳", "干脆不喝", "还是母乳好", "所有", "全部", "一律", "阴谋论"], "priority": 4},
        ]
        # 行动层规则 (4分类)
        action_rules = [
            {"layer": "action", "stage": "s1", "label": "暂无行动", "keywords": [], "priority": 1},
            {"layer": "action", "stage": "s2", "label": "暂无行动", "keywords": [], "priority": 1},
            {"layer": "action", "stage": "s1", "label": "寻求帮助", "keywords": ["怎么办", "咋整", "怎么处理", "求推荐", "哪个好", "有没有问题", "是不是", "能不能", "能不能喝", "要不要换", "怎么选", "选哪个", "没事吧", "安全吗", "潜伏期", "哪个阶段"], "priority": 2},
            {"layer": "action", "stage": "s2", "label": "寻求帮助", "keywords": ["怎么办", "咋整", "怎么处理", "求推荐", "哪个好", "有没有问题", "是不是", "能不能", "能不能喝", "要不要换", "怎么选", "选哪个", "没事吧", "安全吗", "潜伏期", "哪个阶段"], "priority": 2},
            {"layer": "action", "stage": "s1", "label": "转奶流失", "keywords": ["换了", "转奶", "退了", "换回", "准备换", "已经换", "买了国产", "算买国产", "转皇家", "转爱他美", "转德爱", "换飞鹤", "换蓝臻", "换海普", "换1897", "换澳爱", "吃完就换", "只喝了一箱", "马上换", "退了2罐", "彻底下决心", "再也不会", "绝对不买", "不喝外国奶"], "priority": 3},
            {"layer": "action", "stage": "s2", "label": "转奶流失", "keywords": ["换了", "转奶", "退了", "换回", "准备换", "已经换", "买了国产", "算买国产", "转皇家", "转爱他美", "转德爱", "换飞鹤", "换蓝臻", "换海普", "换1897", "换澳爱", "吃完就换", "只喝了一箱", "马上换", "退了2罐", "彻底下决心", "再也不会", "绝对不买", "不喝外国奶"], "priority": 3},
            {"layer": "action", "stage": "s1", "label": "维权诉求", "keywords": ["12315", "投诉", "索赔", "退换", "退款", "赔偿", "退货", "维权", "投诉后退款", "贝壳碎片"], "priority": 4},
            {"layer": "action", "stage": "s2", "label": "维权诉求", "keywords": ["12315", "投诉", "索赔", "退换", "退款", "赔偿", "退货", "维权", "投诉后退款", "贝壳碎片"], "priority": 4},
        ]
        # 品牌竞品层规则
        brand_rules = [
            # A2品牌识别
            {"layer": "brand", "stage": "s1", "label": "A2", "keywords": ["a2", "a2至初", "a2紫白金", "a2紫曜", "A2至初", "A2紫白金"], "priority": 10},
            {"layer": "brand", "stage": "s2", "label": "A2", "keywords": ["a2", "a2至初", "a2紫白金", "a2紫曜", "A2至初", "A2紫白金"], "priority": 10},
            # 爱他美
            {"layer": "brand", "stage": "s1", "label": "爱他美", "keywords": ["爱他美", "Aptamil", "aptamil"], "priority": 8},
            {"layer": "brand", "stage": "s2", "label": "爱他美", "keywords": ["爱他美", "Aptamil", "aptamil"], "priority": 8},
            # 飞鹤
            {"layer": "brand", "stage": "s1", "label": "飞鹤", "keywords": ["飞鹤", "飞鹤奶粉"], "priority": 7},
            {"layer": "brand", "stage": "s2", "label": "飞鹤", "keywords": ["飞鹤", "飞鹤奶粉"], "priority": 7},
            # 金领冠
            {"layer": "brand", "stage": "s1", "label": "金领冠", "keywords": ["金领冠", "伊利金领冠"], "priority": 7},
            {"layer": "brand", "stage": "s2", "label": "金领冠", "keywords": ["金领冠", "伊利金领冠"], "priority": 7},
            # 贝拉米
            {"layer": "brand", "stage": "s1", "label": "贝拉米", "keywords": ["贝拉米", "Bellamy", "bellamy"], "priority": 6},
            {"layer": "brand", "stage": "s2", "label": "贝拉米", "keywords": ["贝拉米", "Bellamy", "bellamy"], "priority": 6},
            # 美赞臣
            {"layer": "brand", "stage": "s1", "label": "美赞臣", "keywords": ["美赞臣", "Enfamil", "enfamil"], "priority": 6},
            {"layer": "brand", "stage": "s2", "label": "美赞臣", "keywords": ["美赞臣", "Enfamil", "enfamil"], "priority": 6},
            # 惠氏
            {"layer": "brand", "stage": "s1", "label": "惠氏", "keywords": ["惠氏", "启赋", "Wyeth", "wyeth"], "priority": 5},
            {"layer": "brand", "stage": "s2", "label": "惠氏", "keywords": ["惠氏", "启赋", "Wyeth", "wyeth"], "priority": 5},
            # 皇家美素力
            {"layer": "brand", "stage": "s1", "label": "皇家美素力", "keywords": ["皇家美素力", "Friso", "friso"], "priority": 5},
            {"layer": "brand", "stage": "s2", "label": "皇家美素力", "keywords": ["皇家美素力", "Friso", "friso"], "priority": 5},
        ]
        for rule in emotional_rules + cognitive_rules + action_rules + brand_rules:
            lr = LabelRule(
                layer=rule['layer'],
                stage=rule['stage'],
                label=rule['label'],
                keywords=rule['keywords'],
                priority=rule['priority'],
                enabled=True
            )
            session.add(lr)

    # 初始化管理员账号
    if session.query(User).count() == 0:
        import hashlib
        admin = User(
            username="admin",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),  # 默认密码 admin123
            display_name="管理员",
            role="admin",
            is_active=True
        )
        session.add(admin)

    session.commit()
    session.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized at:", DB_PATH)
