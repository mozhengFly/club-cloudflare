import random
import string
from typing import List


# 中文词汇库
CHINESE_ADJECTIVES = [
    '温柔', '冷酷', '优雅', '神秘', '浪漫', '忧郁', '阳光', '月光',
    '星光', '清风', '细雨', '晨曦', '暮色', '流年', '浮生', '红尘',
    '墨染', '诗韵', '画境', '云淡', '风轻', '雪舞', '花落', '花开',
    '梦碎', '梦醒', '追忆', '遗忘', '寂寞', '孤独', '繁华', '寂静',
    '缥缈', '朦胧', '璀璨', '黯淡', '宁静', '喧嚣', '悠远', '深邃',
    '清冷', '炽热', '纯净', '混沌', '空灵', '灵动', '飘逸', '洒脱',
    '淡雅', '素净', '清雅', '幽雅', '婉约', '豪放', '奔放', '内敛',
    '张扬', '低调', '华丽', '朴素', '绚烂', '平淡', '惊艳', '平凡',
    '唯美', '凄美', '壮美', '秀美', '绝美', '残缺', '完美', '遗憾',
    '欢喜', '悲伤', '快乐', '痛苦', '幸福', '忧伤', '甜蜜', '苦涩'
]

CHINESE_NOUNS = [
    '星辰', '大海', '天空', '云朵', '山川', '河流', '森林', '草原',
    '玫瑰', '茉莉', '樱花', '枫叶', '蝴蝶', '飞鸟', '游鱼', '萤火虫',
    '琴音', '书香', '墨香', '茶香', '酒香', '诗行', '画卷', '梦境',
    '岁月', '时光', '年华', '青春', '回忆', '故事', '传说', '神话',
    '影子', '倒影', '涟漪', '烟雾', '尘埃', '露珠', '雪花', '雨滴',
    '明月', '残阳', '流星', '极光', '彩虹', '薄雾', '寒霜', '冰晶',
    '青竹', '翠柳', '红莲', '白梅', '紫藤', '金桂', '银荷', '玉兰花',
    '孤舟', '断桥', '古寺', '长亭', '短桥', '深巷', '小巷', '庭院',
    '楼阁', '轩窗', '帘幕', '屏风', '烛火', '灯火', '星光', '月色',
    '心事', '情愫', '思念', '牵挂', '眷恋', '依恋', '痴迷', '执着'
]

CHINESE_TWO_CHAR = [
    '听雨', '观云', '踏雪', '寻梅', '望月', '临风', '醉墨', '抚琴',
    '弄影', '吹笛', '煮茶', '酌酒', '吟风', '弄月', '倚楼', '凭栏',
    '听雨', '看云', '踏浪', '追风', '追星', '揽月', '摘星', '拂尘',
    '品茗', '赏花', '观海', '登山', '涉水', '游园', '漫步', '闲逛',
    '独坐', '静思', '冥想', '沉思', '凝望', '远眺', '回首', '顾盼',
    '挥毫', '泼墨', '题诗', '作词', '作画', '弹琴', '下棋', '读书',
    '采菊', '种豆', '耕田', '织布', '刺绣', '剪纸', '雕刻', '书法',
    '问禅', '悟道', '修行', '参透', '顿悟', '觉醒', '超脱', '释然'
]

CHINESE_FOUR_CHAR = [
    '清风明月', '云淡风轻', '花前月下', '沧海桑田', '天涯海角',
    '如梦似幻', '诗情画意', '鸟语花香', '山清水秀', '春暖花开',
    '雪落无声', '细雨绵绵', '繁星点点', '灯火阑珊', '烟波浩渺',
    '琴棋书画', '笔墨纸砚', '风花雪月', '春夏秋冬', '梅兰竹菊',
    '一叶知秋', '落花流水', '云卷云舒', '花开花落', '潮起潮落',
    '日升月落', '斗转星移', '物是人非', '时过境迁', '岁月如歌',
    '静水流深', '大智若愚', '返璞归真', '顺其自然', '随遇而安',
    '心旷神怡', '悠然自得', '闲云野鹤', '世外桃源', '人间仙境',
    '金风玉露', '珠联璧合', '天作之合', '郎才女貌', '才子佳人',
    '高山流水', '知音难觅', '伯牙子期', '肝胆相照', '情同手足'
]

