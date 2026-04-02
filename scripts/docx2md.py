#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import gnureadline as readline  # 覆盖 libedit
except ImportError:
    pass

import os
import re
import argparse
import subprocess
from pathlib import Path
import datetime
from typing import (
    Union, List, Optional, Dict, overload, Callable, TypedDict
  )


MEDIA_OPTS   = ["电影", "电视剧", "网剧", "短视频", "网络电影", "中剧"]
CONTENT_OPTS = ["故事概要", "全剧大纲", "人物设定", "人物小传", "人物关系",
                 "分场大纲", "剧本", "项目介绍", "思考", "随笔", "小说", "其他"]
GENRE_OPTS   = ["爱情", "都市", "职场", "动作", "恐怖", "悬疑", "探案", "现实",
                 "古装", "穿越", "喜剧", "科幻", "奇幻", "武侠", "家庭", "历史"]


numeric_validator: Callable[[str], bool] = lambda s: (not s) or s.isdigit()


def get_file_number(filename: str) -> Optional[str]:
    """从文件名中提取数字编号"""
    m = re.search(r'(\d+)', filename)
    return m.group(1) if m else None


def get_file_creation_date(file_path: str) -> str:
    """获取文件的创建日期"""
    try:
        ts = os.stat(file_path).st_ctime
    except Exception:
        ts = datetime.datetime.now().timestamp()
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    

def _normalize(value: str, ci: bool) -> str:
    """根据是否大小写敏感统一处理"""
    return value.strip().lower() if ci else value.strip()


@overload
def get_interactive_input(
    prompt: str,
    default: Optional[str] = None,
    *,
    allow_empty: bool = True,
    options: Optional[list[str]] = None,
    is_multi: bool,
    strict_options: bool = False,
    case_insensitive: bool = False,
    return_none_if_empty: bool = False,
    validator: Callable[[str], bool] | None = None,
    validator_msg: str = "输入不合法！",    
) -> list[str]: ...
@overload
def get_interactive_input(
    prompt: str,
    default: Optional[str] = None,
    *,
    allow_empty: bool = True,
    options: Optional[list[str]] = None,
    is_multi: bool = False,
    strict_options: bool = False,
    case_insensitive: bool = False,
    return_none_if_empty: bool = False,
    validator: Callable[[str], bool] | None = None,
    validator_msg: str = "输入不合法！",    
) -> str: ...

def get_interactive_input(
    prompt: str,
    default: Optional[str] = None,
    *,
    allow_empty: bool = True,
    options: Optional[list[str]] = None,
    is_multi: bool = False,
    strict_options: bool = False,
    case_insensitive: bool = False,
    return_none_if_empty: bool = False,
    validator: Callable[[str], bool] | None = None,
    validator_msg: str = "输入不合法！",    
):
    """
    获取交互式输入，支持选项和多值

    Parameters:
        prompt (str): 提示信息
        default (str): 默认值
        allow_empty (bool): 是否允许空值
        options (list): 可选选项列表
        is_multi (bool): 是否为多值输入(逗号分隔)
        strict_options (bool): 是否严格限制输入必须在选项内

    Returns:
        Union[str, list[str]]: 如果是多值输入，返回字符串列表；否则返回单个字符串
    """
    options = options or []
    opt_str = "/".join(options) if options else ""

    if options and default is not None:
        prompt_fmt = f"{prompt} [{opt_str}] (默认:{default}) : "
    elif options:
        prompt_fmt = f"{prompt} [{opt_str}] : "
    elif default is not None:
        prompt_fmt = f"{prompt} (默认:{default}) : "
    else:
        prompt_fmt = f"{prompt} : "
    
    while True:
        raw = input(prompt_fmt)
        
        # 处理空输入
        if not raw.strip(): 
            if default is not None:
                raw = default
            elif allow_empty:
                return None if return_none_if_empty else ( [] if is_multi else "" )
            else:
                print("此项不能为空，请重新输入！")
                continue

        values = (
            [_normalize(v, case_insensitive) for v in raw.split(',')]
            if is_multi 
            else [_normalize(raw, case_insensitive)]
        )

        if options:
            norm_options = [_normalize(o, case_insensitive) for o in options]
            invalid_opts = [v for v in values if v not in norm_options]
            if invalid_opts and strict_options:
                print(f"输入不在选项列表：{', '.join(invalid_opts)}")
                continue

        if validator:
            invalid_vals = [v for v in values if not validator(v)]
            if invalid_vals:
                print(validator_msg)
                continue

        return values if is_multi else values[0]


