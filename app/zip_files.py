import io
import zipfile


def build_zip(files: list[tuple[str, bytes]]) -> bytes:
    """Build a zip archive from a list of (filename, content) tuples."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        seen: dict[str, int] = {}
        for name, content in files:
            if name in seen:
                seen[name] += 1
                base, ext = name.rsplit(".", 1)
                unique_name = f"{base}_{seen[name]}.{ext}"
            else:
                seen[name] = 0
                unique_name = name
            zf.writestr(unique_name, content)
    return buf.getvalue()
