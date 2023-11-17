# Digital Life Server

这个仓库包含了与"数字生命"服务相关的代码，涵盖与前端通信、语音识别、ChatGPT集成和语音合成。

有关项目的其他部分，请参考：

- [Launcher](https://github.com/LIEGU0317/DL_Launcher): 用于启动此服务器的图形界面。（非必要）
- [UE Client](https://github.com/LIEGU0317/DigitalLife): 用于渲染人物动画、录音和播放声音的前端部分。

有关详细配置流程，请参阅[readme_detail.md](readme_detail.md)。

## 准备开始：

### 克隆此仓库

> 确保使用了[`--recursive`](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)参数克隆代码。

```bash
git clone https://github.com/liegu0317/Digital_Life_Server.git --recursive
```

### 安装先决条件

1. 安装PyTorch
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

2. 安装其他依赖项
    ```bash
    pip install -r requirements.txt
    ```

3. 构建`monotonic_align`  
   这一步可能并不完美，但你知道它应该是什么意思。
   ```bash
   cd "TTS/vits/monotonic_align"
   mkdir monotonic_align
   python setup.py build_ext --inplace
   cp monotonic_align/*.pyd .
   ```

4. 下载模型  
   [百度网盘](https://pan.baidu.com/s/1EnHDPADNdhDl71x_DHeElg?pwd=75gr)
   - ASR模型：放置到`/ASR/resources/models`目录下
   - Sentiment 模型：放置到`/SentimentEngine/models`目录下
   - TTS模型：放置到`/TTS/models`目录下

5. （对于**没有**Nvidia显卡的电脑，采用CPU来运行的情况）需要额外的步骤：

   修改 `Digital_Life_Server\TTS\TTService.py` 文件下：
   ```
   self.net_g = SynthesizerTrn(...).cuda()
   修改为
   self.net_g = SynthesizerTrn(...).cpu()
   ```

> 至此，项目已经搭建完成 🥰

### 启动服务器

```bash
run-gpt3.5-api.bat # run-gpt3.5-api.sh
```