from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
needle = '- start_part_tree_job / start_stage_plan_job'
print(text.index(needle))