# 英文词汇库
ENGLISH_ADJECTIVES = [
    'silent', 'gentle', 'dark', 'bright', 'mystic', 'dreamy', 'stormy', 'peaceful',
    'wild', 'calm', 'frozen', 'burning', 'shining', 'fading', 'hidden', 'secret',
    'eternal', 'temporal', 'celestial', 'terrestrial', 'ethereal', 'mortal', 'divine', 'sacred',
    'whisper', 'echo', 'shadow', 'light', 'night', 'day', 'dawn', 'dusk',
    'crimson', 'azure', 'golden', 'silver', 'emerald', 'violet', 'scarlet', 'ivory',
    'velvet', 'crystal', 'diamond', 'pearl', 'jade', 'amber', 'onyx', 'opal',
    'ancient', 'modern', 'classic', 'vintage', 'retro', 'futuristic', 'cosmic', 'galactic',
    'royal', 'noble', 'majestic', 'regal', 'imperial', 'sovereign', 'supreme', 'ultimate',
    'radiant', 'luminous', 'brilliant', 'glowing', 'sparkling', 'gleaming', 'glistening', 'shimmering'
]

ENGLISH_NOUNS = [
    'star', 'moon', 'sun', 'sky', 'ocean', 'river', 'forest', 'mountain',
    'flower', 'butterfly', 'bird', 'wolf', 'phoenix', 'dragon', 'angel', 'demon',
    'dream', 'reality', 'memory', 'hope', 'love', 'soul', 'heart', 'mind',
    'wind', 'fire', 'water', 'earth', 'cloud', 'rain', 'snow', 'lightning',
    'crystal', 'diamond', 'pearl', 'ruby', 'sapphire', 'emerald', 'topaz', 'amethyst',
    'rose', 'lily', 'lotus', 'orchid', 'tulip', 'daisy', 'jasmine', 'lavender',
    'eagle', 'hawk', 'falcon', 'raven', 'swan', 'peacock', 'hummingbird', 'owl',
    'tiger', 'lion', 'panther', 'leopard', 'cheetah', 'bear', 'deer', 'fox',
    'galaxy', 'universe', 'nebula', 'comet', 'meteor', 'constellation', 'orbit', 'eclipse'
]

ENGLISH_WORDS = [
    'serendipity', 'ephemeral', 'luminous', 'melancholy', 'nostalgia', 'ethereal',
    'wanderlust', 'solitude', 'tranquility', 'resilience', 'verisimilitude', 'ubiquitous',
    'quintessential', 'inexorable', 'effervescent', 'sagacious', 'eloquent', 'tenacious',
    'enigmatic', 'resplendent', 'lucid', 'pragmatic', 'meticulous', 'spontaneous'
]

# 混合词汇
MIXED_PATTERNS = [
    ('adj_en', 'noun_cn'),
    ('adj_cn', 'noun_en'),
    ('noun_en', 'adj_cn'),
    ('noun_cn', 'adj_en'),
    ('two_cn', 'en_word'),
    ('en_word', 'two_cn'),
]


SPECIAL_SYMBOLS = ['丶', '灬', '丿', '丨', '氵', '丷', '亻', '宀', '冫', '讠', '饣', '扌', '纟']


def generate_chinese_nickname() -> str:
    """生成中文网名"""
    patterns = [
        lambda: random.choice(CHINESE_ADJECTIVES) + random.choice(CHINESE_NOUNS),
        lambda: random.choice(CHINESE_TWO_CHAR),
        lambda: random.choice(CHINESE_FOUR_CHAR) + random.choice(SPECIAL_SYMBOLS),
        lambda: random.choice(CHINESE_NOUNS) + random.choice(CHINESE_ADJECTIVES),
        lambda: random.choice(CHINESE_ADJECTIVES) + random.choice(CHINESE_ADJECTIVES),
        lambda: random.choice(CHINESE_NOUNS) + str(random.randint(1, 99)),
    ]
    return random.choice(patterns)()


def generate_english_nickname() -> str:
    """生成英文网名"""
    patterns = [
        lambda: random.choice(ENGLISH_ADJECTIVES).capitalize() + random.choice(ENGLISH_NOUNS).capitalize(),
        lambda: random.choice(ENGLISH_NOUNS).capitalize() + random.choice(ENGLISH_ADJECTIVES).capitalize(),
        lambda: random.choice(ENGLISH_WORDS).capitalize(),
        lambda: random.choice(ENGLISH_WORDS).capitalize() + str(random.randint(1, 99)),
        lambda: ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))),
        lambda: random.choice(ENGLISH_ADJECTIVES).capitalize() + str(random.randint(100, 999)),
        lambda: random.choice(ENGLISH_NOUNS).capitalize() + str(random.randint(10, 99)),
    ]
    return random.choice(patterns)()


