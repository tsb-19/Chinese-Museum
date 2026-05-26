#!/usr/bin/env python3
"""Generate tags for CARDS_DATA in index.html by joining with artifacts.json.

Reads CARDS_DATA from index.html, joins with artifacts.json by artifact name,
generates dynasty/material/type/province tags, adds museum name to otherFields,
and writes enriched CARDS_DATA back into index.html.

Usage: python scripts/generate_tags.py
"""

import json
import re
import os

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(ROOT, "index.html")
ARTIFACTS_JSON = os.path.join(ROOT, "data", "artifacts.json")

# --- Dynasty normalization map ---
# Maps raw 历史年代 values to canonical dynasty tags.
# Some raw values produce multiple tags (ranges).

DYNASTY_MAP = {
    # Exact matches
    "新石器时代": ["新石器时代"],
    "新石器时期": ["新石器时代"],
    "旧石器时代": ["旧石器时代"],
    "夏代": ["夏代"],
    "商": ["商代"],
    "商朝": ["商代"],
    "商代": ["商代"],
    "商代早期": ["商代"],
    "商代晚期": ["商代"],
    "商代后期": ["商代"],
    "殷商末期": ["商代"],
    "西周": ["西周"],
    "西周早期": ["西周"],
    "西周中期": ["西周"],
    "西周晚期": ["西周"],
    "春秋": ["春秋"],
    "春秋时期": ["春秋"],
    "春秋中期": ["春秋"],
    "春秋晚期": ["春秋"],
    "战国": ["战国"],
    "战国时期": ["战国"],
    "战国早期": ["战国"],
    "战国中期": ["战国"],
    "战国晚期": ["战国"],
    "战国中晚期": ["战国"],
    "秦代": ["秦代"],
    "西汉": ["西汉"],
    "西汉早期": ["西汉"],
    "东汉": ["东汉"],
    "东汉中晚期": ["东汉"],
    "汉": ["汉代"],
    "汉朝": ["汉代"],
    "汉代": ["汉代"],
    "三国时期": ["三国"],
    "曹魏": ["三国"],
    "西晋": ["西晋"],
    "东晋": ["东晋"],
    "南朝": ["南北朝"],
    "北魏": ["南北朝"],
    "北齐": ["南北朝"],
    "东魏": ["南北朝"],
    "南北朝": ["南北朝"],
    "隋代": ["隋代"],
    "隋唐": ["隋代", "唐代"],
    "唐": ["唐代"],
    "唐朝": ["唐代"],
    "唐代": ["唐代"],
    "晚唐": ["唐代"],
    "唐五代时期": ["唐代", "五代"],
    "五代": ["五代"],
    "五代十国": ["五代"],
    "五代南唐": ["五代"],
    "五代后唐": ["五代"],
    "五代、前蜀": ["五代"],
    "北宋": ["北宋"],
    "南宋": ["南宋"],
    "宋": ["宋代"],
    "宋代": ["宋代"],
    "宋元时期": ["宋代", "元代"],
    "宋辽金时期": ["宋代", "辽代", "金代"],
    "宋大理国": ["宋代"],
    "辽代": ["辽代"],
    "辽金时期": ["辽代", "金代"],
    "金代": ["金代"],
    "元": ["元代"],
    "元代": ["元代"],
    "西夏": ["西夏"],
    "明": ["明代"],
    "明代": ["明代"],
    "明末清初": ["明代", "清代"],
    "明代宣德": ["明代"],
    "明代永乐": ["明代"],
    "明代永乐宣德时期": ["明代"],
    "明代弘治年间": ["明代"],
    "明代中期": ["明代"],
    "明代成化年间": ["明代"],
    "明洪武": ["明代"],
    "明嘉靖": ["明代"],
    "明宣德": ["明代"],
    "明万历十五年(1587)": ["明代"],
    "明成化七年": ["明代"],
    "明成化七年（1471年）": ["明代"],
    "明弘治至正德早期": ["明代"],
    "晚明": ["明代"],
    "清": ["清代"],
    "清朝": ["清代"],
    "清代": ["清代"],
    "清初": ["清代"],
    "清末": ["清代"],
    "清末民初": ["清代", "近现代"],
    "清代初期": ["清代"],
    "清代光绪": ["清代"],
    "清代乾隆年间": ["清代"],
    "清代中后期": ["清代"],
    "清代乾隆五十三年（1788年）": ["清代"],
    "清中期": ["清代"],
    "清乾隆": ["清代"],
    "晚清": ["清代"],
    "民国": ["近现代"],
    "伪满时期": ["近现代"],
    "近现代": ["近现代"],
    "近代": ["近现代"],
    "当代": ["近现代"],
    "1900年": ["近现代"],
    "1949年": ["近现代"],
    "1949年8月": ["近现代"],
    "1952年": ["近现代"],
    "20世纪": ["近现代"],
    "20世纪30年代": ["近现代"],
    "20世纪60年代": ["近现代"],
    "二十世纪70年代": ["近现代"],
    "抗日战争时期": ["近现代"],
    "解放战争时期": ["近现代"],
    "晋代": ["晋代"],
    "前凉": ["十六国"],
    "北凉": ["十六国"],
    "北燕·十六国": ["十六国"],
    "十六国时期": ["十六国"],
    "古代": [],
    "黎族传统工艺": [],
    # Paleontological
    "白垩纪": ["史前"],
    "侏罗纪": ["史前"],
    "晚侏罗世（约1.6亿年前）": ["史前"],
    "三叠纪": ["史前"],
    "三叠纪晚期": ["史前"],
    "晚三叠世": ["史前"],
    "更新世": ["史前"],
    "晚更新世": ["史前"],
    "距今200万年的早更新世": ["史前"],
    "约200万年前": ["史前"],
    "1.4亿年前": ["史前"],
    "距今4500多万年": ["史前"],
    "寒武纪": ["史前"],
    "距今4200至4000年": ["史前"],
    "距今3800年": ["史前"],
    "距今约3800年": ["史前"],
    "距今6000多年": ["史前"],
    # Cultural periods
    "仰韶文化": ["新石器时代"],
    "新石器时代仰韶文化": ["新石器时代"],
    "仰韶文化石岭下类型": ["新石器时代"],
    "仰韶文化中晚期（距今5500-6000年前）": ["新石器时代"],
    "龙山文化": ["新石器时代"],
    "大汶口文化": ["新石器时代"],
    "石家河文化": ["新石器时代"],
    "良渚文化中距今4500年前后": ["新石器时代"],
    "良渚文化时期": ["新石器时代"],
    "马家浜文化": ["新石器时代"],
    "新石器时代马家浜文化": ["新石器时代"],
    "新石器时代马家窑文化": ["新石器时代"],
    "新石器时代辛店文化": ["新石器时代"],
    "新石器时代晚期": ["新石器时代"],
    "新石器时代晚期红山文化": ["新石器时代"],
    "红山文化时期": ["新石器时代"],
    "红山文化·新石器时代": ["新石器时代"],
    "马家窑文化": ["新石器时代"],
    "青铜时代辛店文化": ["商代"],
    "青铜时代齐家文化": ["商代"],
    "齐家文化": ["新石器时代"],
    "齐家文化时期": ["新石器时代"],
    # Ranges
    "商周时期": ["商代", "西周"],
    "商周": ["商代", "西周"],
    "春秋战国": ["春秋", "战国"],
    "战国至汉代": ["战国", "汉代"],
    "战国至西汉": ["战国", "西汉"],
    "战国晚期至秦代": ["战国", "秦代"],
    "战国晚期至秦": ["战国", "秦代"],
    "东汉至西晋": ["东汉", "西晋"],
    "汉魏": ["汉代", "三国"],
    "汉魏时期": ["汉代", "三国"],
    "汉晋": ["汉代", "晋代"],
    "汉代到魏晋时期": ["汉代"],
    "秦汉时期": ["秦代", "汉代"],
    "魏晋时期": ["晋代"],
    "辽·耀州窑": ["辽代"],
    "唐·欧阳询": ["唐代"],
    "唐摹本": ["唐代"],
    "唐代渤海国": ["唐代"],
    "上衣20世纪80年代 裙子清代": ["清代", "近现代"],
    "后金天命八年": ["清代"],
    "公元十二世纪（大理国时期）": ["宋代"],
    "明代成化年间": ["明代"],
    "明清时期": ["明代", "清代"],
}