class FMData(TypedDict, total=False):
    storyMarkdown: str
    title: str
    media_type: str
    content_type: str
    genre: List[str]
    season: str
    episode: str
    author: List[str]
    created_date: str
    version: str
    tags: List[str]


def prompt_common_front_matter(source_path: str) -> FMData:
    """询问一次公共字段（所有文件共享）"""
    while True:
        info: FMData = {}

        info['storyMarkdown'] = "1.0"
        info['title'] = get_interactive_input("标题", allow_empty=False)

        # 可选项
        info['media_type'] = get_interactive_input(
            "媒体类型",
            default="电影", 
            options=MEDIA_OPTS,
            )

        info['content_type'] = get_interactive_input(
            "内容类型",
            default="剧本", 
            allow_empty=False,
            options=CONTENT_OPTS,
            )

        info['genre'] = get_interactive_input(
            "类型（可多项，用逗号分隔）",
            options=GENRE_OPTS, 
            is_multi=True,
            )

        # 数字
        info['season'] = get_interactive_input(
            "季数", 
            validator=numeric_validator,
            validator_msg="季数必须是数字！",
        )
        info['episode'] = ""
        info['author'] = get_interactive_input("作者（可多项，用逗号分隔）", is_multi=True)
        info['created_date'] = get_file_creation_date(source_path)
        info['version'] = get_interactive_input("版本")
        info['tags'] = get_interactive_input("标签（可多项，用逗号分隔）", is_multi=True)

        print("\n=======  请确认以下公共信息（所有文件共享）  =======")
        for k, v in info.items():
            print(f"{k}: {v}")
        print("==============================================")
        if input("确认无误？(y/n) ").strip().lower() == 'y':
            return info
        print(">> 重新填写 ...\n")


def build_front_matter(data: FMData) -> str:
    """把 dict 转为 YAML front-matter 字符串"""
    fm_lines: list[str] = ['---']
    for k, v in data.items():
        if v:
            if isinstance(v, list):
                fm_lines.append(f"{k}:")
                for item in v:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{k}: {v if v is not None else ''}")
    fm_lines.append('---\n\n')
    return '\n'.join(fm_lines)


