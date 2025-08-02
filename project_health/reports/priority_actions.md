## Priority Actions

These high-priority issues should be addressed first:

### 1. Module Structure: Missing pyproject.toml in GopiAI-CrewAI

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI
**Recommendation:** Add pyproject.toml file for proper Python package configuration

### 2. Complexity: Function 'main' has high complexity (19)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py
**Line:** 12
**Recommendation:** Consider refactoring 'main' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 3. Complexity: Function '_check_naming_consistency' has high complexity (17)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 504
**Recommendation:** Consider refactoring '_check_naming_consistency' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 4. Complexity: Function '_find_unreferenced_modules' has high complexity (24)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py
**Line:** 264
**Recommendation:** Consider refactoring '_find_unreferenced_modules' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 5. Complexity: Function '_parse_requirements_txt' has high complexity (15)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 155
**Recommendation:** Consider refactoring '_parse_requirements_txt' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 6. Complexity: Function '_analyze_docstring_coverage' has high complexity (18)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 325
**Recommendation:** Consider refactoring '_analyze_docstring_coverage' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 7. Complexity: Function '_analyze_documentation_consistency' has high complexity (15)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 452
**Recommendation:** Consider refactoring '_analyze_documentation_consistency' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 8. Complexity: Function 'patch_crewai_client_for_debug' has high complexity (15)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py
**Line:** 71
**Recommendation:** Consider refactoring 'patch_crewai_client_for_debug' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 9. Complexity: Function 'get_project_files' has high complexity (15)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py
**Line:** 209
**Recommendation:** Consider refactoring 'get_project_files' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 10. Complexity: Function 'generate_markdown_report' has high complexity (17)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py
**Line:** 201
**Recommendation:** Consider refactoring 'generate_markdown_report' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 11. Complexity: Function 'generate_html_report' has high complexity (17)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py
**Line:** 340
**Recommendation:** Consider refactoring 'generate_html_report' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 12. Complexity: Function 'analyze' has high complexity (18)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py
**Line:** 105
**Recommendation:** Consider refactoring 'analyze' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 13. Complexity: Function 'generate_report' has high complexity (17)

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py
**Line:** 24
**Recommendation:** Consider refactoring 'generate_report' to reduce complexity. Break it into smaller functions or simplify conditional logic.

### 14. Temporary Files: Temporary file detected: empty_template_renv.lock

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\crewai_env\Lib\site-packages\pre_commit\resources\empty_template_renv.lock
**Recommendation:** Review file contents before deleting

### 15. Temporary Files: Temporary file detected: empty_template_renv.lock

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\gopiai_env\Lib\site-packages\pre_commit\resources\empty_template_renv.lock
**Recommendation:** Review file contents before deleting

### 16. Duplicate Files: Duplicate file content detected: __init__.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-App\gopiai\__init__.py
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\__init__.py

### 17. Duplicate Files: Duplicate file content detected: __init__.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Core\gopiai\__init__.py
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\__init__.py

### 18. Duplicate Files: Duplicate file content detected: __init__.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions\gopiai\__init__.py
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\__init__.py

### 19. Duplicate Files: Duplicate file content detected: __init__.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Widgets\gopiai\__init__.py
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\__init__.py

### 20. Duplicate Files: Duplicate file content detected: top_level.txt

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-App\gopiai_app.egg-info\top_level.txt
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai_ui.egg-info\top_level.txt

### 21. Duplicate Files: Duplicate file content detected: top_level.txt

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Core\gopiai_core.egg-info\top_level.txt
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai_ui.egg-info\top_level.txt

### 22. Duplicate Files: Duplicate file content detected: top_level.txt

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions\gopiai_extensions.egg-info\top_level.txt
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai_ui.egg-info\top_level.txt

### 23. Duplicate Files: Duplicate file content detected: top_level.txt

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Widgets\gopiai_widgets.egg-info\top_level.txt
**Recommendation:** Consider removing duplicate. Original file: C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai_ui.egg-info\top_level.txt

### 24. Version Conflict: Version conflict for pyside6: >=6.5.0, ==6.7.3 in files: GopiAI-Extensions\pyproject.toml, GopiAI-Core\pyproject.toml, GopiAI-Assets\pyproject.toml, GopiAI-UI\pyproject.toml, requirements.txt, GopiAI-App\pyproject.toml, GopiAI-Widgets\pyproject.toml

**Severity:** HIGH
**File:** GopiAI-Extensions\pyproject.toml, GopiAI-Core\pyproject.toml, GopiAI-Assets\pyproject.toml, GopiAI-UI\pyproject.toml, requirements.txt, GopiAI-App\pyproject.toml, GopiAI-Widgets\pyproject.toml
**Recommendation:** Standardize version specification for pyside6 across all dependency files

### 25. Version Conflict: Version conflict for txtai: >=8.2.0, >=8.6.0 in files: requirements.txt, GopiAI-UI\pyproject.toml

**Severity:** HIGH
**File:** requirements.txt, GopiAI-UI\pyproject.toml
**Recommendation:** Standardize version specification for txtai across all dependency files

### 26. Version Conflict: Version conflict for sentence-transformers: >=2.7.0, >=5.0.0 in files: requirements.txt, GopiAI-UI\pyproject.toml

**Severity:** HIGH
**File:** requirements.txt, GopiAI-UI\pyproject.toml
**Recommendation:** Standardize version specification for sentence-transformers across all dependency files

### 27. Version Conflict: Version conflict for pytest: >=7.0.0, !=7.1.0,>=5.2.0, >=7.3.2, >=8.0.2 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt, GopiAI-UI\pyproject.toml, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt, GopiAI-UI\pyproject.toml, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt
**Recommendation:** Standardize version specification for pytest across all dependency files

