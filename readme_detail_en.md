# Building the "Digital Life" Service

## Precautions

⚠ **Important:** If you are a beginner, please open the terminal (Win11) or Powershell (Win10) or Terminal (Linux) **at the location where you need to store this project**, and **follow the steps below**. Before starting, make sure that [Git](https://git-scm.com/downloads/) and [Conda](https://www.anaconda.com/download/success) are installed on your computer.

## Installation Steps

### Clone the Repository

```bash
git clone https://github.com/RiderWhirl/Digital_Life_Server-multi-thread.git --recursive
cd Digital_Life_Server
mkdir tmp
mkdir BERT
```

### Configure the Environment

#### 1. Create a Python Virtual Environment Using Conda

```bash
conda create --name py39 python=3.9
```

#### 2. Install PyTorch in the `py39` Environment

- Activate the `py39` environment
  ```bash
  conda activate py39
  ```
- Check the CUDA version (for computers with Nvidia GPUs)
  ```bash
  nvcc --version
  ```

**For computers with Nvidia GPUs (install torch with CUDA 11.8):**

- Default URL
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- Domestic accelerated URL (may download faster)
  ```bash
  pip install torch==2.0.0+cu118 torchvision torchaudio -f https://mirror.sjtu.edu.cn/pytorch-wheels/torch_stable.html
  ```

**For computers without Nvidia GPUs (install CPU-only torch):**

- Default URL
  ```bash
  pip install torch torchvision torchaudio
  ```
- Domestic accelerated URL (may download faster)
  ```bash
  pip install torch==2.0.0+cpu torchvision torchaudio -f https://mirror.sjtu.edu.cn/pytorch-wheels/torch_stable.html
  ```

- [Other Version Combination Guide (pytorch.org)](https://pytorch.org/get-started/locally)

#### 3. Install Other Required Dependencies

- Linux:
  First, install portaudio
  ```bash
  apt install portaudio19-dev  #Ubuntu
  # yum install portaudio-devel  #CentOS
  ```
  Then install other dependencies
  ```bash
  pip install -r requirements_linux.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- Windows:
  ```bash
  pip install -r requirements_out_of_pytorch.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

#### 4. Build the Corresponding Version of `monotonic_align`

```bash
cd "TTS/vits/monotonic_align"
mkdir monotonic_align
python setup.py build_ext --inplace
cp monotonic_align/*.pyd ./ # For Linux, change to cp monotonic_align/*.so
```

#### 5. For Computers Without Nvidia GPUs (Skip This Step if You Have an Nvidia GPU)

- Modify three places in the `Digital_Life_Server\TTS\TTService.py` file, changing `.cuda()` to `.to('cpu')` or `.cpu()`

> At this point, the project setup is complete.

#### 6. Download the Required Models for the Project

- [Baidu Netdisk](https://pan.baidu.com/s/1BkUnSte6Zso16FYlUMGfww?pwd=lg17)
- [Aliyun Drive](https://www.aliyundrive.com/s/jFvgsJVtV6g)
- [Google Drive](https://drive.google.com/drive/folders/1Jpn8d1g3uQp6wfS0wulri8mQs8Ete1Oj?usp=drive_link)
- [BERT Model (huggingface.co)](https://huggingface.co/google-bert/bert-base-chinese/tree/main)
    - ASR Model: Place in `/ASR/resources/models`
    - Sentiment Model: Place in `/SentimentEngine/models`
    - TTS Model: Place in `/TTS/models`
    - BERT Model: Download config.json, Pytorch_model.bin, tokenizer_config.json, vocab.txt and place in `/BERT`

## Launch the "Digital Life" Server

⚠ **Note:** Before launching, please modify the specific configurations in the bat or sh files according to your actual situation and configure the relevant environment variables.

```bash
run-gpt3.5-api.bat # Windows
run-gpt3.5-api.sh  # Linux
```

or

```bash
run-deepseek-api.bat # Windows
run-deepseek-api.sh  # Linux
```

#### All Parameters

| Name          | Description                  | Remarks                                                                             | Required               |
|---------------|-----------------------------|-------------------------------------------------------------------------------------|------------------------|
| APIKey        | Application Key             | OPENAI_API_KEY, ERINEBot_API_Key                                                    | ERINEBot, ChatGPT      |
| SecretKey     | ERINEBot Secret Key         | ERINEBot Secret Key                                                                | ERINEBot               |
| accessToken   | Session Token               | [ERNIEBot accessToken](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Ilkkrb0i5)     |                        |
| proxy         | Proxy Service Address       | ChatGPT proxy service address, e.g., http://127.0.0.1:7890                          |                        |
| brainwash     | Brainwash Mode              | Not recommended to enable, only effective for ERNIEBot                              |                        |
| model         | Model to Call               | Specifies the GPT model to use, options: gpt-3.5-turbo, gpt-4, ERNIEBot, ERNIEBot-4 | ALL                    |
| stream        | Stream Response             | Can effectively reduce response time, options: True, False                          | ALL                    |
| character     | Character to Use            | Specifies the character to use, options: paimon, yunfei, catmaid                    | ALL                    |

### Example Calls

- Example of calling ChatGPT from the command line:
  ```bash
  python SocketServer.py --APIKey %OPENAI_API_KEY%  --proxy http://127.0.0.1:7890 --stream false --model gpt-3.5-turbo --character paimon
  ```
- Example of calling Deepseek from the command line:
  ```bash
  python SocketServer.py --APIKey %Deepseek API Key% --stream false  --model deepseek-chat --character paimon
  ```
- Example of calling ERNIEBot from the command line:
  ```bash
  python SocketServer.py --stream true  --SecretKey %ERINEBot_SecretKey% --APIKey %ERINEBot_API_Key % --model ERNIEBot-4 --character paimon
  ```
