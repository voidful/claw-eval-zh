"""Shared Traditional-Chinese utilities for claw-eval-zh.

Pure stdlib by default. If the optional `opencc` package is importable it is
used for accurate simplified-character detection; otherwise a curated
simplified-only character set is used as a fallback. OpenCC is NEVER a required
dependency.

Provides:
  * find_simplified(text)           -> list of simplified-only chars present
  * strip_noncjk_spans(text)        -> text with code/URLs/paths removed
  * english_leakage_ratio(text)     -> rough fraction of latin-word content
  * ZH_EN_SYNONYMS                   -> Chinese (trad+simp) -> English canonical
  * normalize_zh_to_en(text)        -> append English canonicals after CJK terms
"""

from __future__ import annotations

import re
from typing import Dict, List

# --- Optional OpenCC ---------------------------------------------------------
_OPENCC = None
try:  # pragma: no cover - depends on optional package
    from opencc import OpenCC

    _OPENCC = OpenCC("t2s")  # traditional -> simplified, to detect mismatches
    _OPENCC_S2T = OpenCC("s2t")
except Exception:  # noqa: BLE001
    _OPENCC = None
    _OPENCC_S2T = None


def opencc_available() -> bool:
    return _OPENCC is not None


# Characters legitimately valid in BOTH scripts. Two groups:
#  (a) one simplified form maps to several traditional forms (干/里/面/松/范/余/
#      准/系/表/致/板/谷/制/划/出/升/占/困/几/丑/卜/斗/周/游/向), and
#  (b) "orthodox variant" pairs where OpenCC's s2t prefers a rarer variant over
#      the form that is STANDARD in Taiwan (群→羣, 台→臺, 峰→峯, 吃→喫, 雇→僱).
# OpenCC's context-free s2t rewrites all of these, so flagging them produces
# false positives; we never treat them as "simplified".
AMBIGUOUS_SHARED = {
    c for c in "干里面松范余准系表致板谷制划出升占困几丑卜斗周游向群台峰吃雇栗秘"
    if "一" <= c <= "鿿"
}


# --- Curated simplified-only fallback set ------------------------------------
# Common simplified characters whose Traditional form differs. Deliberately
# excludes characters shared by both scripts (件, 果, 用, 行, 你, 内, 谷, ...).
SIMPLIFIED_ONLY = set(
    "为们与个发现处过对时话题数据应设备执结请让会进较错误关键长认证风险财务邮读写"
    "软网页视频资习统产复单续报际实节专业东车马鸟鱼见贝飞银钱铁门问间队阳阴陈难顶"
    "顺须顾顿颗颜飘饭饮饱饿馆验体价优传伤俩偿储儿党册军农冲况减几凤创删则刚剧动励劳"
    "势区医华协卖卫厂历厅压厌县参双变号叹吗听启员响唤团园围图圆国圣块坚坛坏垫场壳够头"
    "夹夺奋奖妇妈娱婴学孙宁宝宠审宪宫宽宾对寻导寿将尔尘尝尽层属屿岁岂岛岭峡帅师帐带帮"
    "并广庄庆庐库庙庞废开异张弥弯录彻径忆忧怀态总恋恒恶恼恳悬惊惧惨惩惫惭惯愤愿懒戏战"
    "户扑扩扫扬扰抚抛护担拟拢据损摄摆携摊撑击挡挣挤挥换揽搁摇敌敛斋斗斩断旧旷昼显晒晕"
    "术机杀杂权条来杨极构枢枣枪枫柜标栈栋栏树样档桥桨桩梦检楼欢欧残毁毕毡气氢汇汉汤沟"
    "没沥沦沧沪泞泪泻泼泽洁洒浅浆浊测济浑浓涛涝涡涤润涧涨涩渊渐渔湾湿溃溅滚滞满滤滥滨"
    "滩灭灯灵灾灿炉点炼烁烂烛烟烦烧烩烫热焕爱爷牵牺状狭狮狱猎猪猫献环现电画畅畴疗疟疮"
    "疯痒癣皱盏盐监盖盗盘睁矫矿码砖砚础硕确碍碱礼祸祷离种积称稳穷窃窍窜窝窥竖竞笔笼筑"
    "筛筝筹签简篮篱类粪粮紧纠红纤约级纪纬纯纱纲纳纵纷纸纹纺线练组绅细织终绍经绑绒结绕"
    "绘给络绝绞统绣绪续维绵绷绸综绽绿缀缄缆缉缓缔缕编缘缚缝缠缤缩缴网罗罚罢羡翘耸耻聋"
    "职联聪肃肠肤肾肿胀胁胆胜胶脏脐脑脓脱脸腻腾舆舰舱艰艳艺节芜芦苇苍苹范茎荐荚荡荣荤"
    "荧药莱莲获莹莺萝萤营萧萨葱蒋蓝蓟蔼薇虏虑虚虽虾蚀蚁蚂蚕蛮蜗蜡蝇蝉补衬袄袜袭装裤"
    "见规觅视览觉触誉计订认讥讨让训议讯记讲讳许论讼讽设访证评诅识诈诉诊词译试诗诚话诞"
    "询该详语误诱说请诸读课谁调谅谈谊谋谎谐谓谜谢谣谦谨谬谭谱谴贝贞负贡财责贤败账货质"
    "贩贪贫贬购贮贯贱贴贵贷贸费贺贼贾贿赁赂赃资赈赊赋赌赎赏赐赔赖赚赛赞赠赡赢赵赶趋跃"
    "践踪躯车轧轨轩转轮软轰轴轻载轿较辅辆辈辉输辕辖辗辙辞辩边辽达迁过运还这进远违连迟"
    "适选逊递逻遗邓邮郑释鉴针钉钓钟钠钢钥钦钩钮钱铀铁铂铃铅铆铜铝银铸铺链销锁锅锈锋锌"
    "锐错锚锣锤锥锦键锯锰锻镀镁镇镍镑镜长门闪闭闯闰闲间闷闸闹闻阀阁阅队阳阴阵阶际陆陇"
    "陈险随隐隶难雏雾静韦韧韩韬页顶顷项顺须顽顾顿预领颇颈频题颓颗颠颤颧风飘飞饭饮饱饿"
    "馆馈馒马驭驯驰驱驳驴驶驹驻驼驾验骂骄骆骇骏骑骗骚骤骥鱼鲁鲍鲜鲤鲫鲸鳃鳄鳍鳕鳗鳝"
    "鳞鸟鸡鸣鸥鸦鸭鸳鸵鸽鸿鹃鹅鹊鹏鹤鹦鹰麦黄齐齿龄龙龚龟"
)


