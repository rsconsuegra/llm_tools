def extract_section(text: str, header: str) -> str:
    lines = text.split("\n")
    capturing = False
    result: list[str] = []

    for line in lines:
        if line.strip().startswith(f"## {header}"):
            capturing = True
            continue
        if capturing and line.strip().startswith("## "):
            break
        if capturing:
            result.append(line)

    return "\n".join(result).strip()


def extract_list(text: str, header: str) -> list[str]:
    section = extract_section(text, header)
    items = []
    for line in section.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            items.append(stripped[2:].strip())
        elif stripped and not stripped.startswith("#"):
            items.append(stripped)
    return items
