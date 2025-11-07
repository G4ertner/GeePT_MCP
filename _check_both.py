from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
print('new block index', text.find('- start_part_tree_job'))
print('old block index', text.find('- start_part_tree_job / start_stage_plan_job'))