### 28. Version Conflict: Version conflict for pytest-qt: >=4.2.0, >=4.0.0 in files: requirements.txt, GopiAI-UI\pyproject.toml

**Severity:** HIGH
**File:** requirements.txt, GopiAI-UI\pyproject.toml
**Recommendation:** Standardize version specification for pytest-qt across all dependency files

### 29. Version Conflict: Version conflict for black: ==22.3.0, >=22.0.0 in files: txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, GopiAI-UI\pyproject.toml

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, GopiAI-UI\pyproject.toml
**Recommendation:** Standardize version specification for black across all dependency files

### 30. Version Conflict: Version conflict for isort: >=5.10.0, <6.0,>=5.0 in files: txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, GopiAI-UI\pyproject.toml

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, GopiAI-UI\pyproject.toml
**Recommendation:** Standardize version specification for isort across all dependency files

### 31. Version Conflict: Version conflict for crewai: >=0.148.0, <1.0.0,>=0.130.0, <1.0.0,>=0.148.0, >=0.141.0, <1.0.0,>=0.141.0 in files: gopiai_env\Lib\site-packages\crewai\cli\templates\tool\pyproject.toml, gopiai_env\Lib\site-packages\crewai\cli\templates\flow\pyproject.toml, GopiAI-CrewAI\gopiai\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\crewai\cli\templates\tool\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\crewai\cli\templates\flow\pyproject.toml

**Severity:** HIGH
**File:** gopiai_env\Lib\site-packages\crewai\cli\templates\tool\pyproject.toml, gopiai_env\Lib\site-packages\crewai\cli\templates\flow\pyproject.toml, GopiAI-CrewAI\gopiai\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\crewai\cli\templates\tool\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\crewai\cli\templates\flow\pyproject.toml
**Recommendation:** Standardize version specification for crewai across all dependency files

### 32. Version Conflict: Version conflict for numpy: >=1.22.4, >=1.26.4, >=1.26.0, >=1.23.2, <3.0.0,>=2.0.0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt
**Recommendation:** Standardize version specification for numpy across all dependency files

### 33. Version Conflict: Version conflict for python-dateutil: >=2.8.2, >=2.8.0, >=2.9.0.post0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for python-dateutil across all dependency files

### 34. Version Conflict: Version conflict for hypothesis: >=6.46.1, <7.0.0,>=3.27.0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt
**Recommendation:** Standardize version specification for hypothesis across all dependency files

### 35. Version Conflict: Version conflict for scipy: >=1.10.0, >=1.13.0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt
**Recommendation:** Standardize version specification for scipy across all dependency files

### 36. Version Conflict: Version conflict for beautifulsoup4: >=4.11.0, >=4.12.3, >=4.11.2 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for beautifulsoup4 across all dependency files

### 37. Version Conflict: Version conflict for lxml: >=4.9.0, >=4.9.2, >=5.1.0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\pandas\pyproject.toml, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for lxml across all dependency files

### 38. Version Conflict: Version conflict for requests: >=2.28.0, <3.0.0,>=2.13.0, >=2.32.3 in files: txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for requests across all dependency files

### 39. Version Conflict: Version conflict for fastapi: ==0.104.0, >=0.110.0 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\modal.com\requirements.txt, requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\modal.com\requirements.txt, requirements.txt
**Recommendation:** Standardize version specification for fastapi across all dependency files

### 40. Version Conflict: Version conflict for uvicorn: ==0.23.2, >=0.27.1 in files: GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\modal.com\requirements.txt, requirements.txt

**Severity:** HIGH
**File:** GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\fly.io\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\render.com\requirements.txt, GopiAI-CrewAI\crewai_env\Lib\site-packages\embedchain\deployment\modal.com\requirements.txt, requirements.txt
**Recommendation:** Standardize version specification for uvicorn across all dependency files

### 41. Version Conflict: Version conflict for selenium: >=4.17.2, >=4.15.0 in files: requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for selenium across all dependency files

### 42. Version Conflict: Version conflict for playwright: >=1.40.0, >=1.41.2 in files: requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt

**Severity:** HIGH
**File:** requirements.txt, GopiAI-CrewAI\tools\gopiai_integration\browser_requirements.txt
**Recommendation:** Standardize version specification for playwright across all dependency files

### 43. Version Conflict: Version conflict for tqdm: <5.0.0,>=4.38.0, >=4.66.2 in files: txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt
**Recommendation:** Standardize version specification for tqdm across all dependency files

### 44. Version Conflict: Version conflict for packaging: >=20.0, >=23.2 in files: txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt, requirements.txt
**Recommendation:** Standardize version specification for packaging across all dependency files

### 45. Outdated Dependency: Outdated dependency: thinc 8.3.6 (latest: 9.1.1)

**Severity:** HIGH
**File:** txtai_env\Lib\site-packages\spacy\tests\package\requirements.txt, gopiai_env\Lib\site-packages\spacy\tests\package\requirements.txt
**Recommendation:** Consider updating thinc to version 9.1.1

### 46. Exact Duplicate: Exact duplicate block found in 4 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py:28, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py:34, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py:40, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py:47

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py
**Line:** 28
**Recommendation:** Extract duplicate block into a shared utility function or module

### 47. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py:36, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py:70, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py:139

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 36
**Recommendation:** Extract duplicate block into a shared utility function or module

### 48. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:124, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py:80, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py:93

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 124
**Recommendation:** Extract duplicate block into a shared utility function or module

### 49. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:409, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:615

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 409
**Recommendation:** Extract duplicate function into a shared utility function or module

