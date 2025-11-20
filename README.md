# AutoSlideGen

🚀 **自动化生成PPT大纲的智能工具链**

AutoSlideGen 是一个基于大语言模型（LLM）的自动化演示文稿生成工具，能够根据主题、受众和演示目的，自动生成结构清晰、逻辑完整的PPT大纲，并输出为标准PPTX文件，完美兼容 Microsoft PowerPoint 和 LibreOffice Impress。

## ✨ 核心特性

- 🤖 **智能大纲生成**: 利用先进的LLM技术，自动生成高质量的演示文稿结构
- 📊 **结构化输出**: 支持标题页、内容页、章节分隔页等多种幻灯片类型
- 🌐 **多语言支持**: 支持中文、英文、日语、西班牙语等多种语言
- 🔌 **多模型兼容**: 支持 OpenAI GPT、Anthropic Claude 等主流LLM
- 📝 **标准格式**: 生成符合标准的PPTX文件，可直接编辑和演示
- 🎯 **MVP设计**: 专注于核心功能，保证稳定性和通用性
- 🔧 **易于扩展**: 清晰的模块化架构，便于后续功能扩展

## 🏗️ 系统架构

AutoSlideGen 采用模块化设计，包含三个核心模块:

```
┌─────────────────────────────────────────────────┐
│              AutoSlideGen 系统                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │   1. 大纲生成模块 (Outline Generator)     │  │
│  │   • 调用LLM API (OpenAI/Anthropic)       │  │
│  │   • 生成结构化JSON大纲                   │  │
│  │   • 智能重试和优化                       │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │   2. 格式解析模块 (Parser/Validator)     │  │
│  │   • JSON结构校验                         │  │
│  │   • Pydantic数据验证                     │  │
│  │   • 错误检测和报告                       │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │   3. PPT构建模块 (PPT Builder)           │  │
│  │   • python-pptx生成PPTX                  │  │
│  │   • 自动排版和样式                       │  │
│  │   • 标准格式输出                         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 目录结构

```
AutoSlideGen/
├── src/autoslidegen/          # 源代码
│   ├── outline_generator/     # LLM大纲生成
│   │   ├── base.py           # 生成器基类
│   │   ├── openai_generator.py
│   │   ├── anthropic_generator.py
│   │   ├── factory.py        # 生成器工厂
│   │   └── prompts.py        # 提示词模板
│   ├── parser/               # 解析和验证
│   │   ├── models.py         # Pydantic数据模型
│   │   └── validator.py      # JSON校验器
│   ├── ppt_builder/          # PPT构建
│   │   └── builder.py        # PPTX生成器
│   ├── utils/                # 工具函数
│   │   └── config.py         # 配置管理
│   ├── main.py               # 主程序
│   └── cli.py                # 命令行接口
├── tests/                    # 测试用例
├── examples/                 # 示例文件
├── output/                   # 输出目录
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖列表
├── setup.py                  # 安装脚本
└── README.md                 # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/GeoffreyWang1117/AutoSlideGen.git
cd AutoSlideGen
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

或安装为可编辑包:

```bash
pip install -e .
```

4. **配置API密钥**

复制环境变量模板:

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的API密钥:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 基本使用

#### 命令行界面 (CLI)

**生成演示文稿:**

```bash
autoslidegen generate \
  --topic "人工智能的未来发展" \
  --audience "技术专业人士和行业决策者" \
  --purpose "介绍人工智能的最新发展趋势和应用前景" \
  --language zh \
  --slides 12 \
  --bullets 4
```

**参数说明:**

- `--topic, -t`: 演示主题（必需）
- `--audience, -a`: 目标受众（必需）
- `--purpose, -p`: 演示目的（必需）
- `--language, -l`: 语言代码 (zh/en/ja/es，默认: zh)
- `--slides, -s`: 幻灯片数量（5-30，默认: 10）
- `--bullets, -b`: 每页要点数（2-6，默认: 4）
- `--provider`: LLM提供商 (openai/anthropic)
- `--output, -o`: 输出文件路径
- `--requirements, -r`: 额外要求
- `--no-json`: 不保存JSON大纲

**从JSON构建PPTX:**

```bash
autoslidegen build outline.json --output presentation.pptx
```

**查看可用提供商:**

```bash
autoslidegen providers
```

**运行示例:**

```bash
autoslidegen example
```

#### Python API

```python
from autoslidegen import AutoSlideGen

# 初始化生成器
generator = AutoSlideGen(provider='openai')

# 生成演示文稿
result = generator.generate(
    topic="Python编程最佳实践",
    audience="初级到中级Python开发者",
    purpose="分享实用的Python编程技巧和模式",
    language="zh",
    num_slides=15,
    bullets_per_slide=4
)

print(f"PPTX文件: {result['pptx_path']}")
print(f"JSON大纲: {result['json_path']}")
```

## 📋 JSON Schema

生成的大纲遵循以下JSON结构:

```json
{
  "metadata": {
    "topic": "演示主题",
    "audience": "目标受众",
    "purpose": "演示目的",
    "language": "zh",
    "estimated_duration": 30
  },
  "slides": [
    {
      "slide_number": 1,
      "title": "演示标题",
      "slide_type": "title",
      "bullet_points": [
        {
          "text": "要点内容",
          "level": 1
        }
      ],
      "notes": "演讲备注（可选）"
    }
  ]
}
```

### 幻灯片类型

- `title`: 标题页（封面）
- `content`: 内容页（包含要点列表）
- `section`: 章节分隔页

## ⚙️ 配置

编辑 `config.yaml` 来自定义配置:

```yaml
llm:
  provider: "openai"  # 或 "anthropic"

  models:
    openai:
      model_name: "gpt-4-turbo-preview"
      temperature: 0.7
      max_tokens: 4096

    anthropic:
      model_name: "claude-3-5-sonnet-20241022"
      temperature: 0.7
      max_tokens: 4096

outline:
  min_slides: 5
  max_slides: 30
  default_slides: 10
  min_bullets_per_slide: 2
  max_bullets_per_slide: 6

ppt:
  fonts:
    title:
      name: "Arial"
      size: 44
      bold: true
      color: "1F4E78"

    bullet:
      name: "Arial"
      size: 16
      color: "333333"

output:
  default_dir: "./output"
```

## 🧪 开发和测试

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
```

### 类型检查

```bash
mypy src/
```

## 🛣️ 未来规划

AutoSlideGen 的后续版本将扩展以下功能:

- [ ] **多Agent架构**: 支持专门的Agent处理不同任务
- [ ] **图表生成**: 自动生成图表和可视化
- [ ] **图片插入**: 智能匹配和插入相关图片
- [ ] **演讲稿生成**: 为每页生成完整演讲稿
- [ ] **RAG检索增强**: 基于知识库生成内容
- [ ] **模板系统**: 支持自定义PPT模板
- [ ] **实时协作**: 多人协作编辑
- [ ] **Web界面**: 提供友好的Web操作界面

## 🤝 贡献

欢迎贡献! 请遵循以下步骤:

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [python-pptx](https://python-pptx.readthedocs.io/) - PPT生成库
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证
- [Click](https://click.palletsprojects.com/) - CLI框架
- [Rich](https://rich.readthedocs.io/) - 终端美化

## 📧 联系方式

项目链接: [https://github.com/GeoffreyWang1117/AutoSlideGen](https://github.com/GeoffreyWang1117/AutoSlideGen)

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！
