# bert_data_preprocessing_rational_eraser.py
from itertools import chain

import numpy as np
import tensorflow as tf

if tf.__version__.startswith('2'):
    import tensorflow.compat.v1 as tf
import tensorflow_hub as hub
from copy import deepcopy

from bert_with_ration_eraser import convert_examples_to_features, \
    FullTokenizerWithRations, \
    InputRationalExample
from config import *
from eraserbenchmark.rationale_benchmark.utils import Evidence


def create_tokenizer_from_hub_module(gpu_id):
    """Get the vocab file and casing info from the Hub module."""
    with tf.Graph().as_default():  # basically useless, but good practice to specify the graph using, even it sets the default graph as the default graph
        bert_module = hub.Module(BERT_MODEL_HUB)
        tokenization_info = bert_module(signature="tokenization_info", as_dict=True)
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.gpu_options.visible_device_list = gpu_id
        config.graph_options.optimizer_options.global_jit_level = tf.OptimizerOptions.ON_1
        with tf.Session(
                config=config) as sess:  # create a new session, with session we can setup even remote computation
            vocab_file, do_lower_case = sess.run([tokenization_info["vocab_file"],
                                                  tokenization_info["do_lower_case"]])
    return FullTokenizerWithRations(vocab_file=vocab_file, do_lower_case=do_lower_case)


def load_bert_features(data, docs, label_list, max_seq_length, merge_evidences, decorator, gpu_id):
    tokenizer = create_tokenizer_from_hub_module(gpu_id)
    input_examples = []
    for ann_id, ann in enumerate(data):
        text_a = ann.query
        label = ann.classification
        if not merge_evidences:
            for ev_group in ann.evidences:
                doc_ids = list(set([ev.docid for ev in ev_group]))
                sentences = chain.from_iterable(docs[doc_id] for doc_id in doc_ids)
                flattened_tokens = chain(*sentences)
                text_b = ' '.join(flattened_tokens)
                evidences = ev_group
                if decorator is not None:
                    text_b = decorator(text_b, evidences)
                input_examples.append(InputRationalExample(guid=None,
                                                           text_a=text_a,
                                                           text_b=text_b,
                                                           label=label,
                                                           evidences=evidences))
        else:
            docids_to_offsets = dict()
            latest_offset = 0
            example_evidences = []
            text_b_tokens = []

            for ev_group in ann.evidences:
                for ev in ev_group:
                    if ev.docid in docids_to_offsets:
                        offset = docids_to_offsets[ev.docid]
                    else:
                        tokens = list(chain.from_iterable(docs[ev.docid]))
                        docids_to_offsets[ev.docid] = latest_offset
                        offset = latest_offset
                        latest_offset += len(tokens)
                        text_b_tokens += tokens
                    example_ev = Evidence(text=ev.text,
                                          docid=ev.docid,
                                          start_token=offset + ev.start_token,
                                          end_token=offset + ev.end_token,
                                          start_sentence=ev.start_sentence,
                                          end_sentence=ev.end_sentence)
                    example_evidences.append(deepcopy(example_ev))
            # if len(text_b_tokens) == 0:
            #     text_b_tokens = list(chain.from_iterable(
            #                             chain.from_iterable(docs[i] for i in ann.docids)))
            text_b = ' '.join(text_b_tokens)
            evidences = example_evidences
            if decorator is not None:
                text_b = decorator(text_b, evidences, tokenizer)
            input_examples.append(InputRationalExample(guid=None,
                                                       text_a=text_a,
                                                       text_b=text_b,
                                                       label=label,
                                                       evidences=evidences))
            # print(input_examples[-1].text_b, input_examples[-1].text_a, input_examples[-1].evi)
            # if ann.annotation_id == 'negR_010.txt':
            #    print('#'*100)
            #    print(input_examples[-1].text_b)
            #    print(text_b)
            #    print("#"*100)

    features = convert_examples_to_features(input_examples, label_list, max_seq_length, tokenizer)
    # print(data[10].annotation_id)
    # print(input_examples[10].text_b)
    # print(features[10].input_ids)
    return features


def convert_bert_features(features, with_label_id, with_rations, exp_output='gru'):
    feature_names = "input_ids input_mask segment_ids".split()

    input_ids, input_masks, segment_ids = \
        list(map(lambda x: [getattr(f, x) for f in features], feature_names))

    rets = [input_ids, input_masks, segment_ids]

    if with_rations:
        feature_names.append('rations')
        rations = [getattr(f, 'rations') for f in features]
        rations = np.array(rations).reshape([-1, MAX_SEQ_LENGTH, 1])
        if exp_output == 'interval':
            rations = np.concatenate([np.zeros((rations.shape[0], 1, 1)),
                                      rations,
                                      np.zeros((rations.shape[0], 1, 1))], axis=-2)
            rations = rations[:, 1:, :] - rations[:, :-1, :]
            rations_start = (rations > 0)[:, :-1, :].astype(np.int32)
            rations_end = (rations < 0)[:, 1:, :].astype(np.int32)
            rations = np.concatenate((rations_start, rations_end), axis=-1)
        rets.append(rations)
    else:
        rets.append(None)

    if with_label_id:
        feature_names.append('label_id')
        label_id = [getattr(f, 'label_id') for f in features]
        labels = np.array(label_id).reshape(-1, 1)
        rets.append(labels)
    else:
        rets.append(None)
    return rets


def preprocess(data, docs, label_list, dataset_name, max_seq_length, exp_output, merge_evidences, data_decorator=None,
               gpu_id='0'):
    features = load_bert_features(data, docs, label_list, max_seq_length, merge_evidences, data_decorator, gpu_id)

    with_rations = ('cls' not in dataset_name)
    with_lable_id = ('seq' not in dataset_name)

    return convert_bert_features(features, with_lable_id, with_rations, exp_output)