### 50. Exact Duplicate: Exact duplicate block found in 6 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:697, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py:655, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py:524, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py:662, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py:685, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py:533

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 697
**Recommendation:** Extract duplicate block into a shared utility function or module

### 51. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:702, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py:667, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py:690

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 702
**Recommendation:** Extract duplicate block into a shared utility function or module

### 52. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py:704, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py:669, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py:692

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 704
**Recommendation:** Extract duplicate block into a shared utility function or module

### 53. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:189, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:189

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 189
**Recommendation:** Extract duplicate function into a shared utility function or module

### 54. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:200, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py:37, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:200

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 200
**Recommendation:** Extract duplicate block into a shared utility function or module

### 55. Exact Duplicate: Exact duplicate block found in 3 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:210, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py:47, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:210

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 210
**Recommendation:** Extract duplicate block into a shared utility function or module

### 56. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:227, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:227

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 227
**Recommendation:** Extract duplicate function into a shared utility function or module

### 57. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:262, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:262

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 262
**Recommendation:** Extract duplicate function into a shared utility function or module

### 58. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:273, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:273

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 273
**Recommendation:** Extract duplicate block into a shared utility function or module

### 59. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:291, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:291

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 291
**Recommendation:** Extract duplicate block into a shared utility function or module

### 60. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:302, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:302

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 302
**Recommendation:** Extract duplicate function into a shared utility function or module

### 61. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:320, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:320

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 320
**Recommendation:** Extract duplicate block into a shared utility function or module

### 62. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:332, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:332

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 332
**Recommendation:** Extract duplicate block into a shared utility function or module

### 63. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:343, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:343

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 343
**Recommendation:** Extract duplicate function into a shared utility function or module

### 64. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py:360, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py:360

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 360
**Recommendation:** Extract duplicate block into a shared utility function or module

### 65. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py:80, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py:123

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py
**Line:** 80
**Recommendation:** Extract duplicate block into a shared utility function or module

### 66. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py:37, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py:56

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 37
**Recommendation:** Extract duplicate block into a shared utility function or module

### 67. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py:41, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py:60

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 41
**Recommendation:** Extract duplicate block into a shared utility function or module

### 68. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py:42, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py:61

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 42
**Recommendation:** Extract duplicate block into a shared utility function or module

### 69. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py:46, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py:65

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 46
**Recommendation:** Extract duplicate block into a shared utility function or module

### 70. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py:52, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py:71

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 52
**Recommendation:** Extract duplicate block into a shared utility function or module

### 71. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py:127, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py:174

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py
**Line:** 127
**Recommendation:** Extract duplicate block into a shared utility function or module

### 72. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py:136, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py:183

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py
**Line:** 136
**Recommendation:** Extract duplicate block into a shared utility function or module

### 73. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py:60, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py:84

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py
**Line:** 60
**Recommendation:** Extract duplicate block into a shared utility function or module

### 74. Exact Duplicate: Exact duplicate block found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py:61, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py:85

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py
**Line:** 61
**Recommendation:** Extract duplicate block into a shared utility function or module

### 75. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py:36, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py:146

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py
**Line:** 36
**Recommendation:** Extract duplicate function into a shared utility function or module

### 76. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:24, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:24

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 24
**Recommendation:** Extract duplicate function into a shared utility function or module

### 77. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:39, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:39

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 39
**Recommendation:** Extract duplicate function into a shared utility function or module

### 78. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:97, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:67

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 97
**Recommendation:** Extract duplicate function into a shared utility function or module

### 79. Exact Duplicate: Exact duplicate function found in 4 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:102, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:164, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:72, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:114

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 102
**Recommendation:** Extract duplicate function into a shared utility function or module

### 80. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:107, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:77

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 107
**Recommendation:** Extract duplicate function into a shared utility function or module

### 81. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:114, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:84

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 114
**Recommendation:** Extract duplicate function into a shared utility function or module

### 82. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:124, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:94

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 124
**Recommendation:** Extract duplicate function into a shared utility function or module

### 83. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:158, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:108

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 158
**Recommendation:** Extract duplicate function into a shared utility function or module

### 84. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:169, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:119

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 169
**Recommendation:** Extract duplicate function into a shared utility function or module

### 85. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:177, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:127

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 177
**Recommendation:** Extract duplicate function into a shared utility function or module

### 86. Exact Duplicate: Exact duplicate function found in 2 locations: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py:268, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py:187

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 268
**Recommendation:** Extract duplicate function into a shared utility function or module

### 87. Global Variable Conflict: Global variable 'backup_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 17
**Recommendation:** Consider using a centralized state manager or passing 'backup_path' as a parameter instead of using global variables

### 88. Global Variable Conflict: Global variable 'file_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fix_encoding.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 17
**Recommendation:** Consider using a centralized state manager or passing 'file_path' as a parameter instead of using global variables

### 89. Global Variable Conflict: Global variable 'logger' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 20
**Recommendation:** Consider using a centralized state manager or passing 'logger' as a parameter instead of using global variables

### 90. Global Variable Conflict: Global variable 'f' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fix_encoding.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 30
**Recommendation:** Consider using a centralized state manager or passing 'f' as a parameter instead of using global variables

### 91. Global Variable Conflict: Global variable 'content' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fix_encoding.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 31
**Recommendation:** Consider using a centralized state manager or passing 'content' as a parameter instead of using global variables

### 92. Global Variable Conflict: Global variable 'pattern' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fix_encoding.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 34
**Recommendation:** Consider using a centralized state manager or passing 'pattern' as a parameter instead of using global variables

