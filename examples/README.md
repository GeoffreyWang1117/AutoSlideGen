# AutoSlideGen 示例文件 (Examples)

本目录包含AutoSlideGen的使用示例，演示各种功能的用法。

## 批量生成 (Batch Generation)

### CSV格式批量生成

**文件**: `batch_requests.csv`

CSV格式允许您使用电子表格工具（如Excel、Google Sheets）轻松创建和编辑批量请求。

**CSV格式说明**:
```csv
topic,audience,purpose,language,num_slides,bullets_per_slide,additional_requirements
主题,目标受众,演示目的,语言代码,幻灯片数量,每页要点数,额外要求
```

**使用方法**:
```bash
autoslidegen batch batch_requests.csv --output-dir ./presentations
```

**高级选项**:
```bash
# 使用并行处理（默认）
autoslidegen batch batch_requests.csv --parallel --max-workers 5

# 使用串行处理
autoslidegen batch batch_requests.csv --sequential

# 指定LLM提供商
autoslidegen batch batch_requests.csv --provider openai

# 不保存JSON outline
autoslidegen batch batch_requests.csv --no-json
```

### JSON格式批量生成

**文件**: `batch_requests.json`

JSON格式提供更结构化的方式来定义批量请求，适合程序化生成。

**JSON格式说明**:
```json
{
  "requests": [
    {
      "topic": "演示主题",
      "audience": "目标受众",
      "purpose": "演示目的",
      "language": "zh",
      "num_slides": 10,
      "bullets_per_slide": 4,
      "additional_requirements": "额外要求（可选）"
    }
  ]
}
```

**使用方法**:
```bash
autoslidegen batch batch_requests.json --output-dir ./presentations
```

### 批量生成输出

批量生成完成后，会在输出目录生成以下内容：

```
output/batch_20231122_143000/
├── 001_人工智能技术概览.pptx
├── 002_Cloud_Computing_Basics.pptx
├── 003_区块链应用场景.pptx
├── 004_Machine_Learning_Fundamentals.pptx
├── 005_网络安全最佳实践.pptx
├── batch_report.json          # 详细的JSON报告
└── batch_summary.txt          # 文本格式摘要
```

**batch_report.json** 包含:
- 每个生成任务的详细结果
- 成功和失败的统计信息
- 每个演示文稿的文件路径
- 生成耗时和性能指标

**batch_summary.txt** 包含:
- 批量生成概要
- 成功和失败的列表
- 平均生成时间

### 性能优化建议

1. **并行处理**: 使用 `--parallel` 可显著提升速度
   - 推荐 `--max-workers 3-5` (取决于API限制)
   - 注意LLM API的速率限制

2. **缓存利用**: 相同参数的请求会自动使用缓存
   - 减少API调用
   - 降低成本
   - 提升速度

3. **批量大小**: 建议每批10-50个请求
   - 太小: 效率低
   - 太大: 失败风险高

### 常见问题

**Q: 批量生成中途失败怎么办？**

A: 批量生成会记录所有成功和失败的任务。您可以：
1. 查看 `batch_report.json` 了解失败原因
2. 创建新的CSV/JSON文件，只包含失败的请求
3. 重新运行批量生成

**Q: 如何估算批量生成时间？**

A: 一般情况下:
- 无缓存: 每个演示文稿 5-15秒
- 有缓存: 每个演示文稿 < 1秒
- 并行处理可减少总时间50-70%

**Q: 批量生成支持哪些语言？**

A: 支持所有AutoSlideGen支持的语言:
- `zh`: 中文
- `en`: 英文
- `ja`: 日文
- `es`: 西班牙文

## 更多示例

更多使用示例请参考主文档：
- [README.md](../README.md)
- [QUICKSTART.md](../QUICKSTART.md)
- [EXTENSIONS.md](../EXTENSIONS.md)
