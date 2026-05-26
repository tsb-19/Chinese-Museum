#!/usr/bin/env python3
"""Generate individual museum pages from artifacts.json.

Creates /museum/index.html (museum listing) and /museum/<slug>.html per museum.
Also generates a museum index section to embed in the main page.

Usage: python scripts/generate_museum_pages.py
"""

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_JSON = os.path.join(ROOT, "data", "artifacts.json")
MUSEUM_DIR = os.path.join(ROOT, "museum")

# Province lookup (same as generate_tags.py)
MUSEUM_PROVINCE = {
    "故宫博物院": "北京", "中国国家博物馆": "北京", "首都博物馆": "北京",
    "北京鲁迅博物馆": "北京", "北京古代建筑博物馆": "北京", "国家自然博物馆": "北京",
    "天津博物馆": "天津",
    "河北博物院": "河北", "临城县邢窑博物馆": "河北", "定州博物馆": "河北",
    "正定县博物馆": "河北", "泥河湾博物馆": "河北", "磁县北朝考古博物馆": "河北",
    "迁安市博物馆": "河北", "邺城博物馆": "河北", "黄骅市博物馆": "河北",
    "山西省博物院": "山西", "山西博物院": "山西", "临汾市博物馆": "山西",
    "晋祠博物馆": "山西", "运城博物馆": "山西", "长治市博物馆": "山西",
    "内蒙古博物院": "内蒙古",
    "辽宁省博物馆": "辽宁", "旅顺博物馆": "辽宁", "沈阳故宫博物院": "辽宁",
    "吉林省博物院": "吉林", "吉林市满族博物馆": "吉林", "吉林省自然博物馆": "吉林",
    "伪满皇宫博物院": "吉林",
    "黑龙江省博物馆": "黑龙江", "哈尔滨市博物馆": "黑龙江",
    "上海博物馆": "上海", "上海城市历史发展陈列馆": "上海", "上海天文博物馆": "上海",
    "上海市历史博物馆": "上海", "上海自然博物馆": "上海", "中华艺术宫": "上海",
    "南京博物院": "江苏", "苏州博物馆": "江苏", "南通博物苑": "江苏",
    "常州博物馆": "江苏", "徐州博物馆": "江苏", "徐州汉兵马俑博物馆": "江苏",
    "扬州博物馆": "江苏", "无锡博物院": "江苏", "淮安市博物馆": "江苏",
    "连云港市博物馆": "江苏", "镇江博物馆": "江苏", "隋唐大运河文化博物馆": "江苏",
    "浙江省博物馆": "浙江", "东阳市博物馆": "浙江", "宁波博物馆": "浙江",
    "杭州博物馆": "浙江", "杭州西湖博物馆": "浙江", "浙江自然博物院": "浙江",
    "温州博物馆": "浙江", "湖州市博物馆": "浙江", "绍兴博物馆": "浙江",
    "金华市博物馆": "浙江",
    "安徽博物院": "安徽", "安徽省博物馆": "安徽", "安徽楚文化博物馆": "安徽",
    "蚌埠市博物馆": "安徽",
    "福建博物院": "福建", "厦门博物馆": "福建", "厦门市博物馆": "福建",
    "泉州海外交通史博物馆": "福建", "福建民俗博物馆": "福建", "莆田市博物馆": "福建",
    "漳州市博物馆": "福建",
    "江西省博物馆": "江西", "井冈山革命博物馆": "江西", "八大山人纪念馆": "江西",
    "南昌汉代海昏侯国遗址博物馆": "江西", "景德镇中国陶瓷博物馆": "江西",
    "抚州市博物馆": "江西", "瑞金中央革命根据地纪念馆": "江西", "高安市博物馆": "江西",
    "山东博物馆": "山东", "青岛市博物馆": "山东",
    "河南博物院": "河南", "河南省博物院": "河南", "二里头夏都遗址博物馆": "河南",
    "安阳殷墟博物馆": "河南", "殷墟博物馆": "河南", "洛阳博物馆": "河南",
    "洛阳古墓博物馆": "河南", "开封市博物馆": "河南", "商丘博物馆": "河南",
    "南阳汉画馆": "河南", "郑州博物馆": "河南",
    "湖北省博物馆": "湖北", "华中师范大学博物馆": "湖北", "武汉博物馆": "湖北",
    "湖南省博物馆": "湖南", "湖南博物院": "湖南", "长沙简牍博物馆": "湖南",
    "广东省博物馆": "广东", "东莞市博物馆": "广东", "中山市博物馆": "广东",
    "广东海上丝绸之路博物馆": "广东", "广州博物馆": "广东", "广州铁路博物馆": "广东",
    "深圳博物馆": "广东",
    "广西壮族自治区博物馆": "广西", "广西民族博物馆": "广西",
    "海南省博物馆": "海南", "三亚自然博物馆": "海南", "中国（海南）南海博物馆": "海南",
    "海南省民族博物馆": "海南", "海南铁路博物馆": "海南",
    "重庆中国三峡博物馆": "重庆", "重庆红岩革命历史博物馆": "重庆",
    "四川博物院": "四川", "四川博物馆": "四川", "成都金沙遗址博物馆": "四川",
    "三星堆博物馆": "四川", "成都博物馆": "四川", "成都杜甫草堂博物馆": "四川",
    "成都武侯祠博物馆": "四川", "大足石刻博物馆": "四川", "罗家坝遗址博物馆": "四川",
    "贵州省博物馆": "贵州", "平坝博物馆": "贵州", "贵州省地质博物馆": "贵州",
    "贵州省民族博物馆": "贵州", "遵义市博物馆": "贵州", "黔东南州民族博物馆": "贵州",
    "黔西南州博物馆": "贵州",
    "云南省博物馆": "云南", "丽江市博物院": "云南", "保山市博物馆": "云南",
    "大理白族自治州博物馆": "云南", "西双版纳民族博物馆": "云南", "昆明市博物馆": "云南",
    "西藏博物馆": "西藏", "西黎民族文化展示馆": "西藏",
    "陕西历史博物馆": "陕西", "秦始皇帝陵博物院": "陕西", "西安碑林博物馆": "陕西",
    "咸阳博物院": "陕西", "宝鸡青铜器博物院": "陕西", "汉景帝阳陵博物院": "陕西",
    "法门寺博物馆": "陕西", "西安博物院": "陕西", "陕西考古博物馆": "陕西",
    "甘肃省博物馆": "甘肃", "甘肃简牍博物馆": "甘肃",
    "青海省博物馆": "青海", "青海原子城纪念馆": "青海", "青海藏医药文化博物馆": "青海",
    "宁夏博物馆": "宁夏", "宁夏回族自治区博物馆": "宁夏",
    "新疆维吾尔自治区博物馆": "新疆", "新疆博物馆": "新疆", "喀什地区博物馆": "新疆",
    "台北故宫博物院": "台湾",
    "澳门博物馆": "澳门",
    "香港故宫文化博物馆": "香港",
}

