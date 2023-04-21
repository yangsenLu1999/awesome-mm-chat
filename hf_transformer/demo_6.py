def demo_1():
    import os
    # 会自动下载到  ~/.cache/huggingface/dataset, 您可以通过设置 HF_HOME 环境变量来自定义缓存的文件夹
    # 必须要放到 from datasets import load_dataset 前面，否则无效
    os.environ['HF_HOME'] = '../'  # 所有缓存都会放到这个路径下

    from datasets import load_dataset

    # This can take a few minutes to load, so grab a coffee or tea while you wait!
    raw_datasets = load_dataset("espejelomar/code_search_net_python_10000_examples", "python")
    print(raw_datasets["train"])
    print(raw_datasets["train"][3456]["whole_func_string"])

    def get_training_corpus():
        dataset = raw_datasets["train"]
        for start_idx in range(0, len(dataset), 1000):
            samples = dataset[start_idx: start_idx + 1000]
            yield samples["whole_func_string"]

    from transformers import AutoTokenizer

    old_tokenizer = AutoTokenizer.from_pretrained("gpt2")
    example = '''def add_numbers(a, b):
        """Add the two numbers `a` and `b`."""
        return a + b'''

    tokens = old_tokenizer.tokenize(example)
    print(len(old_tokenizer))  # 50257
    print(tokens)

    training_corpus = get_training_corpus()
    tokenizer = old_tokenizer.train_new_from_iterator(training_corpus, 52000)

    tokens = tokenizer.tokenize(example)
    print(tokens)

    print(len(tokens))  # 27
    print(len(old_tokenizer.tokenize(example)))  # 44

    print(len(tokenizer))  # 52000
    # 可以发现总的词汇表发现了变化(保存到了 merges.txt 里面), finetune 的时候应该要改输入 embedding 参数，否则可能越界, 可以看 demo_2
    tokenizer.save_pretrained("code-search-net-tokenizer")


def demo_2():
    import os
    os.environ['HF_HOME'] = '../'  # 所有缓存都会放到这个路径下

    from transformers import BertTokenizer, BertModel
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    text = "c_1四处张望。"

    print(text)  # c_1四处张望。
    # ['c', '_', '1', '四', '[UNK]', '[UNK]', '[UNK]', '。']  c_1 会切分为三个单词，后续解码时候也是变成三个单词，而不是一个单词，也就是说有缺陷
    print(tokenizer.tokenize(text))

    print(tokenizer.encode(text))
    # [CLS] c _ 1 四 [UNK] [UNK] [UNK] 。 [SEP]
    print(tokenizer.decode(tokenizer.encode(text)))

    # 可以通过新增 token 来解决这个问题
    characters = ["c_1"]
    print(tokenizer.vocab_size) # 30522
    tokenizer.add_tokens(characters)
    print(tokenizer.vocab_size) # 30522
    # 可以发现实际上打印的词汇表并没有改变，原因是他是单独存放的，而不是合并到词汇表
    tokenizer.save_pretrained('aa')
    # 会生成一个新的 added_tokens.json 文件
    print(len(tokenizer))  # 长度+1

    # ['c_1', '四', '[UNK]', '[UNK]', '[UNK]', '。']
    print(tokenizer.tokenize(text))
    # [CLS] c_1 四 [UNK] [UNK] [UNK] 。 [SEP]
    print(tokenizer.decode(tokenizer.encode(text)))

    # 这个步骤必须，因为总的词汇表变了，需要对新增的部分随机初始化
    # 模型需要调用 resize_token_embeddings，预训练的 Embedding 不变，添加的 token 随机初始化进 Embedding 矩阵中。
    # 假设原先词汇表大小是 100，维度是 512,那么原先的 embeding 维度就是 100x512, 现在增加了 10 个 token，那么新的 embeding 维度就是 110x512
    # 但是原先的 100 个 token 的 embeding 是预训练好的，所以不需要改变，只需要把新增的 10 个 token 的 embeding 随机初始化进去就可以了
    model = BertModel.from_pretrained("bert-base-uncased")
    model.resize_token_embeddings(len(tokenizer))


if __name__ == '__main__':
    num = 1
    eval(f"demo_{num}()")