### 93. Global Variable Conflict: Global variable 'new_content' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fix_encoding.py, C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\apply_memory_fix.py
**Line:** 66
**Recommendation:** Consider using a centralized state manager or passing 'new_content' as a parameter instead of using global variables

### 94. Global Variable Conflict: Global variable 'result' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py
**Line:** 45
**Recommendation:** Consider using a centralized state manager or passing 'result' as a parameter instead of using global variables

### 95. Global Variable Conflict: Global variable 'config' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py
**Line:** 86
**Recommendation:** Consider using a centralized state manager or passing 'config' as a parameter instead of using global variables

### 96. Global Variable Conflict: Global variable 'log_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\fix_chat_issues.py
**Line:** 120
**Recommendation:** Consider using a centralized state manager or passing 'log_file' as a parameter instead of using global variables

### 97. Global Variable Conflict: Global variable 'files_to_restore' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py
**Line:** 153
**Recommendation:** Consider using a centralized state manager or passing 'files_to_restore' as a parameter instead of using global variables

### 98. Global Variable Conflict: Global variable 'success_count' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\add_rag_logging.py
**Line:** 179
**Recommendation:** Consider using a centralized state manager or passing 'success_count' as a parameter instead of using global variables

### 99. Global Variable Conflict: Global variable 'hash' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 34
**Recommendation:** Consider using a centralized state manager or passing 'hash' as a parameter instead of using global variables

### 100. Global Variable Conflict: Global variable 'mtime' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 35
**Recommendation:** Consider using a centralized state manager or passing 'mtime' as a parameter instead of using global variables

### 101. Global Variable Conflict: Global variable 'size' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 36
**Recommendation:** Consider using a centralized state manager or passing 'size' as a parameter instead of using global variables

### 102. Global Variable Conflict: Global variable 'last_accessed' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 38
**Recommendation:** Consider using a centralized state manager or passing 'last_accessed' as a parameter instead of using global variables

### 103. Global Variable Conflict: Global variable 'stat' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 106
**Recommendation:** Consider using a centralized state manager or passing 'stat' as a parameter instead of using global variables

### 104. Global Variable Conflict: Global variable 'cache_entry' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 112
**Recommendation:** Consider using a centralized state manager or passing 'cache_entry' as a parameter instead of using global variables

### 105. Global Variable Conflict: Global variable 'file_hash' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 125
**Recommendation:** Consider using a centralized state manager or passing 'file_hash' as a parameter instead of using global variables

### 106. Global Variable Conflict: Global variable 'tree' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 176
**Recommendation:** Consider using a centralized state manager or passing 'tree' as a parameter instead of using global variables

### 107. Global Variable Conflict: Global variable 'cache_key' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 206
**Recommendation:** Consider using a centralized state manager or passing 'cache_key' as a parameter instead of using global variables

### 108. Global Variable Conflict: Global variable 'analyzer_name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 206
**Recommendation:** Consider using a centralized state manager or passing 'analyzer_name' as a parameter instead of using global variables

### 109. Global Variable Conflict: Global variable 'hit' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 210
**Recommendation:** Consider using a centralized state manager or passing 'hit' as a parameter instead of using global variables

### 110. Global Variable Conflict: Global variable 'cached_result' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 214
**Recommendation:** Consider using a centralized state manager or passing 'cached_result' as a parameter instead of using global variables

### 111. Global Variable Conflict: Global variable 'results' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 243
**Recommendation:** Consider using a centralized state manager or passing 'results' as a parameter instead of using global variables

### 112. Global Variable Conflict: Global variable 'cache_data' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 258
**Recommendation:** Consider using a centralized state manager or passing 'cache_data' as a parameter instead of using global variables

### 113. Global Variable Conflict: Global variable 'path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 263
**Recommendation:** Consider using a centralized state manager or passing 'path' as a parameter instead of using global variables

### 114. Global Variable Conflict: Global variable 'entry' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 263
**Recommendation:** Consider using a centralized state manager or passing 'entry' as a parameter instead of using global variables

### 115. Global Variable Conflict: Global variable 'sorted_entries' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 312
**Recommendation:** Consider using a centralized state manager or passing 'sorted_entries' as a parameter instead of using global variables

### 116. Global Variable Conflict: Global variable 'removed' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 317
**Recommendation:** Consider using a centralized state manager or passing 'removed' as a parameter instead of using global variables

### 117. Global Variable Conflict: Global variable 'project_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 376
**Recommendation:** Consider using a centralized state manager or passing 'project_path' as a parameter instead of using global variables

### 118. Global Variable Conflict: Global variable 'changed' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 439
**Recommendation:** Consider using a centralized state manager or passing 'changed' as a parameter instead of using global variables

### 119. Global Variable Conflict: Global variable 'file_info' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 456
**Recommendation:** Consider using a centralized state manager or passing 'file_info' as a parameter instead of using global variables

### 120. Global Variable Conflict: Global variable 'process' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 564
**Recommendation:** Consider using a centralized state manager or passing 'process' as a parameter instead of using global variables

### 121. Global Variable Conflict: Global variable 'memory_info' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 565
**Recommendation:** Consider using a centralized state manager or passing 'memory_info' as a parameter instead of using global variables

### 122. Global Variable Conflict: Global variable 'usage_percent' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 574
**Recommendation:** Consider using a centralized state manager or passing 'usage_percent' as a parameter instead of using global variables

### 123. Global Variable Conflict: Global variable 'exceeds_threshold' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyzer_cache.py
**Line:** 580
**Recommendation:** Consider using a centralized state manager or passing 'exceeds_threshold' as a parameter instead of using global variables

