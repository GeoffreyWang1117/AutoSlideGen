# 更新日志 (Changelog)

本文档记录AutoSlideGen项目的所有重要更改。

## [0.2.0] - 2024-11-20

### 🎉 重大功能更新

本次更新实现了完整的扩展功能系统，大幅提升AutoSlideGen的能力和实用性。

#### ✨ 新增功能

**1. 演讲稿生成 (Speaker Notes Generation)**
- 自动为每张幻灯片生成详细的演讲稿
- 支持中英日西四种语言
- 使用口语化表达，适合现场演讲
- CLI参数：`--speaker-notes`
- Python API：`generate_speaker_notes=True`

**2. 图片搜索和插入 (Image Search & Insertion)**
- 集成Unsplash和Pexels图片API
- 智能提取关键词进行搜索
- 自动下载并缓存图片
- 支持自定义图片提供商
- CLI参数：`--add-images --image-provider unsplash`
- Python API：`add_images=True, image_provider='unsplash'`

**3. 图表生成 (Chart Generation)**
- 支持柱状图、饼图、折线图
- 基于matplotlib和plotly两种库
- 智能识别需要数据可视化的幻灯片
- 自动生成示例数据图表
- CLI参数：`--add-charts`
- Python API：`add_charts=True`

**4. 自定义模板系统 (Custom Template System)**
- 支持导入自定义PPTX模板
- 模板管理功能（添加、删除、列表）
- 自定义布局索引映射
- 保持企业品牌一致性
- 独立模块：`TemplateManager`, `CustomizableTemplateBuilder`

**5. RAG检索增强 (RAG Enhancement)**
- 基于知识库生成更专业的内容
- 简单的文档存储和检索系统
- 支持txt、md等文档格式
- 关键词搜索相关内容
- 独立模块：`DocumentStore`, `RAGEnhancer`, `SimpleRAGGenerator`

**6. 多Agent架构 (Multi-Agent Architecture)**
- 专门的Agent处理不同任务
- 包含5种Agent角色：
  - Content Strategist（内容策略师）
  - Writer（撰稿人）
  - Designer（设计师）
  - Reviewer（审核员）
  - Coordinator（协调员）
- 支持自定义Agent扩展
- 独立模块：`MultiAgentOrchestrator`

#### 🔧 技术改进

**依赖更新**
- 添加 `requests>=2.31.0` - HTTP请求
- 添加 `Pillow>=10.0.0` - 图片处理
- 添加 `matplotlib>=3.7.0` - 图表生成
- 添加 `plotly>=5.14.0` - 交互式图表

**架构优化**
- 创建`extensions`模块统一管理扩展功能
- 所有扩展功能独立可选
- 完整的错误处理和日志记录
- 支持异步操作

**代码改进**
- `main.py`: 集成所有扩展功能
- `cli.py`: 添加新的命令行参数
- `ppt_builder/builder.py`: 支持图片插入
- 模块化设计，易于维护和扩展

#### 📚 文档更新

- 新增 `EXTENSIONS.md` - 详细的扩展功能文档
- 新增 `CHANGELOG.md` - 更新日志
- 更新 `.env.example` - 包含图片API配置
- 创建 `examples/advanced_features_example.py` - 高级功能示例

#### 🎯 使用示例

**组合使用所有功能：**

```bash
autoslidegen generate \
  --topic "企业数字化转型" \
  --audience "企业高管" \
  --purpose "战略规划" \
  --slides 20 \
  --speaker-notes \
  --add-images \
  --add-charts
```

**Python API：**

```python
from autoslidegen import AutoSlideGen

generator = AutoSlideGen(provider='openai')

result = generator.generate(
    topic="企业数字化转型",
    audience="企业高管",
    purpose="战略规划",
    num_slides=20,
    generate_speaker_notes=True,
    add_images=True,
    add_charts=True
)
```

#### 🐛 修复

- 修复PPT构建器中的图片插入逻辑
- 改进错误处理机制
- 优化配置文件加载

#### ⚠️ 注意事项

- 图片搜索功能需要配置API密钥（Unsplash或Pexels）
- 图表生成需要安装matplotlib或plotly
- 启用多个扩展功能会增加生成时间
- 某些API有调用频率限制

---

## [0.1.0] - 2024-11-20

### 🎉 首次发布 - MVP版本

#### ✨ 核心功能

**1. 大纲生成模块**
- 支持OpenAI GPT模型
- 支持Anthropic Claude模型
- 智能重试机制
- JSON格式输出

**2. 格式解析与验证**
- 基于Pydantic的数据模型
- 完整的JSON Schema验证
- 详细的错误报告

**3. PPT自动构建**
- python-pptx集成
- 支持标题页、内容页、章节页
- 自动排版和样式
- 多层级要点支持
- 演讲备注功能

**4. CLI工具**
- 完整的命令行接口
- Rich库美化输出
- 进度提示

**5. 配置系统**
- YAML配置文件
- 环境变量支持
- 多语言支持（中英日西）

#### 📦 项目结构

```
AutoSlideGen/
├── src/autoslidegen/
│   ├── outline_generator/
│   ├── parser/
│   ├── ppt_builder/
│   └── utils/
├── tests/
├── examples/
└── docs/
```

#### 📚 文档

- README.md - 项目介绍
- QUICKSTART.md - 快速入门
- CONTRIBUTING.md - 贡献指南
- LICENSE - MIT许可证

#### 🚀 特性

- ✅ 多LLM提供商支持
- ✅ 灵活的配置系统
- ✅ 完整的数据验证
- ✅ CLI和Python API双重接口
- ✅ 标准PPTX格式输出
- ✅ 多语言支持

---

## 未来计划

### 下一版本 (0.3.0)

- [ ] Web界面
- [ ] 更多图表类型
- [ ] 视频内容支持
- [ ] 实时协作功能
- [ ] 更智能的RAG系统
- [ ] 更多LLM提供商支持

### 长期规划

- [ ] 云服务版本
- [ ] 移动应用
- [ ] 企业级功能
- [ ] AI驱动的设计建议
- [ ] 多人协作编辑

---

## 贡献者

感谢所有为AutoSlideGen项目做出贡献的开发者！

如需贡献，请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 问题反馈

如遇到问题，请在 [GitHub Issues](https://github.com/GeoffreyWang1117/AutoSlideGen/issues) 提交。