PROVINCE_NAMES = [
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
    "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
    "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
    "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆",
]

PROVINCE_EN = {
    "北京": "Beijing", "天津": "Tianjin", "河北": "Hebei", "山西": "Shanxi",
    "内蒙古": "Inner Mongolia", "辽宁": "Liaoning", "吉林": "Jilin",
    "黑龙江": "Heilongjiang", "上海": "Shanghai", "江苏": "Jiangsu",
    "浙江": "Zhejiang", "安徽": "Anhui", "福建": "Fujian", "江西": "Jiangxi",
    "山东": "Shandong", "河南": "Henan", "湖北": "Hubei", "湖南": "Hunan",
    "广东": "Guangdong", "广西": "Guangxi", "海南": "Hainan", "重庆": "Chongqing",
    "四川": "Sichuan", "贵州": "Guizhou", "云南": "Yunnan", "西藏": "Tibet",
    "陕西": "Shaanxi", "甘肃": "Gansu", "青海": "Qinghai", "宁夏": "Ningxia",
    "新疆": "Xinjiang",
}


# Manual slug mapping for all museums (human-readable URLs)
MUSEUM_SLUGS = {
    "故宫博物院": "gugong",
    "中国国家博物馆": "guojia-bowuguan",
    "首都博物馆": "shoudu-bowuguan",
    "北京鲁迅博物馆": "luxun-jinianguan",
    "北京古代建筑博物馆": "gudai-jianzhu",
    "国家自然博物馆": "ziran-bowuguan",
    "天津博物馆": "tianjin",
    "河北博物院": "hebei",
    "临城县邢窑博物馆": "xingyao",
    "定州博物馆": "dingzhou",
    "正定县博物馆": "zhengding",
    "泥河湾博物馆": "nihewan",
    "磁县北朝考古博物馆": "beichao-kaogu",
    "迁安市博物馆": "qianan",
    "邺城博物馆": "yecheng",
    "黄骅市博物馆": "huanghua",
    "山西省博物院": "shanxi",
    "山西博物院": "shanxi",
    "临汾市博物馆": "linfen",
    "晋祠博物馆": "jinci",
    "运城博物馆": "yuncheng",
    "长治市博物馆": "changzhi",
    "内蒙古博物院": "neimenggu",
    "辽宁省博物馆": "liaoning",
    "旅顺博物馆": "lvshun",
    "辽上京博物馆": "liaoshangjing",
    "沈阳故宫博物院": "shenyang-gugong",
    "吉林省博物院": "jilin",
    "吉林市满族博物馆": "jilin-manzu",
    "吉林省自然博物馆": "jilin-ziran",
    "伪满皇宫博物院": "weimang-huanggong",
    "黑龙江省博物馆": "heilongjiang",
    "哈尔滨市博物馆": "haerbin",
    "上海博物馆": "shanghai",
    "上海城市历史发展陈列馆": "shanghai-chengshi",
    "上海天文博物馆": "shanghai-tianwen",
    "上海市历史博物馆": "shanghai-lishi",
    "上海自然博物馆": "shanghai-ziran",
    "中华艺术宫": "zhonghua-yishu",
    "南京博物院": "nanjing",
    "南平市博物馆": "nanping",
    "南越王博物院": "nanyuewang",
    "苏州博物馆": "suzhou",
    "南通博物苑": "nantong",
    "常州博物馆": "changzhou",
    "徐州博物馆": "xuzhou",
    "徐州汉兵马俑博物馆": "xuzhou-bingmayong",
    "扬州博物馆": "yangzhou",
    "无锡博物院": "wuxi",
    "淮安市博物馆": "huaian",
    "连云港市博物馆": "lianyungang",
    "镇江博物馆": "zhenjiang",
    "隋唐大运河文化博物馆": "suitang-dayunhe",
    "浙江省博物馆": "zhejiang",
    "东阳市博物馆": "dongyang",
    "宁波博物馆": "ningbo",
    "杭州博物馆": "hangzhou",
    "杭州西湖博物馆": "hangzhou-xihu",
    "浙江自然博物院": "zhejiang-ziran",
    "温州博物馆": "wenzhou",
    "湖州市博物馆": "huzhou",
    "绍兴博物馆": "shaoxing",
    "金华市博物馆": "jinhua",
    "安徽博物院": "anhui",
    "安徽省博物馆": "anhui",
    "安徽楚文化博物馆": "anhui-chuwenhua",
    "蚌埠市博物馆": "bengbu",
    "福建博物院": "fujian",
    "厦门博物馆": "xiamen",
    "厦门市博物馆": "xiamen",
    "泉州海外交通史博物馆": "quanzhou-haijiao",
    "福建民俗博物馆": "fujian-minsu",
    "莆田市博物馆": "putian",
    "漳州市博物馆": "zhangzhou",
    "江西省博物馆": "jiangxi",
    "井冈山革命博物馆": "jinggangshan",
    "八大山人纪念馆": "badashanren",
    "南昌汉代海昏侯国遗址博物馆": "haihunhou",
    "景德镇中国陶瓷博物馆": "jingdezhen-taoci",
    "抚州市博物馆": "fuzhou",
    "瑞金中央革命根据地纪念馆": "ruijin",
    "高安市博物馆": "gaoan",
    "山东博物馆": "shandong",
    "青岛市博物馆": "qingdao",
    "河南博物院": "henan",
    "河南省博物院": "henan",
    "二里头夏都遗址博物馆": "erlitou",
    "安阳殷墟博物馆": "anyang-yinxu",
    "殷墟博物馆": "yinxu",
    "洛阳博物馆": "luoyang",
    "洛阳古墓博物馆": "luoyang-gumu",
    "开封市博物馆": "kaifeng",
    "商丘博物馆": "shangqiu",
    "南阳汉画馆": "nanyang-hanhua",
    "郑州博物馆": "zhengzhou",
    "湖北省博物馆": "hubei",
    "华中师范大学博物馆": "huazhong-shifan",
    "武汉博物馆": "wuhan",
    "湖南省博物馆": "hunan",
    "湖南博物院": "hunan",
    "长沙简牍博物馆": "changsha-jiandu",
    "广东省博物馆": "guangdong",
    "东莞市博物馆": "dongguan",
    "中山市博物馆": "zhongshan",
    "广东海上丝绸之路博物馆": "guangdong-haisi",
    "广州博物馆": "guangzhou",
    "广州铁路博物馆": "guangzhou-tielu",
    "深圳博物馆": "shenzhen",
    "广西壮族自治区博物馆": "guangxi",
    "广西民族博物馆": "guangxi-minzu",
    "海南省博物馆": "hainan",
    "三亚自然博物馆": "sanya-ziran",
    "中国（海南）南海博物馆": "hainan-nanhai",
    "海南省民族博物馆": "hainan-minzu",
    "海南铁路博物馆": "hainan-tielu",
    "重庆中国三峡博物馆": "chongqing-sanxia",
    "重庆红岩革命历史博物馆": "chongqing-hongyan",
    "四川博物院": "sichuan",
    "四川博物馆": "sichuan",
    "成都金沙遗址博物馆": "chengdu-jinsha",
    "三星堆博物馆": "sanxingdui",
    "成都博物馆": "chengdu",
    "成都杜甫草堂博物馆": "chengdu-dufu",
    "成都武侯祠博物馆": "chengdu-wuhou",
    "大足石刻博物馆": "dazu-shike",
    "罗家坝遗址博物馆": "luojiaba",
    "贵州省博物馆": "guizhou",
    "平坝博物馆": "pingba",
    "贵州省地质博物馆": "guizhou-dizhi",
    "贵州省民族博物馆": "guizhou-minzu",
    "遵义市博物馆": "zunyi",
    "黔东南州民族博物馆": "qiandongnan-minzu",
    "黔西南州博物馆": "qianxinan",
    "云南省博物馆": "yunnan",
    "丽江市博物院": "lijiang",
    "保山市博物馆": "baoshan",
    "大理白族自治州博物馆": "dali",
    "西双版纳民族博物馆": "xishuangbanna-minzu",
    "昆明市博物馆": "kunming",
    "西藏博物馆": "xizang",
    "西黎民族文化展示馆": "xili-minzu",
    "陕西历史博物馆": "shaanxi-lishi",
    "秦始皇帝陵博物院": "qinshihuang-ling",
    "西安碑林博物馆": "xian-beilin",
    "咸阳博物院": "xianyang",
    "宝鸡青铜器博物院": "baoji-qingtongqi",
    "汉景帝阳陵博物院": "yangling",
    "法门寺博物馆": "famensi",
    "西安博物院": "xian",
    "陕西考古博物馆": "shaanxi-kaogu",
    "甘肃省博物馆": "gansu",
    "甘肃简牍博物馆": "gansu-jiandu",
    "青海省博物馆": "qinghai",
    "青海原子城纪念馆": "qinghai-yuanzicheng",
    "青海藏医药文化博物馆": "qinghai-zangyiyao",
    "宁夏博物馆": "ningxia",
    "宁夏回族自治区博物馆": "ningxia",
    "新疆维吾尔自治区博物馆": "xinjiang",
    "新疆博物馆": "xinjiang",
    "喀什地区博物馆": "kashi",
    "台北故宫博物院": "taibei-gugong",
    "澳门博物馆": "aomen",
    "香港故宫文化博物馆": "xianggang-gugong",
}


