import re


def clean_text(text):
    # Remove trailing and leading spaces from each line
    text = "\n".join(line.strip() for line in text.splitlines())

    # Replace multiple blank lines (more than 2) with just one blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_markdown(md_text):
    # Remove navigation menu items (links in square brackets)
    md_text = re.sub(r"\[.*?\]\(.*?\)", "", md_text)

    # Remove excessive whitespace
    md_text = re.sub(r"\n\s*\n", "\n\n", md_text)

    # Preserve and format image links properly
    md_text = re.sub(r"!\[\]\((.*?)\)", r"![Image](\1)", md_text)

    # Remove broken image links and empty markdown elements
    md_text = re.sub(r"\!\[\]\(\)", "", md_text)

    # Remove repeated 'Close Menu' and other UI elements
    md_text = re.sub(r"Open Menu|Close Menu", "", md_text, flags=re.IGNORECASE)

    # Preserve section headers
    md_text = re.sub(r"##\s+", "## ", md_text)

    # Trim excessive newlines
    md_text = re.sub(r"\n{3,}", "\n\n", md_text)

    return md_text.strip()
