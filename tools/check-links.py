# -*- coding: utf-8 -*-
"""檢查 repo 內所有 markdown 的相對連結：目標檔在不在、`#` 錨點對不對得上標題。

錨點用的是 GitHub 的規則近似：轉小寫、去掉反引號與標點、空白換成連字號、
其餘文字（含漢字）保留。近似的地方在於 GitHub 對某些 Unicode 標點的處理，
所以「有問題」是強訊號、「沒問題」不是保證。

順帶會抓到一種容易漏的錯：markdown 把 `dir[77](一般檔案…)` 這種寫法渲染成連結。
這是真的踩過的坑，不是假想。

用法（照 CLAUDE.md 的 docker-only 規則）：
    docker run --rm --network none -u "$(id -u):$(id -g)" \
      -v "$PWD:/work:ro" -w /work python:3.13-alpine python tools/check-links.py
"""
import os
import re
import sys

SKIP_DIRS = {'.git', 'node_modules'}


def slug(heading):
    """把標題文字轉成 GitHub 風格的錨點"""
    out = []
    for ch in heading.strip().lower().replace('`', ''):
        if ch.isalnum() or ch == '_':
            out.append(ch)
        elif ch in ' \t-':
            out.append('-')
    return ''.join(out)


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith('.md'):
                yield os.path.join(dirpath, name)


def without_fences(path):
    """去掉 fenced code block。標題掃描用這個——行內程式碼要保留，
    因為 GitHub 產生錨點時只去掉反引號、內容照留。"""
    return re.sub(r'```.*?```', '', open(path, encoding='utf-8').read(), flags=re.S)


def body(path):
    """再去掉行內程式碼。連結掃描用這個——反引號裡的寫法不會被 markdown 當成連結，
    否則像 `dir[77](一般檔案…)` 這種示範會被誤報。"""
    return re.sub(r'`[^`\n]*`', '', without_fences(path))


def main(root='.'):
    root = os.path.abspath(root)
    headings = {}
    for path in walk(root):
        headings[os.path.normpath(path)] = {
            slug(m.group(2)) for m in re.finditer(r'^(#{1,6})\s+(.*)$', without_fences(path), re.M)
        }

    bad = 0
    for path in walk(root):
        rel = os.path.relpath(path, root)
        for m in re.finditer(r'\]\(([^)]+)\)', body(path)):
            target = m.group(1).strip()
            if not target or target.startswith(('http://', 'https://', 'mailto:')):
                continue
            filepart, _, anchor = target.partition('#')
            resolved = (os.path.normpath(os.path.join(os.path.dirname(path), filepart))
                        if filepart else os.path.normpath(path))
            if not os.path.exists(resolved):
                print(f'連結目標不存在  {rel} -> {target}')
                bad += 1
                continue
            if anchor and resolved in headings and anchor not in headings[resolved]:
                print(f'錨點對不上      {rel} -> {target}')
                print(f'                該檔的錨點：{sorted(headings[resolved])}')
                bad += 1

    print(f'{bad} 個問題')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