### 124. Global Variable Conflict: Global variable 'current_dir' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 29
**Recommendation:** Consider using a centralized state manager or passing 'current_dir' as a parameter instead of using global variables

### 125. Global Variable Conflict: Global variable 'parent_dir' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 33
**Recommendation:** Consider using a centralized state manager or passing 'parent_dir' as a parameter instead of using global variables

### 126. Global Variable Conflict: Global variable 'reports_dir' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 89
**Recommendation:** Consider using a centralized state manager or passing 'reports_dir' as a parameter instead of using global variables

### 127. Global Variable Conflict: Global variable 'timestamp' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 93
**Recommendation:** Consider using a centralized state manager or passing 'timestamp' as a parameter instead of using global variables

### 128. Global Variable Conflict: Global variable 'output_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 94
**Recommendation:** Consider using a centralized state manager or passing 'output_path' as a parameter instead of using global variables

### 129. Global Variable Conflict: Global variable 'analyzer' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 97
**Recommendation:** Consider using a centralized state manager or passing 'analyzer' as a parameter instead of using global variables

### 130. Global Variable Conflict: Global variable 'start_time' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 100
**Recommendation:** Consider using a centralized state manager or passing 'start_time' as a parameter instead of using global variables

### 131. Global Variable Conflict: Global variable 'report_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 105
**Recommendation:** Consider using a centralized state manager or passing 'report_path' as a parameter instead of using global variables

### 132. Global Variable Conflict: Global variable 'elapsed' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 108
**Recommendation:** Consider using a centralized state manager or passing 'elapsed' as a parameter instead of using global variables

### 133. Global Variable Conflict: Global variable 'line' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\chat_logger.py
**Line:** 7
**Recommendation:** Consider using a centralized state manager or passing 'line' as a parameter instead of using global variables

### 134. Global Variable Conflict: Global variable 'file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\check_serena_tools.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\check_serena_tools.py
**Line:** 41
**Recommendation:** Consider using a centralized state manager or passing 'file' as a parameter instead of using global variables

### 135. Global Variable Conflict: Global variable 'response' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\example_rag_usage.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 15
**Recommendation:** Consider using a centralized state manager or passing 'response' as a parameter instead of using global variables

### 136. Global Variable Conflict: Global variable 'message' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 15
**Recommendation:** Consider using a centralized state manager or passing 'message' as a parameter instead of using global variables

### 137. Global Variable Conflict: Global variable 'root' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 23
**Recommendation:** Consider using a centralized state manager or passing 'root' as a parameter instead of using global variables

### 138. Global Variable Conflict: Global variable 'dirs' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 23
**Recommendation:** Consider using a centralized state manager or passing 'dirs' as a parameter instead of using global variables

### 139. Global Variable Conflict: Global variable 'files' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 23
**Recommendation:** Consider using a centralized state manager or passing 'files' as a parameter instead of using global variables

### 140. Global Variable Conflict: Global variable 'ext' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 55
**Recommendation:** Consider using a centralized state manager or passing 'ext' as a parameter instead of using global variables

### 141. Global Variable Conflict: Global variable 'dir_name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 88
**Recommendation:** Consider using a centralized state manager or passing 'dir_name' as a parameter instead of using global variables

### 142. Global Variable Conflict: Global variable 'log_files' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 118
**Recommendation:** Consider using a centralized state manager or passing 'log_files' as a parameter instead of using global variables

### 143. Global Variable Conflict: Global variable 'parser' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 152
**Recommendation:** Consider using a centralized state manager or passing 'parser' as a parameter instead of using global variables

### 144. Global Variable Conflict: Global variable 'args' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\clean_project.py
**Line:** 161
**Recommendation:** Consider using a centralized state manager or passing 'args' as a parameter instead of using global variables

### 145. Global Variable Conflict: Global variable 'name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 24
**Recommendation:** Consider using a centralized state manager or passing 'name' as a parameter instead of using global variables

### 146. Global Variable Conflict: Global variable 'complexity' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 25
**Recommendation:** Consider using a centralized state manager or passing 'complexity' as a parameter instead of using global variables

### 147. Global Variable Conflict: Global variable 'line_number' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 26
**Recommendation:** Consider using a centralized state manager or passing 'line_number' as a parameter instead of using global variables

### 148. Global Variable Conflict: Global variable 'type' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 28
**Recommendation:** Consider using a centralized state manager or passing 'type' as a parameter instead of using global variables

### 149. Global Variable Conflict: Global variable 'issue_type' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 37
**Recommendation:** Consider using a centralized state manager or passing 'issue_type' as a parameter instead of using global variables

### 150. Global Variable Conflict: Global variable 'description' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 38
**Recommendation:** Consider using a centralized state manager or passing 'description' as a parameter instead of using global variables

### 151. Global Variable Conflict: Global variable 'severity' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 39
**Recommendation:** Consider using a centralized state manager or passing 'severity' as a parameter instead of using global variables

### 152. Global Variable Conflict: Global variable 'node' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 52
**Recommendation:** Consider using a centralized state manager or passing 'node' as a parameter instead of using global variables

### 153. Global Variable Conflict: Global variable 'child' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 70
**Recommendation:** Consider using a centralized state manager or passing 'child' as a parameter instead of using global variables

### 154. Global Variable Conflict: Global variable 'issues' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 102
**Recommendation:** Consider using a centralized state manager or passing 'issues' as a parameter instead of using global variables

### 155. Global Variable Conflict: Global variable 'lines' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 106
**Recommendation:** Consider using a centralized state manager or passing 'lines' as a parameter instead of using global variables

### 156. Global Variable Conflict: Global variable 'line_num' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 109
**Recommendation:** Consider using a centralized state manager or passing 'line_num' as a parameter instead of using global variables