# --- Material normalization ---
MATERIAL_MAP = {
    "青铜": "青铜",
    "铜": "青铜",
    "铜质": "青铜",
    "瓷器": "瓷器",
    "瓷": "瓷器",
    "青瓷": "瓷器",
    "青釉瓷": "瓷器",
    "陶瓷": "陶瓷",
    "陶": "陶瓷",
    "陶器": "陶瓷",
    "泥质灰陶": "陶瓷",
    "玉": "玉器",
    "玉石": "玉器",
    "汉白玉": "玉器",
    "石": "石器",
    "石材": "石器",
    "石质": "石器",
    "青石": "石器",
    "金": "金银器",
    "黄金": "金银器",
    "银": "金银器",
    "银鎏金": "金银器",
    "铁": "金属器",
    "金属": "金属器",
    "绢本设色": "书画",
    "绢本": "书画",
    "纸本设色": "书画",
    "纸本墨书": "书画",
    "纸本": "书画",
    "纸": "书画",
    "纸张": "书画",
    "壁画": "书画",
    "木材": "木器",
    "漆木": "木器",
    "竹木简": "竹木简",
    "竹简": "竹木简",
    "化石": "化石",
    "琉璃": "琉璃/玻璃",
    "玻璃": "琉璃/玻璃",
    "象牙": "牙骨器",
    "漆器": "漆器",
}