def slugify(text):
    """Create a URL-friendly slug from Chinese museum name."""
    return MUSEUM_SLUGS.get(text, text)


def get_province(museum_name):
    return MUSEUM_PROVINCE.get(museum_name, "")


def generate_museum_page(museum_name, artifacts, slug):
    """Generate an HTML page for a single museum."""
    province = get_province(museum_name)
    count = len(artifacts)

    # Build artifact rows
    rows = ""
    for art in artifacts:
        img_cell = ""
        img_url = art.get("高清图片来源链接_1", "")
        if img_url:
            img_cell = f'<img width="400" height="300" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src=\'/assets/image-fallback.svg\';" src="{img_url}" alt="{art["文物名称"]}" style="max-width:300px;max-height:200px;border-radius:8px;cursor:pointer;" onclick="window.open(this.src)">'
        else:
            img_cell = '<span style="color:#999;">暂无图片</span>'

        ref = art.get("参考文件", "")
        ref_cell = ""
        if ref and ref != "-":
            # Extract URLs from reference text
            urls = re.findall(r'https?://[^\s\]]+', ref)
            if urls:
                ref_cell = " ".join(
                    f'<a href="{u}" target="_blank" rel="noopener" style="color:#059669;">[{i+1}]</a>'
                    for i, u in enumerate(urls[:3])
                )
            else:
                ref_cell = ref[:50]
        elif ref == "-":
            ref_cell = ""

        rows += f"""<tr>
  <td><strong>{art['文物名称']}</strong></td>
  <td>{art.get('历史年代', '-')}</td>
  <td>{art.get('主要材质', '-')}</td>
  <td style="max-width:400px;font-size:0.9em;line-height:1.6;">{art.get('外观与结构特征描述', '-')}</td>
  <td>{art.get('制作工艺技术', '-')}</td>
  <td>{img_cell}</td>
  <td style="font-size:0.85em;">{ref_cell}</td>
</tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{museum_name} 镇馆之宝 - Chinese Museum Treasures</title>
<meta name="description" content="{museum_name}的{count}件镇馆之宝，包含文物图片、年代、材质、工艺等详细信息。">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://chinese-museum.vercel.app/museum/{slug}.html">
<script src="https://cdn.tailwindcss.com/3.4.17.js"></script>
<style>
  body {{ font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', system-ui, sans-serif; background: #F0FDF4; color: #14532D; }}
  .table-scroll-wrapper {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th {{ background: rgba(5,150,105,0.08); font-weight: 600; text-align: left; padding: 0.75rem; white-space: nowrap; }}
  td {{ padding: 0.75rem; border-bottom: 1px solid rgba(5,150,105,0.1); vertical-align: top; }}
  tr:hover td {{ background: rgba(5,150,105,0.04); }}
  a {{ color: #059669; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body class="min-h-screen">
<header style="background: linear-gradient(135deg, #F0FDF4 0%, #05966910 50%, #84CC1608 100%); padding: 2rem 1.5rem; text-align: center;">
  <a href="/" style="color: #059669; font-size: 0.9rem;">&larr; 返回首页 / Back to Home</a>
  <h1 style="font-size: clamp(1.5rem, 4vw, 2.2rem); font-weight: 700; color: #14532D; margin: 0.5em 0 0.3em;">{museum_name}</h1>
  <p style="color: #4D7C0F; font-size: 0.95rem;">{province + ' · ' if province else ''}{count} 件镇馆之宝</p>
</header>
<main class="mx-auto px-4 py-6 sm:px-8 lg:px-12" style="max-width: 1400px;">
  <div class="table-scroll-wrapper">
    <table>
      <thead>
        <tr>
          <th>文物名称</th>
          <th>历史年代</th>
          <th>主要材质</th>
          <th>外观与结构特征</th>
          <th>制作工艺技术</th>
          <th>图片</th>
          <th>参考</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>
</main>
<footer style="text-align:center; padding:2rem; color:#4D7C0F; font-size:0.85rem; border-top:1px solid rgba(5,150,105,0.15);">
  <a href="/" style="color:#059669;">返回首页 / Back to Home</a>
</footer>
</body>
</html>"""
    return html


