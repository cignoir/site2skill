REM Commands
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2025/JPN/Maya-Tech-Docs/Commands/index_all.html" maya2025-cmd-mel --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2025/JPN/Maya-Tech-Docs/CommandsPython/index_all.html" maya2025-cmd-python --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2026/JPN/Maya-Tech-Docs/Commands/index_all.html" maya2026-cmd-mel --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2026/JPN/Maya-Tech-Docs/CommandsPython/index_all.html" maya2026-cmd-python --output output

REM API Ref
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2025/ENU/?guid=MAYA_API_REF_cpp_ref_index_html" maya2025-cpp --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2026/ENU/?guid=MAYA_API_REF_cpp_ref_index_html" maya2026-cpp --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2025/ENU/?guid=MAYA_API_REF_py_ref_index_html" maya2025-python --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2026/ENU/?guid=MAYA_API_REF_py_ref_index_html" maya2026-python --browser --sidebar-selector "#nav-tree" --output output