# --- Object type extraction from artifact name ---
# Maps suffix characters to type tags
TYPE_SUFFIXES = {
    "鼎": "青铜器",
    "尊": "青铜器",
    "壶": "青铜器",
    "盘": "青铜器",
    "簋": "青铜器",
    "鬲": "青铜器",
    "爵": "青铜器",
    "觚": "青铜器",
    "觥": "青铜器",
    "卣": "青铜器",
    "盉": "青铜器",
    "匜": "青铜器",
    "钟": "青铜器",
    "镈": "青铜器",
    "鉴": "青铜器",
    "缶": "青铜器",
    "敦": "青铜器",
    "豆": "青铜器",
    "甗": "青铜器",
    "罍": "青铜器",
    "编钟": "青铜器",
    "铜镜": "铜镜",
    "镜": "铜镜",
    "璧": "玉器",
    "琮": "玉器",
    "璜": "玉器",
    "圭": "玉器",
    "璋": "玉器",
    "环": "玉器",
    "玦": "玉器",
    "佩": "玉器",
    "碗": "瓷器",
    "瓶": "瓷器",
    "罐": "瓷器",
    "杯": "瓷器",
    "盏": "瓷器",
    "碟": "瓷器",
    "缸": "瓷器",
    "炉": "香炉/炉具",
    "香炉": "香炉/炉具",
    "印": "印章",
    "玺": "印章",
    "画": "绘画",
    "卷": "书画",
    "帖": "书法",
    "册": "书画",
    "轴": "书画",
    "衣": "服饰",
    "袍": "服饰",
    "裳": "服饰",
    "裙": "服饰",
    "冠": "服饰",
    "冕": "服饰",
    "碑": "碑刻",
    "墓志": "碑刻",
    "简": "简牍",
    "牍": "简牍",
    "帛书": "帛书",
    "俑": "雕塑",
    "佛像": "雕塑",
    "造像": "雕塑",
    "塔": "宗教文物",
    "钟": "青铜器",
}