### 157. Global Variable Conflict: Global variable 'start_line' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 188
**Recommendation:** Consider using a centralized state manager or passing 'start_line' as a parameter instead of using global variables

### 158. Global Variable Conflict: Global variable 'i' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\example_rag_usage.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 189
**Recommendation:** Consider using a centralized state manager or passing 'i' as a parameter instead of using global variables

### 159. Global Variable Conflict: Global variable 'python_files' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 276
**Recommendation:** Consider using a centralized state manager or passing 'python_files' as a parameter instead of using global variables

### 160. Global Variable Conflict: Global variable 'error' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 298
**Recommendation:** Consider using a centralized state manager or passing 'error' as a parameter instead of using global variables

### 161. Global Variable Conflict: Global variable 'visitor' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 321
**Recommendation:** Consider using a centralized state manager or passing 'visitor' as a parameter instead of using global variables

### 162. Global Variable Conflict: Global variable 'func_name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 325
**Recommendation:** Consider using a centralized state manager or passing 'func_name' as a parameter instead of using global variables

### 163. Global Variable Conflict: Global variable 'issue' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 388
**Recommendation:** Consider using a centralized state manager or passing 'issue' as a parameter instead of using global variables

### 164. Global Variable Conflict: Global variable 'parts' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 419
**Recommendation:** Consider using a centralized state manager or passing 'parts' as a parameter instead of using global variables

### 165. Global Variable Conflict: Global variable 'module_name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 420
**Recommendation:** Consider using a centralized state manager or passing 'module_name' as a parameter instead of using global variables

### 166. Global Variable Conflict: Global variable 'part' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 422
**Recommendation:** Consider using a centralized state manager or passing 'part' as a parameter instead of using global variables

### 167. Global Variable Conflict: Global variable 'import_patterns' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 452
**Recommendation:** Consider using a centralized state manager or passing 'import_patterns' as a parameter instead of using global variables

### 168. Global Variable Conflict: Global variable 'alias' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 471
**Recommendation:** Consider using a centralized state manager or passing 'alias' as a parameter instead of using global variables

### 169. Global Variable Conflict: Global variable 'p' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 602
**Recommendation:** Consider using a centralized state manager or passing 'p' as a parameter instead of using global variables

### 170. Global Variable Conflict: Global variable 'cmd' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 632
**Recommendation:** Consider using a centralized state manager or passing 'cmd' as a parameter instead of using global variables

### 171. Global Variable Conflict: Global variable 'code' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 647
**Recommendation:** Consider using a centralized state manager or passing 'code' as a parameter instead of using global variables

### 172. Global Variable Conflict: Global variable 'recommendations' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 736
**Recommendation:** Consider using a centralized state manager or passing 'recommendations' as a parameter instead of using global variables

### 173. Global Variable Conflict: Global variable 'r' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\code_quality_analyzer.py
**Line:** 750
**Recommendation:** Consider using a centralized state manager or passing 'r' as a parameter instead of using global variables

### 174. Global Variable Conflict: Global variable 'context' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\example_rag_usage.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 27
**Recommendation:** Consider using a centralized state manager or passing 'context' as a parameter instead of using global variables

### 175. Global Variable Conflict: Global variable 'project_root' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 118
**Recommendation:** Consider using a centralized state manager or passing 'project_root' as a parameter instead of using global variables

### 176. Global Variable Conflict: Global variable 'file_content' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 160
**Recommendation:** Consider using a centralized state manager or passing 'file_content' as a parameter instead of using global variables

### 177. Global Variable Conflict: Global variable 'file_list' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 256
**Recommendation:** Consider using a centralized state manager or passing 'file_list' as a parameter instead of using global variables

### 178. Global Variable Conflict: Global variable 'item' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 538
**Recommendation:** Consider using a centralized state manager or passing 'item' as a parameter instead of using global variables

### 179. Global Variable Conflict: Global variable 'end_line' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\conflict_analyzer.py
**Line:** 597
**Recommendation:** Consider using a centralized state manager or passing 'end_line' as a parameter instead of using global variables

### 180. Global Variable Conflict: Global variable 'match' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py
**Line:** 179
**Recommendation:** Consider using a centralized state manager or passing 'match' as a parameter instead of using global variables

### 181. Global Variable Conflict: Global variable 'module_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py
**Line:** 289
**Recommendation:** Consider using a centralized state manager or passing 'module_path' as a parameter instead of using global variables

### 182. Global Variable Conflict: Global variable 'init_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dead_code_analyzer.py
**Line:** 304
**Recommendation:** Consider using a centralized state manager or passing 'init_file' as a parameter instead of using global variables

### 183. Global Variable Conflict: Global variable 'root_logger' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 46
**Recommendation:** Consider using a centralized state manager or passing 'root_logger' as a parameter instead of using global variables

### 184. Global Variable Conflict: Global variable 'handler' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 50
**Recommendation:** Consider using a centralized state manager or passing 'handler' as a parameter instead of using global variables

### 185. Global Variable Conflict: Global variable 'console_handler' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 54
**Recommendation:** Consider using a centralized state manager or passing 'console_handler' as a parameter instead of using global variables

### 186. Global Variable Conflict: Global variable 'file_handler' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 61
**Recommendation:** Consider using a centralized state manager or passing 'file_handler' as a parameter instead of using global variables

### 187. Global Variable Conflict: Global variable 'original_import' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 82
**Recommendation:** Consider using a centralized state manager or passing 'original_import' as a parameter instead of using global variables

### 188. Global Variable Conflict: Global variable 'duration' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 91
**Recommendation:** Consider using a centralized state manager or passing 'duration' as a parameter instead of using global variables

