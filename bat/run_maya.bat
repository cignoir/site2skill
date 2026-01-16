REM Commands
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2025/JPN/Maya-Tech-Docs/Commands/index_all.html" maya2025_cmd_mel --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2025/JPN/Maya-Tech-Docs/CommandsPython/index_all.html" maya2025_cmd_python --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2026/JPN/Maya-Tech-Docs/Commands/index_all.html" maya2026_cmd_mel --output output
python -m site2skill.main "https://help.autodesk.com/cloudhelp/2026/JPN/Maya-Tech-Docs/CommandsPython/index_all.html" maya2026_cmd_python --output output

REM API Ref
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2025/ENU/?guid=MAYA_API_REF_cpp_ref_index_html" maya2025_cpp --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2026/ENU/?guid=MAYA_API_REF_cpp_ref_index_html" maya2026_cpp --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2025/ENU/?guid=MAYA_API_REF_py_ref_index_html" maya2025_python --browser --sidebar-selector "#nav-tree" --output output
python -m site2skill.main "https://help.autodesk.com/view/MAYADEV/2026/ENU/?guid=MAYA_API_REF_py_ref_index_html" maya2026_python --browser --sidebar-selector "#nav-tree" --output output