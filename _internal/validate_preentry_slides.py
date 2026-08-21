from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(r"C:\Program Files\nodejs\node.exe")


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.images: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "img" and values.get("src"):
            self.images.append(values["src"] or "")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")


def main() -> int:
    failures: list[str] = []
    decks = sorted((ROOT / "入队前培训").glob("1.*/*演示文档.html"))
    if len(decks) != 7:
        failures.append(f"应有 7 份课件，实际 {len(decks)}")

    for path in decks:
        text = path.read_text(encoding="utf-8")
        content = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        label = path.parent.name
        parser = DeckParser()
        parser.feed(text)
        slides = len(re.findall(r'<section\b[^>]*class="[^"]*\bslide\b', content))
        supplements = len(
            re.findall(
                r'<section\b[^>]*class="[^"]*\bslide\b[^>]*>(?:(?!<section\b).)*?补充内容',
                content,
                re.S,
            )
        )
        recaps = len(re.findall(r"本次回顾", content))
        canvases = re.findall(r'<canvas[^>]*data-demo="([^"]+)"', text)
        definitions = set(re.findall(r"ARTINX_DEMOS\[['\"]([^'\"]+)['\"]\]", text))
        duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        missing_demos = sorted(set(canvases) - definitions)
        missing_images: list[str] = []
        remote_images = [src for src in parser.images if src.startswith(("http://", "https://"))]
        for src in parser.images:
            if src.startswith(("http://", "https://", "data:")):
                continue
            if not (path.parent / src).resolve().exists():
                missing_images.append(src)

        if not 18 <= slides <= 30:
            failures.append(f"{label}: 页数 {slides} 不在 18–30")
        if recaps:
            failures.append(f"{label}: 仍含 {recaps} 处本次回顾")
        if supplements != 1:
            failures.append(f"{label}: 补充页应为 1，实际 {supplements}")
        if len(canvases) < 2:
            failures.append(f"{label}: 交互演示少于 2 个")
        if missing_demos:
            failures.append(f"{label}: 未注册演示 {missing_demos}")
        if duplicate_ids:
            failures.append(f"{label}: 重复 ID {duplicate_ids}")
        if remote_images:
            failures.append(f"{label}: 存在远程图片 {remote_images}")
        if missing_images:
            failures.append(f"{label}: 图片不存在 {missing_images}")
        if len([href for href in parser.links if href.startswith("https://")]) < 3:
            failures.append(f"{label}: 官方延伸链接少于 3 个")

        script_source = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", script_source, re.S)
        for number, script in enumerate(scripts, 1):
            result = subprocess.run(
                [str(NODE), "--check"],
                input=script,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
            if result.returncode:
                failures.append(f"{label}: 脚本 {number} 语法错误：{result.stderr.strip()}")

        print(
            f"{label}: slides={slides}, demos={len(canvases)}, "
            f"supplement={supplements}, links={len(parser.links)}"
        )

    if failures:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("\nAll seven decks passed structural, asset, and JavaScript checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