def generate_museum_index(museums_by_province):
    """Generate HTML for the museum index section to embed in main page."""
    html = '<div class="museum-index">\n'

    for province in PROVINCE_NAMES:
        museums = museums_by_province.get(province, [])
        if not museums:
            continue
        en = PROVINCE_EN.get(province, "")
        html += f'<div class="museum-province-group">\n'
        html += f'<h3 class="museum-province-title">{province} {en}</h3>\n'
        html += '<div class="museum-list">\n'
        for name, slug, count in sorted(museums, key=lambda x: -x[2]):
            html += f'<a href="/museum/{slug}.html" class="museum-card">'
            html += f'<span class="museum-name">{name}</span>'
            html += f'<span class="museum-count">{count}件</span>'
            html += '</a>\n'
        html += '</div>\n</div>\n'

    html += '</div>'
    return html


def main():
    with open(ARTIFACTS_JSON, "r", encoding="utf-8") as f:
        artifacts = json.load(f)

    # Group by museum
    by_museum = {}
    for art in artifacts:
        name = art["所属博物馆名称"]
        by_museum.setdefault(name, []).append(art)

    print(f"Total: {len(by_museum)} museums, {len(artifacts)} artifacts")

    # Create museum directory
    os.makedirs(MUSEUM_DIR, exist_ok=True)

    # Generate pages and build index data
    museums_by_province = {}
    pages_generated = 0

    for museum_name, arts in sorted(by_museum.items(), key=lambda x: -len(x[1])):
        slug = slugify(museum_name)
        province = get_province(museum_name)

        # Generate sub-page
        html = generate_museum_page(museum_name, arts, slug)
        filepath = os.path.join(MUSEUM_DIR, f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        pages_generated += 1

        # Add to index
        if province:
            museums_by_province.setdefault(province, []).append(
                (museum_name, slug, len(arts))
            )

    # Generate index HTML
    index_html = generate_museum_index(museums_by_province)
    index_path = os.path.join(MUSEUM_DIR, "_index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)

    # Also generate a simple museum index page
    index_page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>博物馆索引 - Chinese Museum Treasures</title>
<meta name="description" content="中国各大博物馆镇馆之宝完整索引，按省份分类浏览。">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://chinese-museum.vercel.app/museum/">
<script src="https://cdn.tailwindcss.com/3.4.17.js"></script>
<style>
  body {{ font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', system-ui, sans-serif; background: #F0FDF4; color: #14532D; }}
  a {{ color: #059669; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .museum-province-group {{ margin-bottom: 1.5rem; }}
  .museum-province-title {{ font-size: 1.1rem; font-weight: 700; color: #14532D; margin-bottom: 0.5rem; padding-bottom: 0.3rem; border-bottom: 2px solid rgba(5,150,105,0.15); }}
  .museum-list {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
  .museum-card {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.85); border: 1px solid rgba(5,150,105,0.15); border-radius: 0.75rem; transition: all 0.2s; font-size: 0.9rem; }}
  .museum-card:hover {{ background: rgba(5,150,105,0.08); border-color: rgba(5,150,105,0.3); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-decoration: none; }}
  .museum-count {{ font-size: 0.75rem; color: #4D7C0F; background: rgba(5,150,105,0.08); padding: 0.15rem 0.5rem; border-radius: 9999px; }}
</style>
</head>
<body class="min-h-screen">
<header style="background: linear-gradient(135deg, #F0FDF4 0%, #05966910 50%, #84CC1608 100%); padding: 2rem 1.5rem; text-align: center;">
  <a href="/" style="color: #059669; font-size: 0.9rem;">&larr; 返回首页 / Back to Home</a>
  <h1 style="font-size: clamp(1.5rem, 4vw, 2.2rem); font-weight: 700; color: #14532D; margin: 0.5em 0 0.3em;">中国各大博物馆镇馆之宝</h1>
  <p style="color: #4D7C0F; font-size: 0.95rem;">{len(by_museum)} 家博物馆 · {len(artifacts)} 件文物</p>
</header>
<main class="mx-auto px-4 py-6 sm:px-8 lg:px-12" style="max-width: 1200px;">
{index_html}
</main>
<footer style="text-align:center; padding:2rem; color:#4D7C0F; font-size:0.85rem; border-top:1px solid rgba(5,150,105,0.15);">
  <a href="/" style="color:#059669;">返回首页 / Back to Home</a>
</footer>
</body>
</html>"""

    with open(os.path.join(MUSEUM_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page)

    print(f"Generated {pages_generated} museum pages in {MUSEUM_DIR}/")
    print(f"Generated museum index: {MUSEUM_DIR}/index.html")
    print(f"Index HTML fragment: {MUSEUM_DIR}/_index.html")

    # Output slug mapping for reference
    slug_map = {}
    for museum_name in by_museum:
        slug_map[museum_name] = slugify(museum_name)
    with open(os.path.join(MUSEUM_DIR, "_slug_map.json"), "w", encoding="utf-8") as f:
        json.dump(slug_map, f, ensure_ascii=False, indent=2)
    print(f"Slug map: {MUSEUM_DIR}/_slug_map.json")


if __name__ == "__main__":
    main()