_URL_RE = re.compile(r"https?://\S+")
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_PATH_RE = re.compile(r"[\w./\-]+\.(?:py|md|txt|csv|json|ya?ml|ics|html|xlsx|pdf|yml)")
_IDENT_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\(")  # foo(


def strip_noncjk_spans(text: str) -> str:
    """Remove code fences, inline code, URLs, and file paths from prose.

    Used before scanning user-facing prose so whitelisted English tokens
    (filenames, URLs, identifiers in code) do not trigger leakage warnings.
    """
    text = _CODE_FENCE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _PATH_RE.sub(" ", text)
    return text


def find_simplified(text: str) -> List[str]:
    """Return sorted unique simplified-only characters present in *text*.

    Uses OpenCC (t2s round-trip) when available for accuracy, else the curated
    SIMPLIFIED_ONLY set. Code/URLs/paths are stripped first to avoid noise.
    """
    prose = strip_noncjk_spans(text)
    found = set()
    if _OPENCC is not None and _OPENCC_S2T is not None:
        for ch in set(prose):
            if not ("一" <= ch <= "鿿") or ch in AMBIGUOUS_SHARED:
                continue
            # ch is simplified-only if converting it to traditional changes it.
            if _OPENCC_S2T.convert(ch) != ch:
                found.add(ch)
    else:
        for ch in set(prose):
            if ch in SIMPLIFIED_ONLY and ch not in AMBIGUOUS_SHARED:
                found.add(ch)
    return sorted(found)


_LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")
_CJK_RE = re.compile(r"[一-鿿]")


def english_leakage_ratio(text: str) -> float:
    """Rough latin-word density of prose (after stripping code/URLs/paths).

    1.0 = all latin words, 0.0 = no latin words. A high ratio on a field that
    should be Chinese suggests untranslated English.
    """
    prose = strip_noncjk_spans(text).strip()
    if not prose:
        return 0.0
    latin = len(_LATIN_WORD_RE.findall(prose))
    cjk = len(_CJK_RE.findall(prose))
    if latin + cjk == 0:
        return 0.0
    # Weight CJK chars as ~1 token each (they pack more meaning per char).
    return latin / (latin + cjk)


# --- Grader bilingual normalization (Chinese -> English canonical) -----------
# Maps Chinese natural-language terms (both Traditional and Simplified) to the
# English canonical word(s) used by PinchBench graders, so a Chinese report can
# satisfy the original English keyword checks. Longest keys are applied first.
ZH_EN_SYNONYMS: Dict[str, str] = {
    # trend direction
    "上升趨勢": "upward trend bullish uptrend", "上升趋势": "upward trend bullish uptrend",
    "上漲趨勢": "upward trend bullish uptrend", "上涨趋势": "upward trend bullish uptrend",
    "下降趨勢": "downward trend bearish downtrend", "下降趋势": "downward trend bearish downtrend",
    "下跌趨勢": "downward trend bearish downtrend", "下跌趋势": "downward trend bearish downtrend",
    "看漲": "bullish", "看涨": "bullish", "多頭": "bullish", "多头": "bullish",
    "看跌": "bearish", "空頭": "bearish", "空头": "bearish",
    "上漲": "up increase rise", "上涨": "up increase rise",
    "下跌": "down decline drop",
    "上升": "up increase rise upward", "下降": "down decrease decline downward",
    "盤整": "sideways flat", "盘整": "sideways flat", "橫盤": "sideways", "横盘": "sideways",
    "區間震盪": "sideways range", "区间震荡": "sideways range",
    # stats / analysis
    "月均": "monthly average", "每月平均": "monthly average", "月度平均": "monthly average",
    "各月平均": "monthly average", "每月": "monthly", "月度": "monthly",
    "摘要": "summary", "總結": "summary", "总结": "summary",
    "結論": "conclusion", "结论": "conclusion",
    "異常": "anomaly anomalies error", "异常": "anomaly anomalies error",
    "離群值": "outlier outliers", "离群值": "outlier outliers",
    "離群": "outlier", "离群": "outlier", "可疑": "suspicious anomaly", "不尋常": "unusual anomaly",
    "不寻常": "unusual anomaly",
    "連續上漲": "consecutive up gain", "连续上涨": "consecutive up gain",
    "連續下跌": "consecutive down decline", "连续下跌": "consecutive down decline",
    "連續": "consecutive", "连续": "consecutive",
    "百分比": "percent percentage", "成長": "growth increase", "增長": "growth increase",
    "增长": "growth increase", "波動": "volatility", "波动": "volatility",
    "標準差": "standard deviation std", "标准差": "standard deviation std",
    "平均": "average mean", "中位數": "median", "中位数": "median",
    "反彈": "rally rebound", "反弹": "rally rebound", "回落": "decline pullback",
    "新高": "high peak", "高點": "high peak", "高点": "high peak", "峰值": "peak",
    # logs / security
    "錯誤": "error", "错误": "error", "失敗": "failed failure", "失败": "failed failure",
    "成功": "success successful", "警告": "warning", "嚴重": "critical severe",
    "严重": "critical severe", "關鍵": "critical key", "关键": "critical key",
    "安全": "security", "風險": "risk", "风险": "risk", "漏洞": "vulnerability",
    "弱點": "weakness vulnerability", "弱点": "weakness vulnerability", "威脅": "threat",
    "威胁": "threat", "暴力破解": "brute force", "登入": "login", "登錄": "login",
    "登录": "login", "狀態碼": "status code", "状态码": "status code", "流量": "traffic",
    "回應時間": "response time", "响应时间": "response time", "慢請求": "slow request",
    "慢请求": "slow request",
    # meetings
    "待辦": "action item", "行動項目": "action item", "後續事項": "follow up action item",
    "后续事项": "follow up action item", "與會者": "attendee attendees participant",
    "与会者": "attendee attendees participant", "出席者": "attendee", "參與者": "participant",
    "参与者": "participant", "決議": "decision", "决议": "decision", "決定": "decision",
    "决定": "decision", "投票": "vote votes", "預算": "budget", "预算": "budget",
    "情緒": "sentiment", "情绪": "sentiment", "建議": "recommendation suggestion",
    "建议": "recommendation suggestion", "競爭對手": "competitor competitors",
    "竞争对手": "competitor competitors", "時間軸": "timeline", "时间轴": "timeline",
    # generic report
    "報告": "report", "报告": "report", "趨勢": "trend", "趋势": "trend",
    "走勢": "trend movement", "走势": "trend movement",
}


def normalize_zh_to_en(text: str) -> str:
    """Make a Chinese report satisfy English keyword checks.

    The original text is preserved verbatim (so bilingual graders' Chinese
    patterns still match contiguous phrases like 連續下跌). English canonicals
    for every Chinese term present are appended as one block at the END, so
    English keyword checks (`re.search('bullish', content)`) also match.

    Inline insertion is deliberately avoided: it would split contiguous Chinese
    phrases (連續下跌 -> 連續 consecutive 下跌) and break order-dependent regex.
    """
    found: List[str] = []
    seen = set()
    for zh in sorted(ZH_EN_SYNONYMS, key=len, reverse=True):
        if zh in text:
            en = ZH_EN_SYNONYMS[zh]
            if en not in seen:
                found.append(en)
                seen.add(en)
    if found:
        text = text + "\n\n<!-- zh2en keywords: " + " ".join(found) + " -->\n"
    return text
