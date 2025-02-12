# OFA

论文： [OFA: Unifying Architectures, Tasks, and Modalities Through a Simple Sequence-to-Sequence Learning Framework](https://arxiv.org/abs/2202.03052)

在这项工作中，我们追求一种统一的多模态预训练范式，以打破复杂的任务/模态特定定制的支架。我们提出了OFA，一个支持任务全面性的任务无关性和模态无关性框架。OFA在一个简单的seq2seq的学习框架中统一了不同的跨模态和单模态的任务，包括图像生成、视觉定位、图像说明、图像分类、语言模型等。OFA在预训练和微调阶段都遵循基于指令的学习，不需要为下游任务提供额外的特定任务层。与最近的最先进的视觉和语言模型相比，OFA只在2000万个公开的图像-文本对上进行了预训练，这些模型依赖于极其庞大的跨模态数据集。尽管其简单性和相对较小的训练数据，OFA在一系列跨模态任务中取得了新的SOTA，同时在单模态任务中获得了极具竞争力的表现

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/b8958894-44ba-4dbe-8142-e7d30c41025a"/>
</div>

OFA 支持的任务如上所示。

模型架构如下所示：

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/ff372f80-a704-48e6-aeee-4971e005db05"/>
</div>

可以看到架构是 a unified Seq2Seq framework。

图像 embedding 选择 ResNet, 文本分词选择 BPE。

如何统一各种模态的输入和输出？ 输入比较好统一，主要关注模态输出。一个可能的解决方案是将文本、图像和object离散化，并在一个统一的单词表中用 token 表示它们。

在文生图领域，已经有图片量化策略来实现这个功能了，可以借助这个策略实现图像 token 化。例如，256 × 256 分辨率的图像表示为长度为 16 × 16 的代码序列。每个离散代码与相应的补丁密切相关

bbox 模态表示就比较容易了，表示为一连串的离散标注，每个标注对应一个 bbox，bbox 整数坐标本质上是单词，因此可以用BPE标注表示。

最后统一词表是文本的subwords，图片的image code和物体的location tokens三者的并集。

我们选择Transformer作为主干架构，并采用编码器-解码器框架作为所有预训练、微调和zero-shot任务的统一架构。具体来说，编码器和解码器都是Transformer层的堆叠。

因为他是一个 seq2seq 任务，以 object 检测为例，他可能并不是总输出有效的 token，因此在推理时候要处理下。在分类任务中存在几个问题： 1.对整个词汇表进行优化是不必要的，而且是效率低下的；2.在推理过程中，该模型可能会从封闭的标签集中产生无效的标签。为了克服这些问题，引入一种基于前缀树的搜索策略。

预训练数据如下：

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/bd96c0be-2e4d-401d-b4dc-830fd8cc0248"/>
</div>

下游任务微调也是采用和预训练一样的模式即采用指令微调学习。

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/be6c2a55-462e-4eca-b337-b8cef5a8dae7"/>
</div>

# MMGPT

Train a multi-modal chatbot with visual and language instructions!

开源地址：https://github.com/open-mmlab/Multimodal-GPT

基于开源的多模态模型 OpenFlamingo，使用开放数据集创建了各种视觉指导数据，包括 VQA、图像字幕、视觉推理、文本 OCR 和视觉对话。此外还使用仅语言指导数据训练了 OpenFlamingo 的语言模型组件。 视觉和语言指导的联合训练有效提高了模型的性能！

## 环境安装

```shell
git clone https://github.com/open-mmlab/Multimodal-GPT.git
cd Multimodal-GPT
conda create -n mmgpt python=3.8 -y
conda activate mmgpt
pip install -r requirements.txt
pip install -e . -v
```
环境安装可能需要一定时间，因为库比较多。 下面以 Linux 为例

## 权重准备

最终结构应该是：

```text
Multimodal-GPT/checkpoints
├── llama-7b_hf
│   ├── config.json
│   ├── pytorch_model-00001-of-00002.bin
│   ├── ......
│   └── tokenizer.model
├── OpenFlamingo-9B
│   └──checkpoint.pt
├──mmgpt-lora-v0-release.pt
```

**(1) llama-7b_hf 下载**

需要先安装 git-lfs, 你可以去 https://github.com/git-lfs/git-lfs/releases 下载安装包

```shell
wget https://github.com/git-lfs/git-lfs/releases/download/v2.13.1/git-lfs-linux-amd64-v2.13.1.tar.gz
tar -xzvf git-lfs-linux-amd64-v2.13.1.tar.gz
cd git-lfs-2.13.1
sudo ./install.sh
```

安装好后，可以直接下载权重

```shell
git clone https://huggingface.co/decapoda-research/llama-7b-hf
```
上述权重大概 26G(7B fp32 模型参数量的存储空间为 4B* 70 亿 = 28 GB 实际下载大概 26 G)

下载后需要修改类名，否则后续会报错：

```shell
cd llama-7b-hf
vim tokenizer_config.json # 将 LLaMATokenizer 修改为 LlamaTokenizer
```

上述只是一个典型的别人弄好的 HF FP32 权重，实际上网上还是很多版本的，大家都可以尝试一下。

**(2) OpenFlamingo-9B 下载**

```shell
git lfs install
git clone https://huggingface.co/openflamingo/OpenFlamingo-9B
```

需要输入 huggingface 账号的用户名和密码。如果实在是下载不了，可以直接登录网页点击下载。

**(3) mmgpt-lora-v0-release.pt 下载**

```shell
wget https://download.openmmlab.com/mmgpt/v0/mmgpt-lora-v0-release.pt
```

## 运行 Demo

```shell
python app.py
```
        
第一次运行会自动下载 CLIP 权重，正常启动后会出现浏览器地址，也会生成一个临时的可以公开访问的地址。界面如下所示：

<div align=center>
<img src="https://user-images.githubusercontent.com/17425982/234834321-e0a958c9-7552-497b-aae4-2f664f748fb5.png"/>
</div>

这个 LLM 的一大特点是无敌自信，不管你咋说他错了，他都告诉你我没有错(其他 LLM 都是立刻道歉，并给出别的答案)。～～～

# MiniGPT-4

## 环境安装
基础环境： CentOS 7 + 32G V100 

**(1) 安装基础环境**

```shell
git clone https://github.com/Vision-CAIR/MiniGPT-4.git
cd MiniGPT-4
conda env create -f environment.yml
conda activate minigpt4
```

**(2) 安装 git-lfs**

如果你已经安装好了，可以跳过这一步，如果你是其他系统，则应该选择其他安装命令，以下为 centos 7 安装命令：

```shell
wget https://packagecloud.io/github/git-lfs/packages/el/7/git-lfs-2.13.2-1.el7.x86_64.rpm/download # 或者直接下载
sudo rpm -ivh git-lfs-2.13.2-1.el7.x86_64.rpm
```

**(3) 准备 vicuna-13b 权重**

你需要下载 vicuna-13b-delta-v0 和 llama-13b-hf 两个权重，然后合并。

注意： 虽然 vicuna 模型是基于 llama 的全量微调，但是由于 llama 协议限制，作者无法直接发布 vicuna 全量模型，因此作者先手动减掉了 llama 权重，然后发布了 vicuna-13b-delta-v0 权重，因此你需要先下载这个权重，然后再和 llama-13b-hf 权重合并。

```shell
git clone https://huggingface.co/lmsys/vicuna-13b-delta-v0 # 大概 49G
git clone https://huggingface.co/decapoda-research/llama-13b-hf  # 大概 75G
```

下载后需要修改类名，否则后续会报错：

```shell
cd llama-13b-hf
vim tokenizer_config.json # 将 LLaMATokenizer 修改为 LlamaTokenizer
```

**(4) 权重合并得到 vicuna-13b**

首先安装 FastChat

```shell
pip install git+https://github.com/lm-sys/FastChat.git@v0.1.10
```

然后运行

```shell
python -m fastchat.model.apply_delta \
    --base 你的路径/llama-13b-hf \
    --target 你的路径/vicuna-13b \  # 合并后为 37G
    --delta 你的路径/vicuna-13b-delta-v0 
```

最后修改 https://github.com/Vision-CAIR/MiniGPT-4/blob/main/minigpt4/configs/models/minigpt4.yaml#L16 为你的 vicuna-13b 路径

**(5) 下载 minigpt-4 预训练的权重**

去 https://drive.google.com/file/d/1a4zLvaiDBr-36pasffmgpvH5P7CKmpze/view?usp=share_link 下载 13b 的权重

然后修改 https://github.com/Vision-CAIR/MiniGPT-4/blob/main/eval_configs/minigpt4_eval.yaml#L11 为你自己的路径

## 环境启动

```shell
python demo.py --cfg-path eval_configs/minigpt4_eval.yaml  --gpu-id 0
```

如果出现如下错误： `NameError: name 'cuda_setup' is not defined`
请使用如下命令修复：  `pip install bitsandbytes==0.35.0`

如果出现如下错误： `ERROR: Your GPU does not support Int8 Matmul!`
请修改 https://github.com/Vision-CAIR/MiniGPT-4/blob/main/eval_configs/minigpt4_eval.yaml#L8 将 low_resource 设置为 False

## 效果展示

<div align=center>
<img src="https://github.com/Vision-CAIR/MiniGPT-4/assets/17425982/4408fe44-4293-497e-a30e-96e4b45b337f"/>
</div>

英文效果不错，直接就知道是来自哪一部漫画。

<div align=center>
<img src="https://github.com/Vision-CAIR/MiniGPT-4/assets/17425982/b00cf85d-e327-45f8-a80d-30b71de7f564"/>
</div>

中文效果差点，在经过提示了可以回答出来。

OCR 任务也还行

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/c5c01053-f408-4df3-bd2e-eb1283c1363b"/>
</div>

整体来说 minigpt-4 13b 模型效果还是非常 ok 的。

# VisionLLM

论文： [VisionLLM: Large Language Model is also an Open-Ended Decoder for Vision-Centric Tasks](https://arxiv.org/abs/2305.11175)
暂时还没有开源

和 OFA 非常类似，但是模型做的更大，性能更高，同时接入了羊驼 LLM, 还可以对话啥的。没有实现通用图像分割。下面详细描述。

VisionLLM 的核心意图是一个模型可以做多种视觉和语言任务，架构统一，输入和输出也统一，不需要对不同的下游任务构建不同的输入或者增加模型等。

如果你了解 OFA，那么这个模型就比较好理解了。

结构图如下所示：

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/80a54c4b-1acf-40eb-a0df-6fb1177a89c8"/>
</div>

包括 3 个模块：

- 一个统一的语言指令，为以视觉为中心的任务定义和定制提供一致的输入。简单来说就是类似 OFA 通过语言构建统一的不同任务的输入，例如图片理解任务， Describe the image <image> in details.  <image> 是 image embedding 的占位符
- 一个语言导向的图像 tokenizer，它对视觉信息进行编码，与给定的语言提示保持一致，使模型能够有效地理解和解析视觉内容； 其实就是 image embedding 转 lang feature
- 基于 LLM 的开放式任务解码器，它利用编码的视觉信息和语言指令来产生令人满意的预测或输出。 解码器是核心，也是和 OFA 不一样的主要地方。

这三种设计共同实现了一个灵活和开放的框架，可以处理各种以视觉为中心的任务，并通过语言指令进行不同程度的任务定制。通过语言指令进行任务定制。

注意：基于 LLM 的开放式任务解码器采用的是类似 DETR Query 的模式，并不是 seq2seq 输出是并行的，因此相比 OFA 效率更好。输入 Query 就是上图中的 Language Instructions <text>。下面详细说明

## 统一的语言指令
参考之前论文做法，

Vision-Language Tasks

- image captioning： The image is <image>. Please generate a caption for the image: 
- VQA：The image is <image>. Please generate an answer for the image according to the question: <question>

Vision-Only Tasks

典型的如目标检测、实例分割和姿态估计等，考虑到用户描述的不同，作者采用了 self-instruct 方法基于一些样例生成了大量的对应任务描述，训练时候随机选择一个构成训练样本。推理时候一个实例分割语义描述的例子是：

Segment all the objects of category set <class> within the <range> of the image and generate a list of the format
(c, x1, y1, x2, y2, ..., x8, y8). Here, c represents the index of the class label starting from 0, and (x1, y1, x2, y2, ..., x8, y8) correspond to the offsets of boundary points of the object relative to the center  point. The image is: <image>

range 设置为 512。

## 语言导向的图像 tokenizer

VisionLLM 认为相对于语言信息，图像是一种外语，需要将其转换为能被 llm 理解的 token。具体做法是：

1. 先用 image  backbones 对图片进行特征提取，得到多尺度图片特征
2. 使用 text encoder 提取文本特征
3. 通过交叉注意力将语言特征注入到每个尺度的视觉特征中，产生多尺度的语言感知视觉特征，使特征在不同的模式中保持一致。跨模态的特征
4. 将融合后的多尺度特征输入到 Deformable DETR Encoder 中，这个做法和 Mask2Former 是类似的

上述步骤就可以得到序列长度为 M 的图片 token

## 基于 LLM 的开放式任务解码器

Decoder 是采用 LLM 结构，实际上就是 Alpaca。但是对于以视觉为中心的任务，Alpaca 有一些固有的缺点。

(1) 它的词汇表中只有几个数字标记（如0∼9），这限制了它通过数字定位物体的能力；
(2) 它使用多个标记来表示类别名称和类名，这导致了一种低效的方案。
(3) 它是一个因果模型，对于视觉感知任务来说是低效的。在视觉感知任务中效率低下

作者的做法是扩展词汇表，增加了专门为视觉中心任务设计的标记，为以视觉为中心的任务而设计的额外标记。

- 增加了一组位置标记，表示为 {<p-512>, ..., <p0>..., <p512>}、 ..., <p512>}，其中 <p i> 表示离散偏移量。
- 我们引入了语义无关的分类代号{<c0>, <c1>, ..., <c511>}来代替类别名称代号，这就克服了使用多个代号来表示的低效率问题。例如{"人"：<c0>，"车"：<c1>，"黑猫"：<c2>，...}

为了出来语言模型串行输出低效问题，改成了采用 query 的并行预测。query 并不是随机初始化的，而是和具体任务有关系，如图所示：

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/0b161823-db61-420a-aca1-b61b7035eca9"/>
</div>

具体实现过程可能要等开源后。训练的 loss 比较简单，因为就是一个分类任务，采用 cross entropy loss。

## 训练细节

训练数据包括 object detection, instance segmentation, visual grounding, image captioning, and visual question answering 方向，具体是：

- COCO2017
- RefCOCO
- RefCOCO+
- RefCOCOg
- COCO Caption
- LLaVA-Instruct-150K

用两个图像骨干实现了VisionLLM的两个变体，即ResNet和InternImage-H。对于语言引导的图像标记器，我们采用 BERTBase作为文本编码器和 Deformable DETR（D-DETR）来捕获高级信息。
我们将查询次数 M 设定为 100，D-DETR的编码/解码器层数为6。对于LLM，我们采用了Alpaca-7B[，并配备了LoRA进行参数有效的微调。

该模型的训练分为两个阶段。在第一阶段，我们用预先训练好的D-DETR、BERT和Alpaca-7B的权重初始化模型，并训练视觉骨干和语言引导的图像标记器，同时冻结LLM的大部分参数，只有少数LoRA参数除外。为了简化训练的复杂性，在这个阶段，我们主要关注具有随机物体类别和任务描述的物体检测任务。在第二阶段，我们冻结了视觉主干，并引入了多个任务的统一监督。引入对多个任务的统一监督。除非另有说明，训练运行的时间为在4×8的NVIDIA A100 GPU上运行50个epochs。

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/98277983-873d-45e7-bc55-898926538f2e"/>
</div>

一些例子：

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/a5d5f11b-7d2a-42d7-ad40-2cc79ee51d29"/>
</div>

<div align=center>
<img src="https://github.com/open-mmlab/mmpretrain/assets/17425982/418dc07e-9401-4b0f-8d3f-3dab5a73f58d"/>
</div>

总的来说是一个不错的工作，期待后续开源。

# PaLI-X

[PaLI-X: On Scaling up a Multilingual Vision and Language Model](https://arxiv.org/abs/2305.18565)

很强。

摘要： 本文介绍了 PaLI-X，一种多语言视觉和语言模型的训练方法和结果，涉及模型尺度大小和训练任务混合。我们的模型在各种各样的任务中取得了新的性能水平，包括多个基于图像的图像理解和问答任务、基于图像的文档理解和少样本（上下文内）学习，以及目标检测、视频问答和视频字幕等任务。PaLI-X 在大多数视觉和语言基准测试中都取得了最新的研究成果（超过25个基准测试）。最后，我们观察到新兴的能力，如复杂计数和多语言目标检测，这些任务并未明确纳入训练组合中。

consisting of a pretrained large-capacity visual encoder (using Scaling vision transformers to 22 billion parameters as the starting point) and a pretrained language-only encoder-decoder (using UL2: Unifying language learning paradigms as the
starting point), further trained at-scale on a vision-and-language data mixture using a combination of self-supervision and full-supervision signals

需要先了解 [PaLI: A jointly-scaled multilingual language-image model](https://ai.googleblog.com/2022/09/pali-scaling-language-image-learning-in.html)

我们观察到，scaling 可以大大改善 PaLI 模型的结果，而且比专门针对某些任务进行训练的专用大模型的结果要好，这些模型通常是通过（往往更大的）仅文本 LLM 的帮助来解决问题的。也就是说多模训练更好，而且模型越大效益越大。也有类似的涌现效果。

总的贡献如下：

1. 我们扩展了一个视觉-语言模型，以在各种基准测试中实现出色的性能。我们观察到，扩展视觉和语言组件都是有利的，并且报告称，在这个规模下性能仍未饱和。
2. 我们展示了用一种混合目标的训练方法来训练这样的模型，该方法结合了 prefix-completion and masked-token completion，可以在这个规模下提高微调和少样本性能的 Pareto 前沿。
3. 我们还展示了高容量视觉编码器（ViT-22B）可以有效地进行共同训练，用于图像分类和OCR标签分类，以在需要理解图像文本的视觉-语言任务上实现显着的改进。
4. 总的来说，PaLI-X 通过对15个以上基准测试进行微调来改进SoTA结果，并且我们展示了它是第一个能够同时适应多个基准测试的模型，而且没有明显的性能下降。

采用了非常大的 ViT-22B 作为视觉编码器，以及 UL2 作为语言编码器，输出也是文本。目标检测建模为 pix2seq 任务，使用 图片的 OCR 文字作为预训练数据集，然后在各个下游任务上微调，同时也支持 few-shot 推理。

# ChatSpot
8月估计开源，论文也还没有公开

# Kosmos-2

Kosmos-2: Grounding Multimodal Large Language Models to the World

https://arxiv.org/abs/2306.14824
https://github.com/microsoft/unilm/tree/master/kosmos-2

非常好！

一个多模态大语言模型（MLLM），使多模态大语言模型（MLLM）实现了感知物体描述（如边界框）的新能力，并将文本与视觉世界联系起来。MLLM 支持 bbox+text 输出，也支持 bbox+text 输出。

提出了一个新的大规模数据集用于训练，非常有价值。

我们介绍了KOSMOS-2，一个多模态大语言模型（MLLM），能够实现多模态大语言模型（MLLM），实现了感知物体描述（如边界框）和将文本与视觉世界相结合的新能力。将文本与视觉世界联系起来。

具体来说，我们将参考表达式作为Markdown中的链接，即"[文本跨度](边界框)"，其中对象描述是位置标记序列。描述是位置标记的序列。与多模态语料库一起、 我们构建了大规模的图像-文本对数据（称为GRIT）来训练 模型。

除了MLLMs的现有能力（例如 perceiving general modalities, following instructions, and performing in-context learning）、 KOSMOS-2将grounding能力整合到下游的应用中。我们对KOSMOS-2进行了广泛的任务评估，包括（i）multimodal grounding如指代表达的理解和短语接地，(ii) multimodal referring，如指称表达的生成，(iii)感知-语言任务、 以及(iv)语言理解和生成。这项工作奠定了Embodiment AI的发展基础，并揭示了语言、多模态感知、行动和世界建模的大融合，这是向人工智能迈出的关键一步。

总的结构图如下：

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/f2ca8ce3-2293-4802-88a4-4590c1652b89"/>
</div>

LLM 接入 grounding 能力的必要性：It enables the user to point to the object or region in the image directly rather than input detailed text descriptions to refer to it, the model can understand that image region with its spatial locations。Grounding capability also enables the model to respond with visual answers (i.e., bounding boxes), which can support more vision-language tasks such as referring expression comprehension

为了释放grounding能力，我们构建了一个网络规模的grounding图像-文本对数据集，并将其与KOSMOS-1中的多模态语料库相结合来训练该模型。这些grounding的图像-文本对建立在LAION-2B和COYO-700M的图像-文本对的子集上。我们构建了一个管道，将标题中的文本span（即名词短语和指代表达）与图像中相应对象或区域的空间位置（例如，边界框）进行提取和链接。我们将box的空间坐标转换为一串位置标记，然后将其附加在各自的文本span之后。该数据格式作为一个 "超链接"，将图像中的物体或区域与标题连接起来。

## 数据集生成过程

Step-1: Generating noun-chunk-bounding-box pairs
基于标注的图像描述文字，首先提取名词短语，然后将名词输入到 GLIP 中生成 bbox 即可

Step-2: Producing referring-expression-bounding-box pairs
扩展上面解析出来的名词短语，生成指代表达式，生成过程有点讲究，和利用到解析出来所有词之间的关系，结合前面的 bbox 就可以构成一个标注了。

我们使用spaCy来获得句子的依赖关系。然后通过递归地遍历依赖树中的子代，并将子代标记与名词块连接起来，将名词块扩展为一个指代表达。我们不扩展带有连接词的名词块。对于没有子代标记的名词块，我们为下一个过程保留它们。

图示如下：

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/020b87fe-e1e7-4113-84eb-cd810a324e3e"/>
</div>

最后，我们得到了大约 9100 万张图片，1.15 亿个文本跨度，以及 1.37 亿个相关的边界框。

## 模型和训练

KOSMOS-2 采用了与 KOSMOS-1 相同的模型架构和训练目标。我们将 grounded 图像-文本对添加到训练数据中，使模型具有接地和referring能力。

模型的输入形式，默认训练方式本质上还是 预测下一个词，所以只要有这个句子就可以采用 KOSMOS-1 训练了。

```text
<s> <image> Image Embedding </image> <grounding> <p> It </p><box><loc44><loc863></box> seats next to <p> a campfire </p><box><loc4><loc1007></box> </s>
```

<s> 是开启标志， </s> 是结束标志，<p> and </p> are special tokens indicating the beginning and end of the text span.

其余部分和 KOSMOS 一样，无非是词表里面加入了新的 token，然后训练即可。

在新添加的基础图像-文本对、单模态文本、图像-标题对以及交错的图像-文本数据进行训练。训练过程涉及到419K标记的批量大小，包括来自文本语料库的185K标记，来自原始和基础图像-标题对的215K标记，以及来自交错数据的19K标记。我们对KOSMOS-2进行了60K步的训练，相当于大约250亿个标记。采用AdamW优化器。设置权重衰减为0.01，辍学率为0.1。在最初的375个热身步骤中，学习率增加到2e-4，并线性衰减到零。

为了告诉模型何时将 grounding 文本预测输出，我们在训练过程中，将"<grounding>"标记预置到训练期间。也就是说一旦在模型推理时候，我插入了 <grounding> 标记则表示后面的内容需要进行 grounding 预测即输出的文本中带有实体名词的需要输出同时输出 bbox。

我们在256个V100 GPU上训练模型，训练大约需要一天的时间来完成。为了告诉模型何时将文本输出与视觉世界接轨，我们在训练期间将‘<grounding>’标记预置到训练期间。

第一步预训练：
The total number of trainable parameters amounts to approximately 1.6B. The image resolution is set to 224×224 and the patch size is 14×14. We divide the width and height
of the image into 32 bins, with each bin consisting of 7×7 pixels. A total of 32×32 location tokens are added to the vocabulary. KOSMOS-2 uses the weights of KOSMOS-1 for initialization, the newly
added word embeddings of location tokens are initialized randomly. We update all the parameters during training and instruction tuning

第二步指令微调：

在模型训练完成后，我们进行指令调整，以更好地使 KOSMOS-2 与人类指令相一致。我们将视觉语言指令数据集和纯语言指令数据集与训练数据结合起来，对模型进行调整。此外，我们通过利用GRIT中的边界框和表达式（即名词短语和指代表达式）对来构建接地的指令数据。给定一个表达式-边界框对，我们使用"<p>表达式</p>"作为输入指令，并提示模型生成边界框的相应位置标记。我们还使用"<p>它</p><box><loc1><loc2</box>是 "这样的提示，要求模型根据其边界盒生成表达式。

一些指令模板如下所示：

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/9919b447-c376-4f06-9c49-d5133c876f2a"/>
</div>

## 评估

• Multimodal grounding  
- Phrase grounding  
- Referring expression comprehension  
  
• Multimodal referring   
- Referring expression generation  

• Perception-language tasks  
- Image captioning  
- Visual question answering  

• Language tasks  
- Language understanding  
- Language generation  

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/2f784491-9af6-46cd-9529-2c8f7c74bddf"/>
</div>

Phrase grounding 任务要求模型基于一个或多个可能在单个标题中相互关联的短语来预测一组边界框。指代表达理解任务鼓励模型在给定图像中定位文本指代表达式中描述的对象。

在 Flickr30k Entities 上评估 Phrase grounding。在  RefCOCO , RefCOCO+  and RefCOCOg 上面进行评估 Referring expression comprehension，发现结果稍差点，这种差异可以归因于 RefCOCO 和 RefCOCO+ 中存在的数据分布，它们倾向于在双人游戏中使用更短的指代表达式（如“左下角”）。因此，我们未来的目标之一是增强多语言语言模型的能力，以便更准确地理解更多类型的人类表达。

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/44df5fbf-1ce1-40ce-82ea-cf26903ac8cb"/>
</div>

referring expression generation 用于给定图片和区域，对该区域进行描述。我们在 RefCOCOg 上评估了这个任务。我们使用了两个指标，BLEU-4 和 CIDEr-D，来评估生成的指令的质量。

还评估了 image captioning 和 visual question answering 任务。最后还评估了常见的语言任务。

疑问： 看官方论文给的例子，用户在和模型对话过程中，模型似乎知道当前对话是否应该输出 bbox？ 需要等 demo 开源后确认？

看样子是有特殊的 <groundding> token 来区分。一旦输入中带有这个 token，那么表示输出的句子中需要包含 bbox。那么对话时候是如何控制呢？ 通过阅读大致是：

1. 如果想让模型预测的文本中具备对其中的名词进行 groundding bbox 输出功能，需要在输入中带有 <groundding> 特殊token，在这个 token 后面的所有文本都具备 groundding 功能，这是训练时候数据决定的
2. 在对话时候，正常是不会加这个 token， 所以只就有输入 bbox 而没有输出 bbox 功能，不过如果加上应该就有了

以 Referring Expression Comprehension 为例模型的输入实际上是： 

```
<s><image> Image Embedding </image><grounding><p>A man in a blue hard hat and orange safety vest</p>
```

模型应该应该是直接输出 bbox 坐标 <box> <loc68> <loc425> </box>。

# Shikra

Shikra: Unleashing Multimodal LLM's Referential Dialogue Magic 解锁多模态语言模型参考对话的魔法  

https://arxiv.org/pdf/2306.15195.pdf
https://zhuanlan.zhihu.com/p/640891652

在人类的日常交流中，经常会关注场景中的不同区域或物体，双方都可以通过说话并指向这些区域来进行高效的信息交换。我们将这种对话模式称为参考对话（Referential Dialogue）。本工作提出了 Shikra 模型，赋予了MLLM这样的参考对话的魔法，既可以理解位置输入，也可以产生位置输出。

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/44df5fbf-1ce1-40ce-82ea-cf26903ac8cb"/>
</div>

1. Shikra 能够理解用户输入的 Point/Box，并支持 Point/Box 的输出，可以和人类无缝地进行参考对话；
2. Shikra 设计简单统一，采用非拼接式设计，直接使用数字表示坐标，不需要额外的位置编码器、前/后目标检测器或外部插件模块，甚至不需要额外的词汇表。

## 原理

模型架构采用CLIP ViT-L/14 作为视觉主干，Vicuna-7/13B 作为语言基模型，使用一层线性映射连接CLIP和Vicuna的特征空间

Shikra 直接使用自然语言中的数字来表示物体位置，使用[xmin, ymin, xmax, ymax] 表示边界框，使用[xcenter, ycenter]表示中心点，xy 坐标根据图像大小进行归一化，每个数字默认保留 3 位小数，这些坐标可以出现在模型的输入和输出序列中的任何位置，记录坐标的方括号也自然地出现在句子中。在论文中，本工作也尝试使用其他方式进行数值表示，并做了定量的对比实验

思想链（CoT），旨在通过在最终答案前添加推理过程以帮助LLM回答复杂的QA问题。这一技术已被广泛应用到自然语言处理的各种任务中。目前的MLLM还存在严重的幻视问题，CoT也经常会产生幻觉，影响最终答案的正确性。通过在合成数据集CLEVR上的实验，本工作发现，使用带有位置信息的CoT时，可以提升模型回答的准确率。

在CoT中包含坐标信息，性能得到了提升，我们将这种新的 CoT 方式称为 Grounding-CoT（GCoT）。

Shikra is trained in two stages. In the first stage, we train it on the reorganized VL dataset (Section 5.3.1) for 100,000 steps (around 1.5 epoch); 
In the  second stage, we raise the sampling ratio to 50% on LLaVA-Instruct-150K (Liu et al., 2023a) and our generated RD data (Section 5.3.2). 
In both stages, we freeze the visual encoder and tune all parameters in LLM. All training runs on 8 NVIDIA A100 GPUs. It takes around 100h for stage one training and 20h for stage two.

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/7c3490a8-4d5d-4a9d-8f2a-c61d442f0036"/>
</div>

不同任务联合训练的输入模板

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/2ee3f034-8644-445f-9cfc-616a60d8127b"/>
</div>

# LLaVA

# mPLUG-Owl

# InstructBLIP

# LaVIN

# LENS

https://github.com/ContextualAI/lens

Towards Language Models That Can See: Computer Vision Through the LENS of Natural Language

一个不用任何训练就可以赋予 LLM 模型视觉理解和 VQA 能力的方法。看起来非常酷炫，实际上做法非常简单，推理成本也是极其高，感觉也就是看看。目前来看局限性也很大，期待后面有更好的办法。

其主要的点在于：目前的流行多模态模型都需要多模态预训练这个步骤，通常需要收集大量的图文数据进行训练，而本文不需要这个步骤或者说根本就不用训练。

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/eb29f030-b59b-4705-b52d-747dbbd06b39"/>
</div>

如果想不训练，那么其实也是类似于 prompt 工程

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/d073a2cc-c19a-4ad6-b26b-762ea7b45a2b"/>
</div>

视觉部分是并行加了很多 SOTA 的视觉模型，然后可以生成 tag,属性和描述等等一大堆文本信息，然后和用户输入文本一起构成最终输入进行 VQA。

推理成本非常高。

# mPLUG-Owl

# GPT4RoI

https://github.com/jshilong/GPT4RoI

# EMU-不错

Generative Pretraining in Multimodality

https://arxiv.org/pdf/2307.05222.pdf
https://github.com/baaivision/Emu 模型比较大

生成式预训练直接解锁多模态功能。 全开源，可以直接训练第三步指令级微调。

EMU 将物理世界上存在的各种模态都统一变成 embedding，然后采用 NLP 里面的预测下一个 token (token 其实就是 embedding，可以是离散的也可以是连续的)的方式进行统一建模训练，算是一个和别人不同的地方。
这样做的好处是训练的数据源非常好处理，容易获取。

与现有的LMM不同,它只在文本标记上计算预测下一个损失,在训练Emu时,所有输入元素包括离散文本标记和连续图像嵌入都被考虑在损失计算中。我们采用交叉熵分类损失计算离散文本标记,采用L2回归损失计算连续视觉嵌入。由于原始图像通常缺乏语言中的左至右因果依赖关系,Emu 并未在原始像素空间进行图像生成预训练。取而代之的是,视觉嵌入通过因果Transformer转换为一个因果潜在空间,它接受EVA-CLIP生成的图像编码作为输入,输出N个标记来捕捉给定图像的因果依赖性。

我们提出了Emu,一个基于Transformer的多模态联合模型,它可以无缝地在多模态环境中生成图像和文本。这个"全才"模型可以通过 a one-model-for-all 的自回归训练流程,以区别对待的方式接收任何单模式或多模式数据输入(例如,交错的图像、文本和视频)。首先,视觉信号被编码成嵌入,与文本标记一起形成一个交错的输入序列。然后,Emu通过统一地 Objectives 方式进行端到端训练,要么预测下一个文本标记,要么回归下一个视觉嵌入在多模态序列中。这种多样化的多模态力量有利于大规模预训练数据源的探索,例如带有交错帧和文本的视频、带有交错图像和文本的网页,以及网络规模的图像 - 文本对和视频 - 文本对。Emu 可以作为一般性的多模态界面,用于图像到文本和文本到图像任务,并支持上下文图像和文本生成。在许多零文和少文任务上,包括图像captioning、视觉问题回答、视频问题回答和文本到图像生成,Emu 都比先进的大型多模态模型表现出色。通过指令调整也展示了多模态助手等扩展功能,且表现出令人印象深刻的功能。

基模型可以做图像生成任务，视频 VQA，而不仅仅是文本生成。

支持的任务如下：

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/0a16764d-124c-40ee-891b-5276698c8b9f"/>
</div>

图像描述、图片 VQA，few shot 文本补全

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/26e0661d-b66e-4486-82f1-fa3e2da43253"/>
</div>

图生图，文生图，视频 VQA。

## 架构

整体架构如下：

<div align=center>
<img src="https://github.com/open-mmlab/mmdetection/assets/17425982/089dd0c4-b911-4199-9167-2cd68e46aa9c"/>
</div>

Emu 由四部分组成:视觉编码器、因果 Transformer、多模态建模和视觉解码器。我们分别利用预训练的 EVA-CLIP、 LLaMA 和 Stable Diffusion 来初始化视觉编码器、多模态建模LLM和视觉解码器。

首先图片输入到 EVA-CLIP 的编码器中，输出 vision embedding，考虑到后续需要直接回归连续的 vision embedding，但是它实际上没有因果关系，无法直接用，因此作者将其输入到因果 Transformer中使其变成有因果关系的  vision embedding。
如果是视频，则拆分成一张一张图片，进行分别处理，帧和帧之前用分隔符合区分。

以上图为例，输入序列包括一张图片，一段文本和一张后续的图片，首先对图片使用 EVA-CLIP + 因果 Transformer 将其转化为因果 vision embedding，然后就可以直接训练了。对于离散 token 采用 ce loss，对于连续 embedding 采用 l2 loss。

在训练完成后，在单独微调 Stable Diffusion 模型使其可以进行文生图。

以下描述来自翻译：
给定任何交错有图像、文本和视频的序列,我们首先通过 EVA-CLIP 对图像进行编码为稠密的视觉特征，然后通过因果 Transformer 将编码转换为固定数量N个视觉因果嵌入。同样,我们将T帧的视频编码为T×N个视觉因果嵌入。分别在每张图像或帧前面和后面加上两个特殊的图像令牌[IMG]和 [/IMG],以表示编码后图像/帧嵌入的开始和结束。视觉因果嵌入与文本标记相结合形成多模态序列,并提供给多模态建模LLM进行统一的自回归建模。我们在每个序列的开始和结束分别附加 <s> 和 </s> 标记。在推断中，我们微调视觉解码器将视觉嵌入解码为真实的图像。
视觉解码器: 我们使用潜在扩散模型来将视觉嵌入解码为图像,并采用 Stable Diffusion 的权重作为初始值。具体来说, 我们将Emu生成的 N 个视觉嵌入提供给扩散模型作为图像解码的条件。 我们用能够适应 Emu 和 Stable Diffusion 维度的新线性层替换稳定扩散中交叉注意力模块的线性投影。
我们通过跨模态多种形式的网络规模数据预训练 Emu,包括图像 - 文本对(LAION-2B[53]、LAION-COCO[2])、交错图像 - 文本数据(MMC4[76])、视频 - 文本对(WebVid-10M[5]) 和我们收集的交错视频 - 文本数据(YT-Storyboard-1B)。所有这些数据都被表征为多模态序列,从中 Emu 在统一的自回归方式下按照预测下一个元素的目标学习。预训练后,我们微调一个图像解码器来将视觉嵌入转换成真实图像。

The total number of parameters of Emu is 14B and is trained end-to-end.

## 训练过程

1. 预训练
和前面描述的一样，采用自回归方式训练  EVA-CLIP 因果 Transformer、多模态建模 三个模块

2. Visual Decoding 微调
We freeze the Visual Encoder, Multimodal Modeling LLM in Emu, and the VAE in diffusion model during training, with only the parameters of U-Net updated

3. Instruction Tuning
我们在Emu上应用多模态指令调整,通过对公开可用数据集进行有监督微调,包括来自ShareGPT[74]和Alpaca[56]的语言指令、来自LLaVA[39]的图像-文本指令以及来自VideoChat[36]和Video-ChatGPT的视频指令,来使Emu与人类指令保持一致。

在指令调整中,我们冻结预训练 Emu 的所有参数,仅微调低秩适应(LoRA)模块。

# BuboGPT

https://arxiv.org/pdf/2307.08581.pdf
https://bubo-gpt.github.io/

BuboGPT: Enabling Visual Grounding in Multi-Modal LLMs

我们提出BuboGPT, 一个具有视觉定位能力的多模态LLM, 它可以在视觉、听觉和语言之间进行跨感觉交互, 提供对视觉物体和其他给定感觉类型的细粒度理解。 因此, 当 BuboGPT 为该物体生成响应或描述时, 它能指出该物体在图像中的具体位置。 我们的贡献有两个方面: 1) 基于SAM的现成视觉固定模块,它可以从句子中提取实体并在图像中找到对应的掩码。 2) 两阶段训练方案和指令数据集, 为联合文本-图像-音频理解提供能力。

简单来说，就是做了音频、图片和文本对齐，可以对话和输出 visual grounding。

基于 sam 来做 visual grounding

<div align=center>
<img src="https://github.com/hhaAndroid/awesome-mm-chat/assets/17425982/9d1d2670-db47-4562-8aa1-c0d4d37c3ebc"/>
</div>

然后再进行对齐训练

<div align=center>
<img src="https://github.com/hhaAndroid/awesome-mm-chat/assets/17425982/7dbe7554-3ad5-487e-8e23-a2c9fefffd1b"/>
</div>

总体感觉没有特别大的新意。

# 其他

https://zhuanlan.zhihu.com/p/639822513

