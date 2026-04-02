#!/bin/bash

src_dir="./"
dst_dir="../script"

mkdir -p "$dst_dir"

for docx_file in "$src_dir"*.docx; do
    [ -e "$docx_file" ] || continue  # 如果没有匹配文件，跳过

    base_name="$(basename -- "$docx_file" .docx)"
    target_file="$dst_dir/$base_name.md"

    if [ -f "$target_file" ]; then
        read -p "$target_file 已存在，是否覆盖？[y/N] " answer
        [[ ! "$answer" =~ ^[Yy]$ ]] && echo "跳过 $target_file" && continue
    fi

    markitdown "$docx_file" > "$target_file"
    echo "已导出 $target_file"

done
