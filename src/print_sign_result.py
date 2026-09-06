# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

SIGN_RESULT_FILE = "sign_result.json"

TABLE_HEADERS = ("Account", "Token", "Coin Gain", "Total Coins", "Bind Changes")
TABLE_KEYS = ("account", "token", "coin_gain", "total_coin", "change_bind_num")
TOKEN_MAX_WIDTH = 36


def total_coin_value(item: Dict[str, Any]) -> int:
    value = item.get("total_coin", 0)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def display_width(text: str) -> int:
    width = 0
    for char in text:
        if ord(char) > 127:
            width += 2
        else:
            width += 1
    return width


def truncate_text(text: str, max_width: int) -> str:
    if display_width(text) <= max_width:
        return text

    result = []
    current_width = 0
    limit = max_width - 3
    for char in text:
        char_width = 2 if ord(char) > 127 else 1
        if current_width + char_width > limit:
            break
        result.append(char)
        current_width += char_width
    return "".join(result) + "..."


def pad_text(text: str, width: int) -> str:
    padding = width - display_width(text)
    if padding < 0:
        return truncate_text(text, width)
    return text + (" " * padding)


def format_cell(value: Any, max_width: Optional[int] = None) -> str:
    if value is None:
        text = ""
    else:
        text = str(value)
    if max_width is not None:
        text = truncate_text(text, max_width)
    return text


def build_table_rows(results: List[Dict[str, Any]]) -> List[List[str]]:
    rows = []
    for item in results:
        rows.append([
            format_cell(item.get("account", "")),
            format_cell(item.get("token", ""), TOKEN_MAX_WIDTH),
            format_cell(item.get("coin_gain", 0)),
            format_cell(item.get("total_coin", 0)),
            format_cell(item.get("change_bind_num", "")),
        ])
    return rows


def calc_column_widths(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[int]:
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], display_width(cell))
    return widths


def render_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = calc_column_widths(headers, rows)
    separator = "+".join("-" * (width + 2) for width in widths)
    border_top = "+" + separator + "+"

    def render_row(cells: Sequence[str]) -> str:
        padded_cells = [pad_text(cell, widths[index]) for index, cell in enumerate(cells)]
        return "| " + " | ".join(padded_cells) + " |"

    lines = [border_top, render_row(headers), border_top]
    for row in rows:
        lines.append(render_row(row))
    lines.append(border_top)
    return "\n".join(lines)


def load_sign_results(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError("签到结果文件不存在: {}".format(file_path))

    with open(file_path, "r", encoding="utf-8-sig") as file_obj:
        data = json.load(file_obj)

    if not isinstance(data, list):
        raise ValueError("签到结果文件格式错误，根节点必须是数组")

    return data


def print_sign_result_table(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("签到结果为空")
        return

    sorted_results = sorted(results, key=total_coin_value, reverse=True)
    rows = build_table_rows(sorted_results)
    print(render_table(TABLE_HEADERS, rows))

    total_coin_gain = 0
    total_coin_all = 0
    for item in results:
        coin_gain = item.get("coin_gain", 0)
        total_coin = item.get("total_coin", 0)
        if isinstance(coin_gain, int):
            total_coin_gain += coin_gain
        else:
            try:
                total_coin_gain += int(coin_gain)
            except (TypeError, ValueError):
                pass
        if isinstance(total_coin, int):
            total_coin_all += total_coin
        else:
            try:
                total_coin_all += int(total_coin)
            except (TypeError, ValueError):
                pass

    print("")
    print("共 {} 个账号，本次合计获得金币: {}，所有账号总金币: {}".format(len(results), total_coin_gain, total_coin_all))


def resolve_file_path(custom_path: Optional[str]) -> str:
    if custom_path:
        return os.path.abspath(custom_path)
    return os.path.join(os.getcwd(), SIGN_RESULT_FILE)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="读取签到结果 JSON 并以表格形式打印到控制台")
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="签到结果文件路径，默认读取当前目录下的 {}".format(SIGN_RESULT_FILE),
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    file_path = resolve_file_path(args.file)

    try:
        results = load_sign_results(file_path)
        print_sign_result_table(results)
        return 0
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print("[-] {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