### 189. Global Variable Conflict: Global variable 'original_event' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 109
**Recommendation:** Consider using a centralized state manager or passing 'original_event' as a parameter instead of using global variables

### 190. Global Variable Conflict: Global variable 'event_type' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 113
**Recommendation:** Consider using a centralized state manager or passing 'event_type' as a parameter instead of using global variables

### 191. Global Variable Conflict: Global variable 'important_events' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\debug_launcher.py
**Line:** 116
**Recommendation:** Consider using a centralized state manager or passing 'important_events' as a parameter instead of using global variables

### 192. Global Variable Conflict: Global variable 'source_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 33
**Recommendation:** Consider using a centralized state manager or passing 'source_file' as a parameter instead of using global variables

### 193. Global Variable Conflict: Global variable 'req_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 105
**Recommendation:** Consider using a centralized state manager or passing 'req_file' as a parameter instead of using global variables

### 194. Global Variable Conflict: Global variable 'data' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\example_rag_usage.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 119
**Recommendation:** Consider using a centralized state manager or passing 'data' as a parameter instead of using global variables

### 195. Global Variable Conflict: Global variable 'dep' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 131
**Recommendation:** Consider using a centralized state manager or passing 'dep' as a parameter instead of using global variables

### 196. Global Variable Conflict: Global variable 'pkg' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 263
**Recommendation:** Consider using a centralized state manager or passing 'pkg' as a parameter instead of using global variables

### 197. Global Variable Conflict: Global variable 'py_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\dependency_analyzer.py
**Line:** 344
**Recommendation:** Consider using a centralized state manager or passing 'py_file' as a parameter instead of using global variables

### 198. Global Variable Conflict: Global variable 'last_modified' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 45
**Recommendation:** Consider using a centralized state manager or passing 'last_modified' as a parameter instead of using global variables

### 199. Global Variable Conflict: Global variable 'all_files' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 112
**Recommendation:** Consider using a centralized state manager or passing 'all_files' as a parameter instead of using global variables

### 200. Global Variable Conflict: Global variable 'd' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\structure_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 347
**Recommendation:** Consider using a centralized state manager or passing 'd' as a parameter instead of using global variables

### 201. Global Variable Conflict: Global variable 'docstring' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 361
**Recommendation:** Consider using a centralized state manager or passing 'docstring' as a parameter instead of using global variables

### 202. Global Variable Conflict: Global variable 'module' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\setup_modules_updated.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 474
**Recommendation:** Consider using a centralized state manager or passing 'module' as a parameter instead of using global variables

### 203. Global Variable Conflict: Global variable 'count' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\documentation_analyzer.py
**Line:** 497
**Recommendation:** Consider using a centralized state manager or passing 'count' as a parameter instead of using global variables

### 204. Global Variable Conflict: Global variable 'j' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\enable_debug_logging.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py
**Line:** 256
**Recommendation:** Consider using a centralized state manager or passing 'j' as a parameter instead of using global variables

### 205. Global Variable Conflict: Global variable 'code_lines' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\duplicate_analyzer.py
**Line:** 526
**Recommendation:** Consider using a centralized state manager or passing 'code_lines' as a parameter instead of using global variables

### 206. Global Variable Conflict: Global variable 'file_name' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\file_analyzer.py
**Line:** 223
**Recommendation:** Consider using a centralized state manager or passing 'file_name' as a parameter instead of using global variables

### 207. Global Variable Conflict: Global variable 'log_level' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_logging.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 201
**Recommendation:** Consider using a centralized state manager or passing 'log_level' as a parameter instead of using global variables

### 208. Global Variable Conflict: Global variable 'config_kwargs' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 237
**Recommendation:** Consider using a centralized state manager or passing 'config_kwargs' as a parameter instead of using global variables

### 209. Global Variable Conflict: Global variable 'output_dir' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 274
**Recommendation:** Consider using a centralized state manager or passing 'output_dir' as a parameter instead of using global variables

### 210. Global Variable Conflict: Global variable 'format_extensions' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 283
**Recommendation:** Consider using a centralized state manager or passing 'format_extensions' as a parameter instead of using global variables

### 211. Global Variable Conflict: Global variable 'extension' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 288
**Recommendation:** Consider using a centralized state manager or passing 'extension' as a parameter instead of using global variables

### 212. Global Variable Conflict: Global variable 'filename' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 292
**Recommendation:** Consider using a centralized state manager or passing 'filename' as a parameter instead of using global variables

### 213. Global Variable Conflict: Global variable 'stats' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_analyzer_cache.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\fixed_cli.py
**Line:** 321
**Recommendation:** Consider using a centralized state manager or passing 'stats' as a parameter instead of using global variables

### 214. Global Variable Conflict: Global variable 'numeric_level' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\performance_test.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py
**Line:** 85
**Recommendation:** Consider using a centralized state manager or passing 'numeric_level' as a parameter instead of using global variables

### 215. Global Variable Conflict: Global variable 'issue_types' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\generate_test_data.py
**Line:** 117
**Recommendation:** Consider using a centralized state manager or passing 'issue_types' as a parameter instead of using global variables

### 216. Global Variable Conflict: Global variable 'key' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\gopiai_detailed_logger.py
**Line:** 142
**Recommendation:** Consider using a centralized state manager or passing 'key' as a parameter instead of using global variables

### 217. Global Variable Conflict: Global variable 'test_files' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py
**Line:** 183
**Recommendation:** Consider using a centralized state manager or passing 'test_files' as a parameter instead of using global variables

