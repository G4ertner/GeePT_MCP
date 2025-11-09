# MCP Server Reorganization Plan

## Target Layout Overview



## Execution Steps

1. **Entry consolidation** ✅  
   - Merge  and  into the new  entry point.  
   - Update CLI references (pyproject, docs) to import from the new location.

2. **kRPC utility relocation** ✅  
   - Move the current  package into .  
   - Adjust imports across the codebase and tests/manual scripts.

3. **Executor tooling split** ✅  
   - Create  (decorated wrappers) and an  package for the implementation (,  helpers, etc.).  
   - Ensure job-related resources keep working (update tests/docs).

4. **Library tooling split** ✅  
   - Introduce  as the public surface for docs/wiki/snippet tools.  
   - Move existing logic into  modules and update imports.

5. **Playbook resource refactor** ✅  
   - Create  to register resources.  
   - Keep markdown files in  and ensure resource URIs point to the new paths.

6. **General tools grouping** ✅  
   - Add  with logically grouped sections matching the README categories.  
   - Move supporting code into  submodules and have the head file expose the tool decorators.

7. **Helper utilities sweep** ✅  
   - Populate  and  with shared math/formatting helpers extracted during steps 3–6.  
   - Remove duplicate helpers and update imports accordingly.

8. **Documentation & tests update** ✅  
   - Refresh README, docs, and CI references to the new structure.  
   - Update  and other scripts to import from the reorganized modules.