# --- Province extraction from museum name ---
MUSEUM_PROVINCE = {
    "故宫博物院": "北京",
    "中国国家博物馆": "北京",
    "首都博物馆": "北京",
    "北京鲁迅博物馆": "北京",
    "北京古代建筑博物馆": "北京",
    "国家自然博物馆": "北京",
    "天津博物馆": "天津",
    "河北博物院": "河北",
    "临城县邢窑博物馆": "河北",
    "定州博物馆": "河北",
    "正定县博物馆": "河北",
    "泥河湾博物馆": "河北",
    "磁县北朝考古博物馆": "河北",
    "迁安市博物馆": "河北",
    "邺城博物馆": "河北",
    "黄骅市博物馆": "河北",
    "山西省博物院": "山西",
    "山西博物院": "山西",
    "临汾市博物馆": "山西",
    "晋祠博物馆": "山西",
    "运城博物馆": "山西",
    "长治市博物馆": "山西",
    "内蒙古博物院": "内蒙古",
    "辽宁省博物馆": "辽宁",
    "旅顺博物馆": "辽宁",
    "沈阳故宫博物院": "辽宁",
    "吉林省博物院": "吉林",
    "吉林市满族博物馆": "吉林",
    "吉林省自然博物馆": "吉林",
    "伪满皇宫博物院": "吉林",
    "黑龙江省博物馆": "黑龙江",
    "哈尔滨市博物馆": "黑龙江",
    "上海博物馆": "上海",
    "上海城市历史发展陈列馆": "上海",
    "上海天文博物馆": "上海",
    "上海市历史博物馆": "上海",
    "上海自然博物馆": "上海",
    "中华艺术宫": "上海",
    "南京博物院": "江苏",
    "苏州博物馆": "江苏",
    "南通博物苑": "江苏",
    "常州博物馆": "江苏",
    "徐州博物馆": "江苏",
    "徐州汉兵马俑博物馆": "江苏",
    "扬州博物馆": "江苏",
    "无锡博物院": "江苏",
    "淮安市博物馆": "江苏",
    "连云港市博物馆": "江苏",
    "镇江博物馆": "江苏",
    "隋唐大运河文化博物馆": "江苏",
    "浙江省博物馆": "浙江",
    "东阳市博物馆": "浙江",
    "宁波博物馆": "浙江",
    "杭州博物馆": "浙江",
    "杭州西湖博物馆": "浙江",
    "浙江自然博物院": "浙江",
    "温州博物馆": "浙江",
    "湖州市博物馆": "浙江",
    "绍兴博物馆": "浙江",
    "金华市博物馆": "浙江",
    "安徽博物院": "安徽",
    "安徽省博物馆": "安徽",
    "安徽楚文化博物馆": "安徽",
    "蚌埠市博物馆": "安徽",
    "福建博物院": "福建",
    "厦门博物馆": "福建",
    "厦门市博物馆": "福建",
    "泉州海外交通史博物馆": "福建",
    "福建民俗博物馆": "福建",
    "莆田市博物馆": "福建",
    "漳州市博物馆": "福建",
    "江西省博物馆": "江西",
    "井冈山革命博物馆": "江西",
    "八大山人纪念馆": "江西",
    "南昌汉代海昏侯国遗址博物馆": "江西",
    "景德镇中国陶瓷博物馆": "江西",
    "抚州市博物馆": "江西",
    "瑞金中央革命根据地纪念馆": "江西",
    "高安市博物馆": "江西",
    "山东博物馆": "山东",
    "青岛市博物馆": "山东",
    "河南博物院": "河南",
    "河南省博物院": "河南",
    "二里头夏都遗址博物馆": "河南",
    "安阳殷墟博物馆": "河南",
    "殷墟博物馆": "河南",
    "洛阳博物馆": "河南",
    "洛阳古墓博物馆": "河南",
    "开封市博物馆": "河南",
    "商丘博物馆": "河南",
    "南阳汉画馆": "河南",
    "郑州博物馆": "河南",
    "湖北省博物馆": "湖北",
    "华中师范大学博物馆": "湖北",
    "武汉博物馆": "湖北",
    "湖南省博物馆": "湖南",
    "湖南博物院": "湖南",
    "长沙简牍博物馆": "湖南",
    "广东省博物馆": "广东",
    "东莞市博物馆": "广东",
    "中山市博物馆": "广东",
    "广东海上丝绸之路博物馆": "广东",
    "广州博物馆": "广东",
    "广州铁路博物馆": "广东",
    "深圳博物馆": "广东",
    "广西壮族自治区博物馆": "广西",
    "广西民族博物馆": "广西",
    "海南省博物馆": "海南",
    "三亚自然博物馆": "海南",
    "中国（海南）南海博物馆": "海南",
    "海南省民族博物馆": "海南",
    "海南铁路博物馆": "海南",
    "重庆中国三峡博物馆": "重庆",
    "重庆红岩革命历史博物馆": "重庆",
    "四川博物院": "四川",
    "四川博物馆": "四川",
    "成都金沙遗址博物馆": "四川",
    "三星堆博物馆": "四川",
    "成都博物馆": "四川",
    "成都杜甫草堂博物馆": "四川",
    "成都武侯祠博物馆": "四川",
    "大足石刻博物馆": "四川",
    "罗家坝遗址博物馆": "四川",
    "贵州省博物馆": "贵州",
    "平坝博物馆": "贵州",
    "贵州省地质博物馆": "贵州",
    "贵州省民族博物馆": "贵州",
    "遵义市博物馆": "贵州",
    "黔东南州民族博物馆": "贵州",
    "黔西南州博物馆": "贵州",
    "云南省博物馆": "云南",
    "丽江市博物院": "云南",
    "保山市博物馆": "云南",
    "大理白族自治州博物馆": "云南",
    "西双版纳民族博物馆": "云南",
    "昆明市博物馆": "云南",
    "西藏博物馆": "西藏",
    "西黎民族文化展示馆": "西藏",
    "陕西历史博物馆": "陕西",
    "秦始皇帝陵博物院": "陕西",
    "西安碑林博物馆": "陕西",
    "咸阳博物院": "陕西",
    "宝鸡青铜器博物院": "陕西",
    "汉景帝阳陵博物院": "陕西",
    "法门寺博物馆": "陕西",
    "西安博物院": "陕西",
    "陕西考古博物馆": "陕西",
    "甘肃省博物馆": "甘肃",
    "甘肃简牍博物馆": "甘肃",
    "青海省博物馆": "青海",
    "青海原子城纪念馆": "青海",
    "青海藏医药文化博物馆": "青海",
    "宁夏博物馆": "宁夏",
    "宁夏回族自治区博物馆": "宁夏",
    "新疆维吾尔自治区博物馆": "新疆",
    "新疆博物馆": "新疆",
    "喀什地区博物馆": "新疆",
    "台北故宫博物院": "台湾",
    "澳门博物馆": "澳门",
    "香港故宫文化博物馆": "香港",
}


