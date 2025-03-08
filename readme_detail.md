# 搭建”数字生命“服务

## 注意事项

⚠ **重要：** 如果你是初学者，请在**需要存放该项目的位置**打开终端（Win11）或Powershell（Win10）或Terminal（Linux），并**按照以下步骤操作
**
。在开始前，请确保电脑中已安装[Git](https://git-scm.com/downloads/)和[Conda](https://www.anaconda.com/download/success)。

## 安装步骤

### 克隆仓库

```bash
git clone https://github.com/RiderWhirl/Digital_Life_Server-multi-thread.git --recursive
cd Digital_Life_Server
mkdir tmp
mkdir BERT
```

### 配置环境

#### 1. 使用conda建立Python虚拟环境

```bash
conda create --name py39 python=3.9
```

#### 2. 安装pytorch于`py39`环境

- 激活`py39`环境
  ```bash
  conda activate py39
  ```
- 检查cuda版本（对于拥有Nvidia显卡的电脑）
  ```bash
  nvcc --version
  ```

**对于拥有Nvidia显卡的电脑（安装cuda11.8版本的torch）：**

- 默认地址
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- 国内加速地址（下载可能较快）
  ```bash
  pip install torch==2.0.0+cu118 torchvision torchaudio -f https://mirror.sjtu.edu.cn/pytorch-wheels/torch_stable.html
  ```

**对于没有Nvidia显卡的电脑（安装CPU版本的torch）：**

- 默认地址
  ```bash
  pip install torch torchvision torchaudio
  ```
- 国内加速地址（下载可能较快）
  ```bash
  pip install torch==2.0.0+cpu torchvision torchaudio -f https://mirror.sjtu.edu.cn/pytorch-wheels/torch_stable.html
  ```

- [其他版本组合指南（pytorch.org）](https://pytorch.org/get-started/locally)

#### 3. 安装项目所需其它依赖项

- Linux：
  先安装portaudio
  ```bash
  apt install portaudio19-dev  #Ubuntu
  # yum install portaudio-devel  #CentOS
  ```
  然后安装其他依赖
  ```bash
  pip install -r requirements_linux.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- Windows：
  ```bash
  pip install -r requirements_out_of_pytorch.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

#### 4. 构建相应版本的 `monotonic_align`

```bash
cd "TTS/vits/monotonic_align"
mkdir monotonic_align
python setup.py build_ext --inplace
cp monotonic_align/*.pyd ./ # linux修改为cp monotonic_align/*.so
```

#### 5. 对于没有Nvidia显卡的电脑（拥有Nvidia显卡的电脑跳过此步）

- 修改 `Digital_Life_Server\TTS\TTService.py` 文件中三处，将 `.cuda()` 改为 `.to('cpu')`或`.cpu()`

> 到此，项目构建完毕。

#### 6. 下载项目所需模型

- [百度网盘](https://pan.baidu.com/s/1BkUnSte6Zso16FYlUMGfww?pwd=lg17)
- [阿里云盘](https://www.aliyundrive.com/s/jFvgsJVtV6g)
- [Google Drive](https://drive.google.com/drive/folders/1Jpn8d1g3uQp6wfS0wulri8mQs8Ete1Oj?usp=drive_link)
- [BERT Model(huggingface.co)](https://huggingface.co/google-bert/bert-base-chinese/tree/main)
    - ASR Model: 放置于 `/ASR/resources/models`
    - Sentiment Model: 放置于 `/SentimentEngine/models`
    - TTS Model: 放置于 `/TTS/models`
    - BERT Model: 下载 config.json，Pytorch_model.bin，tokenizer_config.json，vocab.txt 后放置于 `/BERT`

## 启动“数字生命”服务器

⚠ **注意：** 启动前，请根据实际情况修改bat或sh文件的具体配置以及配置相关环境变量。

```bash
run-gpt3.5-api.bat # Windows
run-gpt3.5-api.sh  # Linux
```

或

```bash
run-deepseek-api.bat # Windows
run-deepseek-api.sh  # Linux
```

#### 全部参数

| 名称          | 描述                  | 备注                                                                             | 必填               |
|-------------|---------------------|--------------------------------------------------------------------------------|------------------|
| APIKey      | 应用秘钥                | OPENAI_API_KEY、ERINEBot_API_Key                                                | ALL |
| SecretKey   | ERINEBot Secret Key | ERINEBot Secret Key                                                            | ERINEBot         |
| accessToken | 会话标志码               | [ERNIEBot accessToken](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Ilkkrb0i5) |
| proxy       | 代理服务地址              | 使用 ChatGPT 时代理服务的地址，例如 http://127.0.0.1:7890                                        |                  |
| brainwash   | 洗脑模式                | 不推荐开启，仅ERNIEBot有效                                                              |                  |
| model       | 调用的模型               | 指定使用的GPT模型，可选值：gpt-3.5-turbo、gpt-4、deepseek-chat、deepseek-reasoner、ERNIEBot、ERNIEBot-4                         | ALL              |
| stream      | 流式回复                | 可有效减少响应时间，可选值：True、False                                                       | ALL              |
| character   | 使用的角色               | 指定所使用的角色，可选值：paimon、yunfei、catmaid                                             | ALL              |

### 调用示例

- 调用ChatGPT命令行示例：
  ```bash
  python SocketServer.py --APIKey %OPENAI_API_KEY%  --proxy http://127.0.0.1:7890 --stream false --model gpt-3.5-turbo --character paimon
  ```
- 调用Deepseek命令行示例：
  ```bash
  python SocketServer.py --APIKey %Deepseek API Key% --stream false  --model deepseek-chat --character paimon
  ```
- 调用ERNIEBot命令行示例：
  ```bash
  python SocketServer.py --stream true  --SecretKey %ERINEBot_SecretKey% --APIKey %ERINEBot_API_Key % --model ERNIEBot-4 --character paimon
  ```
