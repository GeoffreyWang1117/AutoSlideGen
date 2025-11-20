# AutoSlideGen 扩展功能文档

本文档介绍AutoSlideGen的高级扩展功能。

## 🎤 演讲稿生成 (Speaker Notes)

自动为每张幻灯片生成详细的演讲稿，帮助演讲者更好地表达内容。

### 使用方法

**命令行：**

```bash
autoslidegen generate \
  --topic "人工智能的未来" \
  --audience "技术决策者" \
  --purpose "介绍AI趋势" \
  --speaker-notes
```

**Python API：**

```python
from autoslidegen import AutoSlideGen

generator = AutoSlideGen(provider='openai')

result = generator.generate(
    topic="Python编程最佳实践",
    audience="开发者",
    purpose="分享编程技巧",
    generate_speaker_notes=True  # 启用演讲稿生成
)
```

### 功能特点

- ✅ 自动扩展每个要点，提供详细说明
- ✅ 使用口语化表达，适合现场演讲
- ✅ 包含开场、要点阐述和过渡语
- ✅ 支持中英日西多种语言

---

## 🖼️ 图片搜索和插入

自动搜索相关图片并插入到演示文稿中，提升视觉效果。

### 前置要求

获取API密钥：
- **Unsplash**: https://unsplash.com/developers
- **Pexels**: https://www.pexels.com/api/

在`.env`文件中配置：

```env
UNSPLASH_API_KEY=your_access_key
PEXELS_API_KEY=your_api_key
```

### 使用方法

**命令行：**

```bash
autoslidegen generate \
  --topic "云计算技术" \
  --audience "IT专业人士" \
  --purpose "介绍云计算" \
  --add-images \
  --image-provider unsplash
```

**Python API：**

```python
generator = AutoSlideGen(provider='openai')

result = generator.generate(
    topic="云计算技术",
    audience="IT专业人士",
    purpose="介绍云计算",
    add_images=True,          # 启用图片搜索
    image_provider='unsplash'  # 选择图片源
)
```

### 支持的图片源

- **Unsplash**: 高质量免费图片
- **Pexels**: 免费图片和视频

### 功能特点

- ✅ 智能关键词提取from幻灯片标题
- ✅ 自动下载并缓存图片
- ✅ 合适的图片位置和大小
- ✅ 支持多种图片源

---

## 📊 图表生成

自动识别需要数据可视化的内容并生成相应图表。

### 使用方法

**命令行：**

```bash
autoslidegen generate \
  --topic "销售数据分析" \
  --audience "管理层" \
  --purpose "展示销售趋势" \
  --add-charts
```

**Python API：**

```python
result = generator.generate(
    topic="销售数据分析",
    audience="管理层",
    purpose="展示销售趋势",
    add_charts=True  # 启用图表生成
)
```

### 支持的图表类型

- **柱状图 (Bar Chart)**: 用于对比分析
- **饼图 (Pie Chart)**: 用于展示占比分布
- **折线图 (Line Chart)**: 用于展示趋势变化

### 自动识别规则

系统会根据幻灯片标题自动判断：
- 包含"对比"、"比较" → 柱状图
- 包含"分布"、"占比" → 饼图
- 包含"趋势"、"增长" → 折线图

### 手动创建图表

```python
from autoslidegen.extensions import ChartGenerator

chart_gen = ChartGenerator(library='matplotlib')

# 创建柱状图
chart_path = chart_gen.create_bar_chart(
    data={'Q1': 100, 'Q2': 150, 'Q3': 120, 'Q4': 180},
    title='季度销售额',
    xlabel='季度',
    ylabel='销售额 (万元)'
)

# 创建饼图
chart_path = chart_gen.create_pie_chart(
    data={'产品A': 35, '产品B': 25, '产品C': 40},
    title='产品销售占比'
)
```

---

## 🎨 自定义模板系统

使用自己的PowerPoint模板，保持品牌一致性。

### 模板管理

**添加模板：**

```python
from autoslidegen.extensions import TemplateManager

tm = TemplateManager()

# 添加自定义模板
tm.add_template(
    template_path='./my_templates/corporate.pptx',
    template_name='corporate'
)

# 列出所有模板
templates = tm.list_templates()
print(templates)  # ['corporate', ...]

# 查看模板信息
info = tm.get_template_info('corporate')
print(info)
```

**使用模板生成：**

```python
from autoslidegen.extensions import CustomizableTemplateBuilder

# 加载模板
builder = CustomizableTemplateBuilder(tm, template_name='corporate')

# 自定义布局映射
builder.set_layout_mapping({
    'title': 0,
    'content': 1,
    'section': 3
})

# 使用模板创建演示
prs = builder.create_presentation()
```