def extract_province(museum_name):
    """Extract province from museum name using lookup table only."""
    return MUSEUM_PROVINCE.get(museum_name)


def normalize_dynasty(raw):
    """Normalize a raw dynasty string to canonical tags."""
    if not raw or raw == "-":
        return []
    raw = raw.strip()
    # Direct lookup
    if raw in DYNASTY_MAP:
        return DYNASTY_MAP[raw]
    # Try to extract dynasty from parenthetical dates like "明成化七年（1471年）"
    cleaned = re.sub(r"[（(].*?[）)]", "", raw).strip()
    if cleaned in DYNASTY_MAP:
        return DYNASTY_MAP[cleaned]
    # Try substring matching for common dynasty names
    dynasty_keywords = [
        ("新石器时代", "新石器时代"),
        ("旧石器时代", "旧石器时代"),
        ("夏", "夏代"),
        ("商", "商代"),
        ("西周", "西周"),
        ("东周", "春秋"),
        ("春秋", "春秋"),
        ("战国", "战国"),
        ("秦", "秦代"),
        ("西汉", "西汉"),
        ("东汉", "东汉"),
        ("汉", "汉代"),
        ("三国", "三国"),
        ("魏", "三国"),
        ("蜀", "三国"),
        ("吴", "三国"),
        ("西晋", "西晋"),
        ("东晋", "东晋"),
        ("晋", "晋代"),
        ("南朝", "南北朝"),
        ("北朝", "南北朝"),
        ("隋", "隋代"),
        ("唐", "唐代"),
        ("五代", "五代"),
        ("北宋", "北宋"),
        ("南宋", "南宋"),
        ("宋", "宋代"),
        ("辽", "辽代"),
        ("金", "金代"),
        ("元", "元代"),
        ("西夏", "西夏"),
        ("明", "明代"),
        ("清", "清代"),
        ("民国", "近现代"),
        ("近现代", "近现代"),
        ("当代", "近现代"),
        ("史前", "史前"),
        ("白垩纪", "史前"),
        ("侏罗纪", "史前"),
        ("三叠纪", "史前"),
    ]
    # Sort by length descending to match longer keywords first
    dynasty_keywords.sort(key=lambda x: -len(x[0]))
    for keyword, tag in dynasty_keywords:
        if keyword in raw:
            return [tag]
    return []


def normalize_material(raw):
    """Normalize a raw material string to a canonical category."""
    if not raw or raw == "-":
        return None
    raw = raw.strip()
    # Direct lookup
    if raw in MATERIAL_MAP:
        return MATERIAL_MAP[raw]
    # Try comma-separated compound materials
    parts = re.split(r"[、,，/]", raw)
    primary = parts[0].strip()
    if primary in MATERIAL_MAP:
        return MATERIAL_MAP[primary]
    # Try substring matching
    for key, val in MATERIAL_MAP.items():
        if key in raw:
            return val
    return None


