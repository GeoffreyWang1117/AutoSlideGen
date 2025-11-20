# AutoSlideGen 快速入门指南

本指南将帮助你快速上手 AutoSlideGen。

## 1. 安装

### 方式一：直接安装依赖

```bash
# 克隆项目
git clone https://github.com/GeoffreyWang1117/AutoSlideGen.git
cd AutoSlideGen

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 方式二：以开发模式安装

```bash
pip install -e .
```

## 2. 配置API密钥

创建 `.env` 文件并添加你的API密钥:

```bash
cp .env.example .env
```

编辑 `.env`:

```env
# 使用OpenAI
OPENAI_API_KEY=sk-...

# 或使用Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## 3. 第一次运行

### 使用命令行

```bash
autoslidegen generate \
  --topic "Python基础教程" \
  --audience "编程初学者" \
  --purpose "介绍Python的基本概念和语法" \
  --language zh \
  --slides 10
```

### 使用Python API

创建 `test_gen.py`:

```python
from autoslidegen import AutoSlideGen

# 初始化
generator = AutoSlideGen(provider='openai')

# 生成
result = generator.generate(
    topic="Python基础教程",
    audience="编程初学者",
    purpose="介绍Python的基本概念和语法",
    language="zh",
    num_slides=10
)

print(f"生成成功: {result['pptx_path']}")
```

运行:

```bash
python test_gen.py
```

## 4. 查看输出

生成的文件位于 `./output/` 目录:

```
output/
├── Python基础教程_20240115_143022.pptx
└── Python基础教程_20240115_143022.json
```

## 5. 从JSON重新生成

如果你想修改JSON后重新生成PPTX:

```bash
autoslidegen build output/你的文件.json --output 新文件.pptx
```

## 6. 运行示例

项目包含完整的示例代码:

```bash
# 运行Python示例
python examples/example_usage.py

# 或使用CLI示例命令
autoslidegen example
```

## 7. 常见问题

### Q: API调用失败

**A:** 检查:
1. API密钥是否正确设置
2. 网络连接是否正常
3. API配额是否充足

### Q: 生成的内容不理想

**A:** 尝试:
1. 调整 `--requirements` 参数添加更详细的要求
2. 修改 `config.yaml` 中的 temperature 参数
3. 使用不同的LLM提供商

### Q: 中文显示乱码

**A:** 确保:
1. 系统安装了中文字体
2. `config.yaml` 中字体设置正确
3. 终端支持UTF-8编码

## 8. 自定义配置

编辑 `config.yaml` 来自定义:

```yaml
# 更改默认幻灯片数量
outline:
  default_slides: 15

# 更改字体
ppt:
  fonts:
    title:
      name: "微软雅黑"
      size: 48

# 更改输出目录
output:
  default_dir: "./my_presentations"
```

## 9. 下一步

- 查看 [README.md](README.md) 了解完整功能
- 阅读 [examples/](examples/) 目录中的示例
- 参考 [API文档](docs/) 了解高级用法

## 10. 获取帮助

```bash
# 查看CLI帮助
autoslidegen --help
autoslidegen generate --help

# 查看可用提供商
autoslidegen providers
```

如有问题，请访问 [GitHub Issues](https://github.com/GeoffreyWang1117/AutoSlideGen/issues)。
