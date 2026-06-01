"""user-thoughts 共享工具函数。

所有脚本共用的目录查找、配置读写、维度验证等函数。
"""
import re
from pathlib import Path


def find_ustht() -> Path | None:
    """在当前目录或父目录中查找 .ustht/ 目录。"""
    cwd = Path.cwd()
    for d in [cwd, *cwd.parents]:
        ustht = d / ".ustht"
        if ustht.is_dir():
            return ustht
    return None


def find_skill_dir() -> Path | None:
    """查找 user-thoughts 技能目录（SKILL.md 所在目录）。"""
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    if (skill_dir / "SKILL.md").exists():
        return skill_dir
    return None


def read_define_ini(ustht: Path) -> dict:
    """读取 define.ini 并返回键值对。"""
    ini = ustht / "define.ini"
    if not ini.exists():
        return {}
    result = {}
    for line in ini.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def validate_define_ini(cfg: dict) -> str | None:
    """验证 define.ini 键值安全性。返回错误信息或 None。"""
    for k, v in cfg.items():
        if "\n" in v or "\r" in v:
            return f"{k} 值包含换行符"
        if "=" in v:
            return f"{k} 值包含 = 字符"
    if "SKILL_STATUS" in cfg and cfg["SKILL_STATUS"] not in ("on", "off", ""):
        return f"SKILL_STATUS 值非法：{cfg['SKILL_STATUS']}"
    if "INSTANT_STATUS" in cfg and cfg["INSTANT_STATUS"] not in ("on", "off", ""):
        return f"INSTANT_STATUS 值非法：{cfg['INSTANT_STATUS']}"
    if "LAST_SORTIN" in cfg and cfg["LAST_SORTIN"]:
        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", cfg["LAST_SORTIN"]):
            return f"LAST_SORTIN 格式非法：{cfg['LAST_SORTIN']}"
    return None


def write_define_ini(ustht: Path, cfg: dict):
    """整文件覆写 define.ini。值必须通过安全验证。"""
    err = validate_define_ini(cfg)
    if err:
        raise ValueError(f"define.ini 写入被拒绝：{err}")
    ini = ustht / "define.ini"
    lines = [f"{k}={v}" for k, v in cfg.items()]
    ini.write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_processed(filepath: Path) -> bool:
    """检查 raw 文件第一行是否为 processed 标记。"""
    first_line = filepath.read_text(encoding="utf-8").split("\n", 1)[0].strip()
    return first_line == "<!-- processed -->"


RESERVED_DIM_NAMES = {"backlog", "readme-ai", "export", "raw", "ignored", "define", "general"}


def validate_dim_name(dim: str) -> bool:
    """验证维度名：每段须匹配 [a-z0-9][a-z0-9-]*[a-z0-9] 或单字符 [a-z0-9]。

    拒绝 ..、\\ 等路径遍历字符。总长度不超过 64 字符（含 /）。
    不得与保留名冲突。
    """
    if len(dim) > 64:
        return False
    if dim in RESERVED_DIM_NAMES:
        return False
    for part in dim.split("/"):
        if not part or not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", part):
            return False
        if ".." in part or "\\" in part:
            return False
    return True
