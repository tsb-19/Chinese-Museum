#!/usr/bin/env python3
"""Generate sitemap.xml with museum sub-page URLs."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path

BASE = "https://chinese-museum.vercel.app"
MAX_URLS_PER_SITEMAP = 500

# Same slug mapping as generate_museum_pages.py
MUSEUM_SLUGS = {
    "故宫博物院": "gugong", "中国国家博物馆": "guojia-bowuguan",
    "首都博物馆": "shoudu-bowuguan", "北京鲁迅博物馆": "luxun-jinianguan",
    "北京古代建筑博物馆": "gudai-jianzhu", "国家自然博物馆": "ziran-bowuguan",
    "天津博物馆": "tianjin", "河北博物院": "hebei",
    "临城县邢窑博物馆": "xingyao", "定州博物馆": "dingzhou",
    "正定县博物馆": "zhengding", "泥河湾博物馆": "nihewan",
    "磁县北朝考古博物馆": "beichao-kaogu", "迁安市博物馆": "qianan",
    "邺城博物馆": "yecheng", "黄骅市博物馆": "huanghua",
    "山西省博物院": "shanxi", "山西博物院": "shanxi",
    "临汾市博物馆": "linfen", "晋祠博物馆": "jinci",
    "运城博物馆": "yuncheng", "长治市博物馆": "changzhi",
    "内蒙古博物院": "neimenggu", "辽宁省博物馆": "liaoning",
    "旅顺博物馆": "lvshun", "辽上京博物馆": "liaoshangjing",
    "沈阳故宫博物院": "shenyang-gugong",
    "吉林省博物院": "jilin", "吉林市满族博物馆": "jilin-manzu",
    "吉林省自然博物馆": "jilin-ziran", "伪满皇宫博物院": "weimang-huanggong",
    "黑龙江省博物馆": "heilongjiang", "哈尔滨市博物馆": "haerbin",
    "上海博物馆": "shanghai", "上海城市历史发展陈列馆": "shanghai-chengshi",
    "上海天文博物馆": "shanghai-tianwen", "上海市历史博物馆": "shanghai-lishi",
    "上海自然博物馆": "shanghai-ziran", "中华艺术宫": "zhonghua-yishu",
    "南京博物院": "nanjing", "南平市博物馆": "nanping",
    "南越王博物院": "nanyuewang", "苏州博物馆": "suzhou",
    "南通博物苑": "nantong", "常州博物馆": "changzhou",
    "徐州博物馆": "xuzhou", "徐州汉兵马俑博物馆": "xuzhou-bingmayong",
    "扬州博物馆": "yangzhou", "无锡博物院": "wuxi",
    "淮安市博物馆": "huaian", "连云港市博物馆": "lianyungang",
    "镇江博物馆": "zhenjiang", "隋唐大运河文化博物馆": "suitang-dayunhe",
    "浙江省博物馆": "zhejiang", "东阳市博物馆": "dongyang",
    "宁波博物馆": "ningbo", "杭州博物馆": "hangzhou",
    "杭州西湖博物馆": "hangzhou-xihu", "浙江自然博物院": "zhejiang-ziran",
    "温州博物馆": "wenzhou", "湖州市博物馆": "huzhou",
    "绍兴博物馆": "shaoxing", "金华市博物馆": "jinhua",
    "安徽博物院": "anhui", "安徽省博物馆": "anhui",
    "安徽楚文化博物馆": "anhui-chuwenhua", "蚌埠市博物馆": "bengbu",
    "福建博物院": "fujian", "厦门博物馆": "xiamen",
    "厦门市博物馆": "xiamen", "泉州海外交通史博物馆": "quanzhou-haijiao",
    "福建民俗博物馆": "fujian-minsu", "莆田市博物馆": "putian",
    "漳州市博物馆": "zhangzhou", "江西省博物馆": "jiangxi",
    "井冈山革命博物馆": "jinggangshan", "八大山人纪念馆": "badashanren",
    "南昌汉代海昏侯国遗址博物馆": "haihunhou",
    "景德镇中国陶瓷博物馆": "jingdezhen-taoci", "抚州市博物馆": "fuzhou",
    "瑞金中央革命根据地纪念馆": "ruijin", "高安市博物馆": "gaoan",
    "山东博物馆": "shandong", "青岛市博物馆": "qingdao",
    "河南博物院": "henan", "河南省博物院": "henan",
    "二里头夏都遗址博物馆": "erlitou", "安阳殷墟博物馆": "anyang-yinxu",
    "殷墟博物馆": "yinxu", "洛阳博物馆": "luoyang",
    "洛阳古墓博物馆": "luoyang-gumu", "开封市博物馆": "kaifeng",
    "商丘博物馆": "shangqiu", "南阳汉画馆": "nanyang-hanhua",
    "郑州博物馆": "zhengzhou", "湖北省博物馆": "hubei",
    "华中师范大学博物馆": "huazhong-shifan", "武汉博物馆": "wuhan",
    "湖南省博物馆": "hunan", "湖南博物院": "hunan",
    "长沙简牍博物馆": "changsha-jiandu", "广东省博物馆": "guangdong",
    "东莞市博物馆": "dongguan", "中山市博物馆": "zhongshan",
    "广东海上丝绸之路博物馆": "guangdong-haisi", "广州博物馆": "guangzhou",
    "广州铁路博物馆": "guangzhou-tielu", "深圳博物馆": "shenzhen",
    "广西壮族自治区博物馆": "guangxi", "广西民族博物馆": "guangxi-minzu",
    "海南省博物馆": "hainan", "三亚自然博物馆": "sanya-ziran",
    "中国（海南）南海博物馆": "hainan-nanhai", "海南省民族博物馆": "hainan-minzu",
    "海南铁路博物馆": "hainan-tielu", "重庆中国三峡博物馆": "chongqing-sanxia",
    "重庆红岩革命历史博物馆": "chongqing-hongyan", "四川博物院": "sichuan",
    "四川博物馆": "sichuan", "成都金沙遗址博物馆": "chengdu-jinsha",
    "三星堆博物馆": "sanxingdui", "成都博物馆": "chengdu",
    "成都杜甫草堂博物馆": "chengdu-dufu", "成都武侯祠博物馆": "chengdu-wuhou",
    "大足石刻博物馆": "dazu-shike", "罗家坝遗址博物馆": "luojiaba",
    "贵州省博物馆": "guizhou", "平坝博物馆": "pingba",
    "贵州省地质博物馆": "guizhou-dizhi", "贵州省民族博物馆": "guizhou-minzu",
    "遵义市博物馆": "zunyi", "黔东南州民族博物馆": "qiandongnan-minzu",
    "黔西南州博物馆": "qianxinan", "云南省博物馆": "yunnan",
    "丽江市博物院": "lijiang", "保山市博物馆": "baoshan",
    "大理白族自治州博物馆": "dali", "西双版纳民族博物馆": "xishuangbanna-minzu",
    "昆明市博物馆": "kunming", "西藏博物馆": "xizang",
    "西黎民族文化展示馆": "xili-minzu", "陕西历史博物馆": "shaanxi-lishi",
    "秦始皇帝陵博物院": "qinshihuang-ling", "西安碑林博物馆": "xian-beilin",
    "咸阳博物院": "xianyang", "宝鸡青铜器博物院": "baoji-qingtongqi",
    "汉景帝阳陵博物院": "yangling", "法门寺博物馆": "famensi",
    "西安博物院": "xian", "陕西考古博物馆": "shaanxi-kaogu",
    "甘肃省博物馆": "gansu", "甘肃简牍博物馆": "gansu-jiandu",
    "青海省博物馆": "qinghai", "青海原子城纪念馆": "qinghai-yuanzicheng",
    "青海藏医药文化博物馆": "qinghai-zangyiyao", "宁夏博物馆": "ningxia",
    "宁夏回族自治区博物馆": "ningxia", "新疆维吾尔自治区博物馆": "xinjiang",
    "新疆博物馆": "xinjiang", "喀什地区博物馆": "kashi",
    "台北故宫博物院": "taibei-gugong", "澳门博物馆": "aomen",
    "香港故宫文化博物馆": "xianggang-gugong",
}


def render_urlset(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main() -> int:
    data = json.loads(Path("data/artifacts.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()

    # Home page
    urls = [
        f"  <url>\n    <loc>{BASE}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>",
        f"  <url>\n    <loc>{BASE}/museum/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>",
    ]

    # Museum sub-pages (deduplicated by slug)
    seen_slugs = set()
    museums = sorted({str(d.get("所属博物馆名称", "")).strip() for d in data if str(d.get("所属博物馆名称", "")).strip()})
    for m in museums:
        slug = MUSEUM_SLUGS.get(m)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        urls.append(
            f"  <url>\n    <loc>{BASE}/museum/{slug}.html</loc>\n"
            f"    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n"
            f"    <priority>0.7</priority>\n  </url>"
        )

    chunks = [urls[i:i + MAX_URLS_PER_SITEMAP] for i in range(0, len(urls), MAX_URLS_PER_SITEMAP)]
    if len(chunks) == 1:
        Path("sitemap.xml").write_text(render_urlset(chunks[0]), encoding="utf-8")
    else:
        sitemap_files = []
        for i, chunk in enumerate(chunks, start=1):
            name = f"sitemap-{i}.xml"
            Path(name).write_text(render_urlset(chunk), encoding="utf-8")
            sitemap_files.append(name)
        index = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join([f"  <sitemap><loc>{BASE}/{name}</loc></sitemap>" for name in sitemap_files])
            + "\n</sitemapindex>\n"
        )
        Path("sitemap.xml").write_text(index, encoding="utf-8")

    print(f"Generated sitemap with {len(urls)} urls ({len(seen_slugs)} museum pages) in {len(chunks)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