### 218. Global Variable Conflict: Global variable 'test_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\launcher.py
**Line:** 190
**Recommendation:** Consider using a centralized state manager or passing 'test_file' as a parameter instead of using global variables

### 219. Global Variable Conflict: Global variable 'all_dirs' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 35
**Recommendation:** Consider using a centralized state manager or passing 'all_dirs' as a parameter instead of using global variables

### 220. Global Variable Conflict: Global variable 'dir_path' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 47
**Recommendation:** Consider using a centralized state manager or passing 'dir_path' as a parameter instead of using global variables

### 221. Global Variable Conflict: Global variable 'extensions' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 51
**Recommendation:** Consider using a centralized state manager or passing 'extensions' as a parameter instead of using global variables

### 222. Global Variable Conflict: Global variable 'gopiai_modules' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 57
**Recommendation:** Consider using a centralized state manager or passing 'gopiai_modules' as a parameter instead of using global variables

### 223. Global Variable Conflict: Global variable 'report' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 60
**Recommendation:** Consider using a centralized state manager or passing 'report' as a parameter instead of using global variables

### 224. Global Variable Conflict: Global variable 'output_file' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 147
**Recommendation:** Consider using a centralized state manager or passing 'output_file' as a parameter instead of using global variables

### 225. Global Variable Conflict: Global variable 'report_content' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_report.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\manual_analyzer.py
**Line:** 150
**Recommendation:** Consider using a centralized state manager or passing 'report_content' as a parameter instead of using global variables

### 226. Global Variable Conflict: Global variable 'category' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py
**Line:** 20
**Recommendation:** Consider using a centralized state manager or passing 'category' as a parameter instead of using global variables

### 227. Global Variable Conflict: Global variable 'recommendation' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py
**Line:** 25
**Recommendation:** Consider using a centralized state manager or passing 'recommendation' as a parameter instead of using global variables

### 228. Global Variable Conflict: Global variable 'summary' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\rag_cleanup_wizard.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_analyzer.py
**Line:** 113
**Recommendation:** Consider using a centralized state manager or passing 'summary' as a parameter instead of using global variables

### 229. Global Variable Conflict: Global variable 'config_data' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_cleanup_infrastructure.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py
**Line:** 194
**Recommendation:** Consider using a centralized state manager or passing 'config_data' as a parameter instead of using global variables

### 230. Global Variable Conflict: Global variable 'all_results' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py
**Line:** 231
**Recommendation:** Consider using a centralized state manager or passing 'all_results' as a parameter instead of using global variables

### 231. Global Variable Conflict: Global variable 'all_errors' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py
**Line:** 232
**Recommendation:** Consider using a centralized state manager or passing 'all_errors' as a parameter instead of using global variables

### 232. Global Variable Conflict: Global variable 'executor' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py
**Line:** 243
**Recommendation:** Consider using a centralized state manager or passing 'executor' as a parameter instead of using global variables

### 233. Global Variable Conflict: Global variable 'future' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\project_cleanup_orchestrator.py
**Line:** 251
**Recommendation:** Consider using a centralized state manager or passing 'future' as a parameter instead of using global variables

### 234. Global Variable Conflict: Global variable 'analyzers' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py
**Line:** 174
**Recommendation:** Consider using a centralized state manager or passing 'analyzers' as a parameter instead of using global variables

### 235. Global Variable Conflict: Global variable 'report_generator' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py
**Line:** 210
**Recommendation:** Consider using a centralized state manager or passing 'report_generator' as a parameter instead of using global variables

### 236. Global Variable Conflict: Global variable 'results_by_category' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py
**Line:** 32
**Recommendation:** Consider using a centralized state manager or passing 'results_by_category' as a parameter instead of using global variables

### 237. Global Variable Conflict: Global variable 'category_results' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\simple_cleanup_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\report_generator.py
**Line:** 73
**Recommendation:** Consider using a centralized state manager or passing 'category_results' as a parameter instead of using global variables

### 238. Global Variable Conflict: Global variable 'env' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\run_with_debug_fixed.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\reproduce_hang_with_debug.py
**Line:** 96
**Recommendation:** Consider using a centralized state manager or passing 'env' as a parameter instead of using global variables

### 239. Global Variable Conflict: Global variable 'complexities' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_simple.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 88
**Recommendation:** Consider using a centralized state manager or passing 'complexities' as a parameter instead of using global variables

### 240. Global Variable Conflict: Global variable 'line_too_long_issues' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 120
**Recommendation:** Consider using a centralized state manager or passing 'line_too_long_issues' as a parameter instead of using global variables

### 241. Global Variable Conflict: Global variable 'trailing_issues' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 130
**Recommendation:** Consider using a centralized state manager or passing 'trailing_issues' as a parameter instead of using global variables

### 242. Global Variable Conflict: Global variable 'complexity_results' is modified in multiple files: C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py, C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer_unit.py

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\test_code_quality_analyzer.py
**Line:** 203
**Recommendation:** Consider using a centralized state manager or passing 'complexity_results' as a parameter instead of using global variables

### 243. Resource Leak: Potential connection resource leak: Connection opened without proper context management

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\analyze_project.py
**Line:** 117
**Recommendation:** Use connection context managers or ensure connections are closed in finally blocks

### 244. Resource Leak: Potential connection resource leak: Connection opened without proper context management

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\quick_analyze.py
**Line:** 236
**Recommendation:** Use connection context managers or ensure connections are closed in finally blocks

### 245. Resource Leak: Potential connection resource leak: Connection opened without proper context management

**Severity:** HIGH
**File:** C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\strict_analyzer.py
**Line:** 286
**Recommendation:** Use connection context managers or ensure connections are closed in finally blocks

