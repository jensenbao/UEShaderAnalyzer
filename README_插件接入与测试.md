# MaterialAnalyzer 插件接入与测试（UE5.3）

## 1. 插件位置

将本目录复制到 UE 项目：

`<YourUEProject>/Plugins/MaterialAnalyzer`

确保包含：
1. `MaterialAnalyzer.uplugin`
2. `Source/MaterialAnalyzerEditor/*`

## 2. 生成并编译

1. 关闭 UE 编辑器。
2. 右键 `.uproject` -> Generate Visual Studio project files。
3. 用 VS 打开工程并编译 `Development Editor`。
4. 启动 UE，确认插件已启用。

## 2.1 Python 层复用位置（新增）

从当前版本开始，Python 与 Web 侧核心脚本统一维护在插件目录：

1. `Plugins/MaterialAnalyzer/Content/Python/ue_http_bridge_server.py`
2. `Plugins/MaterialAnalyzer/Content/Python/ue_open_web_for_selected_material.py`
3. `Plugins/MaterialAnalyzer/Content/Python/material_analyzer_streamlit_app.py`
4. `Plugins/MaterialAnalyzer/Content/Python/material_analyzer_init.py`

说明：
1. 项目级 `Content/Python/*` 同名文件已改为兼容转发壳（wrapper）。
2. 日常维护只改插件目录版本即可，便于跨项目复用与分发。
3. 插件已提供 `Plugins/MaterialAnalyzer/Content/Python/init_unreal.py`，复制插件后可自动执行启动逻辑。
4. 插件不再在 UE 启动时自动安装依赖，避免首次启动卡住编辑器。

## 2.2 Python 环境一键安装（给所有用户）

首次使用前，在项目根目录执行：

0. 先关闭 Unreal Editor（必须）。

1. PowerShell（推荐）
`cd Plugins/MaterialAnalyzer`
`./setup_python_env.ps1`

2. 或 CMD
`cd Plugins\\MaterialAnalyzer`
`setup_python_env.bat`

说明：
1. 脚本会自动定位 UE 内置 Python。
2. 在 `Plugins/MaterialAnalyzer/Content/Python/.venv` 创建虚拟环境。
3. 安装 `requirements_streamlit.txt` 中依赖并做导入校验。
4. 完成后再打开 UE，启动阶段只检查不安装。

## 3. 已提供的 C++ 可调用接口

类名：`UMaterialAnalyzerBPLibrary`

函数：
1. `GetMaterialSummaryJson(material_path)`
2. `GetSelectedMaterialSummaryJson()`
3. `GetMaterialPropertiesJson(material_path)`
4. `GetMaterialShaderCodeJson(material_path)`（占位）
5. `CompileMaterialJson(material_path)`（占位）

## 4. 在 UE Python 中测试（Cmd 里用 py 前缀）

先选中一个材质后执行：

`py import unreal; print(unreal.MaterialAnalyzerBPLibrary.get_selected_material_summary_json())`

按路径测试：

`py import unreal; print(unreal.MaterialAnalyzerBPLibrary.get_material_summary_json('/Game/JIANG.JIE/08/MAT/M_ShockWave.M_ShockWave'))`

仅材质属性测试：

`py import unreal; print(unreal.MaterialAnalyzerBPLibrary.get_material_properties_json('/Game/JIANG.JIE/08/MAT/M_ShockWave.M_ShockWave'))`

## 5. 当前实现说明

已实现：
1. 导出基础材质信息（路径、名称、Domain、BlendMode、TwoSided）。
2. 导出节点列表（基于 MaterialEditingLibrary）。
3. 导出边（通过表达式输入反射构建）。
4. 导出常见输出绑定（BaseColor/Emissive/Opacity/Normal/Roughness/Metallic等）。

暂未实现：
1. Shader 代码导出。
2. 强制编译并返回编译日志。
3. 注释框、分组、孤立节点精确标注。

## 6. 常见问题

1. Python 找不到 `MaterialAnalyzerBPLibrary`：
- 插件未编译成功或未启用。

2. `asset_not_found`：
- 路径必须是完整对象路径（`/Game/.../M_Name.M_Name`）。

3. 返回节点数为 0：
- 材质表达式可能主要在函数或实例链，下一步需补函数展开与实例追溯。