def generate_mixed_nickname() -> str:
    """生成中英混合网名"""
    pattern = random.choice(MIXED_PATTERNS)

    parts = []
    for p in pattern:
        if p == 'adj_en':
            parts.append(random.choice(ENGLISH_ADJECTIVES).capitalize())
        elif p == 'noun_en':
            parts.append(random.choice(ENGLISH_NOUNS).capitalize())
        elif p == 'adj_cn':
            parts.append(random.choice(CHINESE_ADJECTIVES))
        elif p == 'noun_cn':
            parts.append(random.choice(CHINESE_NOUNS))
        elif p == 'two_cn':
            parts.append(random.choice(CHINESE_TWO_CHAR))
        elif p == 'en_word':
            parts.append(random.choice(ENGLISH_WORDS).capitalize())

    separator = random.choice(['', '_', '-', ''])
    return separator.join(parts)


def generate_special_nickname() -> str:
    """生成特殊风格网名"""
    patterns = [
        lambda: ''.join(random.choices('✦✧★☆♡♥♠♣♦♢◈◇◆●○◉◎◦', k=random.randint(1, 3))) +
                generate_chinese_nickname() +
                ''.join(random.choices('✦✧★☆♡♥♠♣♦♢◈◇◆●○◉◎◦', k=random.randint(1, 3))),
        lambda: generate_chinese_nickname() + ''.join(random.choices(string.digits, k=random.randint(1, 4))),
        lambda: generate_english_nickname() + ''.join(random.choices('._-', k=1)) + str(random.randint(10, 99)),
        lambda: random.choice(['丶', '灬', '丿', '丨', '氵', '艹', '亻', '宀']) + generate_chinese_nickname(),
        lambda: generate_chinese_nickname() + random.choice(['丶', '灬', '丿', '丨']),
    ]
    return random.choice(patterns)()


def generate_nickname(style: str = 'random', max_length: int = 12) -> str:
    """
    生成网名
    :param style: 风格类型
                  - random: 随机风格
                  - chinese: 中文网名
                  - english: 英文网名
                  - mixed: 中英混合
                  - special: 特殊符号
    :param max_length: 最大长度，默认为12
    :return: 生成的网名
    """
    generators = {
        'chinese': generate_chinese_nickname,
        'english': generate_english_nickname,
        'mixed': generate_mixed_nickname,
        'special': generate_special_nickname,
    }

    if style in generators:
        generator = generators[style]
    else:
        generator = random.choice(list(generators.values()))

    # 循环生成直到满足长度要求
    for _ in range(100):
        nickname = generator()
        if len(nickname) <= max_length:
            return nickname

    # 如果100次都没生成符合要求的，直接返回截断后的结果
    nickname = generator()
    return nickname[:max_length]


def generate_nicknames(count: int = 10, style: str = 'random', max_length: int = 12) -> List[str]:
    """
    生成多个网名
    :param count: 生成数量
    :param style: 风格类型
    :param max_length: 最大长度，默认为12
    :return: 网名列表
    """
    result = []
    for _ in range(count):
        result.append(generate_nickname(style, max_length))
    return result


def main():
    print("🎲 网名生成器")
    print("=" * 30)

    while True:
        try:
            count = int(input("请输入要生成的网名数量: "))
            if count <= 0:
                print("请输入大于0的数字")
                continue
            break
        except ValueError:
            print("请输入有效数字")

    print("\n选择风格:")
    print("1. 随机风格")
    print("2. 中文网名")
    print("3. 英文网名")
    print("4. 中英混合")
    print("5. 特殊符号")

    while True:
        choice = input("请选择风格(1-5): ")
        if choice in ['1', '2', '3', '4', '5']:
            style_map = {
                '1': 'random',
                '2': 'chinese',
                '3': 'english',
                '4': 'mixed',
                '5': 'special',
            }
            style = style_map[choice]
            break
        print("请输入1-5的数字")

    print(f"\n正在生成 {count} 个网名(最大长度: {12})...")
    print("-" * 30)

    nicknames = generate_nicknames(count, style, 12)
    for i, name in enumerate(nicknames, 1):
        print(f"{i}. {name}")


if __name__ == "__main__":
    main()