def convert_docx_to_md(
    source_folder: str,
    target_folder: str,
    *,
    prefix: str = "",
    suffix: str = "",
    overwrite: bool = False,
    # 新增参数，允许从命令行传入执行路径
    markitdown_path: Optional[str] = None
):
    """
    遍历 source_folder 下 *.docx 并转换
    OVERWRITE_STRATEGY:
    • overwrite=True  -> 直接覆盖
    • overwrite=False -> 目标存在时自动在文件名后追加时间戳
    """
    docx_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.docx')]

    # --- 新增: 智能路径检测与加载机制 ---
    import shutil
    has_api = False
    try:
        from markitdown import MarkItDown
        has_api = True
    except ImportError:
        pass

    cmd_bin = None
    if not has_api:
        # 优先级: 传入参数 -> 环境变量 -> 系统 PATH 搜索
        cmd_bin = markitdown_path or os.environ.get('MARKITDOWN_BIN') or shutil.which('markitdown')
        if not cmd_bin:
            print("❌ 错误: 未能在当前环境找到 markitdown 命令，并且缺少 markitdown Python 依赖。")
            print("建议: 1. pip install markitdown | 2. 设置环境变量 MARKITDOWN_BIN | 3. 使用 --markitdown-bin 参数")
            return
    # -----------------------------------
    if not docx_files:
        print("未找到 .docx 文件")
        return

    Path(target_folder).mkdir(parents=True, exist_ok=True)

    first_doc_path = os.path.join(source_folder, docx_files[0])
    common_info: FMData = prompt_common_front_matter(first_doc_path)

    counter = 1
    for doc in docx_files:
        file_num = get_file_number(doc) or f"{counter:02d}"
        counter += 1 if not get_file_number(doc) else 0

        dst_name = f"{prefix}{file_num}{suffix}.md"
        dst_path = os.path.join(target_folder, dst_name)

        if os.path.exists(dst_path) and not overwrite:
            base, ext = os.path.splitext(dst_path)
            ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            dst_path = f"{base}_{ts}{ext}"

        src_path = os.path.join(source_folder, doc)
        print(f"\n处理文件: {doc}")

        try:
            md_content = ""
            
            # --- 新增: 根据之前检测的状态决定执行方式 ---
            if has_api:
                md = MarkItDown()
                result = md.convert(src_path)
                md_content = result.text_content
            else:
                # 兼容旧版本的子进程方式，使用更安全的路径变量 cmd_bin
                assert cmd_bin is not None  # 避免类型检查器报错
                res = subprocess.run([cmd_bin, src_path], capture_output=True, text=True)
                if res.returncode != 0:
                    print("转换失败:", res.stderr)
                    continue
                md_content = res.stdout
            
            # --- 原代码(仅作注释不删除，方便 review) ---
            # res = subprocess.run(['markitdown', src_path],
            #                      capture_output=True, text=True)
            # if res.returncode != 0:
            #     print("转换失败:", res.stderr)
            #     continue
            # -----------------------------------------

            this_info = common_info.copy()
            this_info['episode'] = str(int(file_num))
            fm_text = build_front_matter(this_info)

            with open(dst_path, 'w', encoding='utf-8') as w:
                # --- 修改: 写入获取到的 md_content ---
                # 原代码: w.write(fm_text + res.stdout)
                w.write(fm_text + md_content)
                
            print("✔ 已输出 ->", dst_path)

        except FileNotFoundError:
            # 新增: 专门捕获 subprocess 找不到文件导致崩溃的异常
            print(f"❌ 错误: 找不到命令 {cmd_bin}。请检查 PATH 环境变量。")
            break
        except Exception as e:
            print("处理出错:", e)


def main():
    parser = argparse.ArgumentParser(
        description="将 DOCX 批量转换为 Markdown，并交互式生成 front-matter"
    )
    parser.add_argument('source', nargs='?', default=os.getcwd(),
                        help="源文件夹 (默认: 当前目录)")
    parser.add_argument('target', nargs='?', default=os.path.join(os.getcwd(), 'script'),
                        help="目标文件夹 (默认: ./script)")
    parser.add_argument('--prefix', default="E", help="生成文件名前缀")
    parser.add_argument('--suffix', default="", help="生成文件名后缀")
    parser.add_argument('-f', '--overwrite', action='store_true',
                        help="若目标文件已存在则覆盖 (默认追加时间戳)")
    
    # 新增: 命令行支持手动传入 markitdown 路径
    parser.add_argument('--markitdown-bin', default=None,
                        help="指定 markitdown 可执行文件的绝对路径")

    args = parser.parse_args()

    print("源目录 :", args.source)
    print("输出目录 :", args.target)
    
    # --- 原代码(仅作注释不删除) ---
    # convert_docx_to_md(args.source, args.target,
    #                    prefix=args.prefix,
    #                    suffix=args.suffix,
    #                    overwrite=args.overwrite)
    # -----------------------------
    
    # --- 修改: 传递新增参数 markitdown_path ---
    convert_docx_to_md(args.source, args.target,
                       prefix=args.prefix,
                       suffix=args.suffix,
                       overwrite=args.overwrite,
                       markitdown_path=args.markitdown_bin)
    
if __name__ == "__main__":
    main()
