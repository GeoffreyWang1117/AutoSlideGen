# 贡献指南

感谢你对 AutoSlideGen 项目的兴趣！我们欢迎所有形式的贡献。

## 如何贡献

### 报告Bug

如果你发现了bug，请创建一个Issue并包含:

1. Bug的详细描述
2. 复现步骤
3. 期望的行为
4. 实际的行为
5. 系统环境信息（操作系统、Python版本等）
6. 相关的日志或错误信息

### 建议新功能

我们欢迎功能建议！请创建Issue并说明:

1. 功能的用途和价值
2. 预期的使用场景
3. 可能的实现方案
4. 是否愿意参与开发

### 提交代码

#### 1. Fork项目并克隆

```bash
git clone https://github.com/your-username/AutoSlideGen.git
cd AutoSlideGen
```

#### 2. 创建开发环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
pip install -e .
```

#### 3. 创建特性分支

```bash
git checkout -b feature/your-feature-name
```

#### 4. 进行开发

- 遵循项目的代码风格
- 添加必要的测试
- 更新相关文档

#### 5. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_models.py

# 查看覆盖率
pytest --cov=autoslidegen tests/
```

#### 6. 代码格式化

```bash
# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/

# 类型检查
mypy src/
```

#### 7. 提交更改

```bash
git add .
git commit -m "feat: 添加某某功能"
```

提交信息格式:
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建或辅助工具

#### 8. 推送并创建Pull Request

```bash
git push origin feature/your-feature-name
```

然后在GitHub上创建Pull Request。

## 代码规范

### Python代码风格

- 遵循 PEP 8
- 使用 Black 进行格式化
- 使用类型提示
- 编写清晰的docstring

示例:

```python
def generate_outline(
    topic: str,
    audience: str,
    num_slides: int = 10
) -> PresentationOutline:
    """
    Generate presentation outline from topic.

    Args:
        topic: The presentation topic
        audience: Target audience
        num_slides: Number of slides to generate

    Returns:
        PresentationOutline instance

    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation
    pass
```

### 测试

- 为新功能编写测试
- 保持测试覆盖率 > 80%
- 使用有意义的测试名称
- 测试边界情况

示例:

```python
def test_valid_outline_generation():
    """Test generating a valid outline."""
    generator = AutoSlideGen()
    result = generator.generate(
        topic="Test Topic",
        audience="Test Audience",
        purpose="Test Purpose"
    )
    assert result['outline'] is not None
    assert len(result['outline'].slides) > 0
```

### 文档

- 更新README如果改变了用户接口
- 为新功能添加示例
- 保持文档与代码同步
- 使用清晰的中英文文档

## 项目结构

```
AutoSlideGen/
├── src/autoslidegen/          # 核心代码
│   ├── outline_generator/     # 大纲生成
│   ├── parser/               # 解析验证
│   ├── ppt_builder/          # PPT构建
│   └── utils/                # 工具函数
├── tests/                    # 测试代码
├── examples/                 # 示例代码
└── docs/                     # 文档
```

## 开发流程

1. **讨论** - 在Issue中讨论想法
2. **开发** - 在特性分支上开发
3. **测试** - 确保所有测试通过
4. **文档** - 更新相关文档
5. **审查** - 提交PR等待审查
6. **合并** - 审查通过后合并

## 版本发布

版本号遵循语义化版本规范（Semantic Versioning）:

- 主版本号: 不兼容的API变更
- 次版本号: 向后兼容的功能新增
- 修订号: 向后兼容的问题修正

## 行为准则

- 尊重所有贡献者
- 欢迎建设性的批评
- 专注于对项目最好的决策
- 展现同理心和善意

## 许可证

贡献的代码将在MIT许可证下发布。

## 联系方式

- GitHub Issues: 技术问题和bug报告
- Pull Requests: 代码贡献
- Discussions: 一般性讨论

## 致谢

感谢所有贡献者的付出！

你的名字将出现在项目的贡献者列表中。