### 模板要求

- 格式：标准PPTX文件
- 建议包含：标题页、内容页、章节页布局
- 支持：自定义字体、配色方案、背景

---

## 📚 RAG检索增强生成

基于知识库生成更准确、更专业的内容。

### 设置知识库

1. 创建知识库目录：

```bash
mkdir knowledge_base
```

2. 添加文档（支持txt、md格式）：

```
knowledge_base/
├── ai_basics.txt
├── machine_learning.md
└── deep_learning.md
```

### 使用方法

```python
from autoslidegen.extensions import SimpleRAGGenerator

# 初始化RAG生成器
rag_gen = SimpleRAGGenerator(knowledge_base_path='./knowledge_base')

# 获取增强的需求描述
enhanced_req = rag_gen.get_enhanced_requirements(
    topic='机器学习基础',
    original_requirements='重点介绍监督学习'
)

# 在生成时使用
result = generator.generate(
    topic='机器学习基础',
    audience='数据科学初学者',
    purpose='入门教学',
    additional_requirements=enhanced_req
)
```

### 高级RAG用法

```python
from autoslidegen.extensions import RAGEnhancer, DocumentStore

# 创建文档存储
doc_store = DocumentStore('./knowledge_base')

# 添加新文档
doc_store.add_document(
    content="人工智能是...",
    name="ai_intro.txt",
    metadata={'author': 'Expert', 'date': '2024-01-01'}
)

# 搜索相关文档
results = doc_store.search('深度学习', top_k=3)
```

### 功能特点

- ✅ 自动从知识库检索相关内容
- ✅ 增强生成质量和专业性
- ✅ 支持txt、md等文档格式
- ✅ 简单的关键词搜索

---

## 🤖 多Agent架构

专门的Agent协同工作，提升生成质量。

### Agent角色

- **Content Strategist** (内容策略师): 规划演示结构
- **Writer** (撰稿人): 生成幻灯片内容
- **Designer** (设计师): 提供视觉设计建议
- **Reviewer** (审核员): 审查和改进内容
- **Coordinator** (协调员): 协调多个Agent

### 使用方法

```python
from autoslidegen.extensions import MultiAgentOrchestrator

# 初始化orchestrator
orchestrator = MultiAgentOrchestrator(llm_generator)

# 使用多Agent生成
results = orchestrator.generate_with_agents_sync(
    topic='产品发布计划',
    audience='投资者和合作伙伴',
    purpose='展示新产品',
    num_slides=15
)

# 查看各Agent的输出
print(results['workflow_results']['strategy'])  # 结构规划
print(results['workflow_results']['content'])   # 内容生成
print(results['workflow_results']['design'])    # 设计建议
```

### 自定义Agent

```python
from autoslidegen.extensions import Agent, AgentRole

class CustomAgent(Agent):
    def __init__(self, llm_generator):
        super().__init__(AgentRole.WRITER, llm_generator)

    async def process(self, task):
        # 自定义处理逻辑
        return {
            'status': 'success',
            'result': '...'
        }
```

---

## 🔧 组合使用

所有功能可以组合使用以获得最佳效果：

```bash
autoslidegen generate \
  --topic "企业数字化转型" \
  --audience "企业高管" \
  --purpose "战略规划" \
  --slides 20 \
  --speaker-notes \
  --add-images \
  --add-charts \
  --provider openai
```

或在Python中：

```python
from autoslidegen import AutoSlideGen

generator = AutoSlideGen(provider='openai')

result = generator.generate(
    topic="企业数字化转型",
    audience="企业高管",
    purpose="战略规划",
    num_slides=20,
    generate_speaker_notes=True,  # 演讲稿
    add_images=True,               # 图片
    add_charts=True                # 图表
)
```

---

## 🚀 最佳实践

1. **演讲稿生成**：适合需要详细讲解的教学和培训场景
2. **图片插入**：提升视觉吸引力，但确保图片与主题相关
3. **图表生成**：数据密集型演示必备
4. **自定义模板**：企业演示保持品牌一致性
5. **RAG增强**：专业领域演示提升准确性
6. **多Agent**：复杂演示需要多角度优化

---

## 📝 注意事项

- **API配额**：图片搜索API有调用限制，注意配额
- **性能**：启用多个扩展功能会增加生成时间
- **依赖包**：某些功能需要额外的Python包（见requirements.txt）
- **模板兼容性**：自定义模板需要标准的PPTX格式

---

## 🤝 贡献

欢迎贡献新的扩展功能！请参考 [CONTRIBUTING.md](CONTRIBUTING.md)
