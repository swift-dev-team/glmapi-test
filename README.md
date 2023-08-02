# glmapi 项目测试计划
## 测试说明
### 文件测试 `file_action`
1. 文件上传测试
2. 文件修改测试
3. 文件删除测试
#### 说明
该测试依赖 `data/input/1` 中的文件

### 生成测试 `generate`
1. 开发信生成测试
1. 邮件摘要测试
2. 邮件回复摘要测试
3. 邮件回复测试
#### 说明
在 `data/input/2` 中添加更多的邮件内容，以进行更多的测试

## 使用方法
1. 安装依赖
    ```python
    pip install -r requirements.txt
    ```

2. 测试文件相关功能
    ```python
    python src/file_action.py
    ```

3. 测试邮件生成功能
    ```python
    python src/generate.py
    ```
