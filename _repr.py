from pathlib import Path
text = Path('mcp_server/krpc/tools.py').read_text(encoding='utf-8')
for i,c in enumerate(text):
    if text.startswith('    A', i-4 if i>=4 else 0):
        pass