def extract_type(artifact_name):
    """Extract object type from artifact name suffix."""
    if not artifact_name:
        return None
    # Try multi-char suffixes first (sorted by length desc)
    sorted_suffixes = sorted(TYPE_SUFFIXES.items(), key=lambda x: -len(x[0]))
    for suffix, type_tag in sorted_suffixes:
        if artifact_name.endswith(suffix):
            return type_tag
    return None


def generate_tags(item, museum_name):
    """Generate tags for a CARDS_DATA item."""
    tags = []
    seen = set()

    # Extract dynasty from otherFields
    dynasty_raw = ""
    material_raw = ""
    for field in item.get("otherFields", []):
        if field["label"] == "历史年代":
            dynasty_raw = field["value"]
        elif field["label"] == "主要材质":
            material_raw = field["value"]

    # Dynasty tags
    for dt in normalize_dynasty(dynasty_raw):
        if dt not in seen:
            tags.append(dt)
            seen.add(dt)

    # Material tag
    mat = normalize_material(material_raw)
    if mat and mat not in seen:
        tags.append(mat)
        seen.add(mat)

    # Object type tag
    typ = extract_type(item.get("name", ""))
    if typ and typ not in seen:
        tags.append(typ)
        seen.add(typ)

    # Merge similar tags
    MERGE_MAP = {"书法": "书画", "绘画": "书画"}
    tags = [MERGE_MAP.get(t, t) for t in tags]
    # Deduplicate after merge
    seen = set()
    deduped = []
    for t in tags:
        if t not in seen:
            deduped.append(t)
            seen.add(t)

    return deduped


def main():
    # Read artifacts.json
    with open(ARTIFACTS_JSON, "r", encoding="utf-8") as f:
        artifacts = json.load(f)

    # Build lookup by artifact name
    art_by_name = {}
    for art in artifacts:
        art_by_name[art["文物名称"]] = art

    # Read index.html
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and parse CARDS_DATA
    pattern = r"(const CARDS_DATA = )(\[.*?\]);"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("ERROR: Could not find CARDS_DATA in index.html")
        return

    cards_data = json.loads(match.group(2))
    print(f"Parsed {len(cards_data)} CARDS_DATA items")

    # Enrich each item
    enriched = 0
    tagged = 0
    for item in cards_data:
        name = item.get("name", "")
        art = art_by_name.get(name)
        museum_name = art["所属博物馆名称"] if art else None

        # Add museum name to otherFields if not already present
        has_museum = any(
            f["label"] == "所属博物馆名称" for f in item.get("otherFields", [])
        )
        if museum_name and not has_museum:
            item["otherFields"].append(
                {"label": "所属博物馆名称", "value": museum_name}
            )
            enriched += 1

        # Generate tags
        new_tags = generate_tags(item, museum_name)
        if new_tags:
            item["tags"] = new_tags
            tagged += 1
        else:
            item["tags"] = []

    print(f"Added museum name to {enriched} items")
    print(f"Generated tags for {tagged} items")

    # Count tag frequencies
    tag_counts = {}
    for item in cards_data:
        for tag in item["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Remove low-frequency tags (≤5 occurrences)
    MIN_FREQ = 5
    low_freq = {t for t, c in tag_counts.items() if c <= MIN_FREQ}
    if low_freq:
        for item in cards_data:
            item["tags"] = [t for t in item["tags"] if t not in low_freq]
        print(f"\nRemoved {len(low_freq)} low-frequency tags (≤{MIN_FREQ}): {sorted(low_freq)}")

    # Recount after filtering
    all_tags = {}
    for item in cards_data:
        for tag in item["tags"]:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    print(f"\nTag distribution ({len(all_tags)} unique tags):")
    for tag, count in sorted(all_tags.items(), key=lambda x: -x[1])[:30]:
        print(f"  {count:4d}  {tag}")

    # Write enriched CARDS_DATA back
    new_json = json.dumps(cards_data, ensure_ascii=False, separators=(",", ":"))
    new_content = content[: match.start(2)] + new_json + content[match.end(2) :]

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\nUpdated CARDS_DATA in {INDEX_HTML}")


if __name__ == "__main__":
    main()
