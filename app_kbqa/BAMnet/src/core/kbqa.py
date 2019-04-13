import ssl
from SPARQLWrapper import SPARQLWrapper

from .bamnet.bamnet import BAMnetAgent
# from .bow.bow import BOWnetAgent
from .utils.kb_utils import query_remote_kb

from .build_data.foodkg.build_data import build_all_data
from .build_data.utils import vectorize_data
from .utils.utils import *
from .utils.generic_utils import unique
from .config import *


USE_ENDPOINT_URL = "http://whyislogics.heals.rpi.edu:8080/blazegraph/namespace/knowledge/sparql"


ONLINE_KB_QUERY = False

class KBQA(object):
    """Pretrained KBQA wrapper"""
    def __init__(self, config):
        super(KBQA, self).__init__()
        self.config = config
        self.local_kb = load_ndjson(config['kb_path'], return_type='dict')
        self.vocab2id = load_json(os.path.join(config['data_dir'], 'vocab2id.json'))
        self.entity2id = load_json(os.path.join(config['data_dir'], 'entity2id.json'))
        self.entityType2id = load_json(os.path.join(config['data_dir'], 'entityType2id.json'))
        self.relation2id = load_json(os.path.join(config['data_dir'], 'relation2id.json'))
        self.agent = BAMnetAgent(config, STOPWORDS, self.vocab2id)
        # self.agent = BOWnetAgent(config, STOPWORDS, self.vocab2id)
        for param in self.agent.model.parameters():
            param.requires_grad = False

        if ONLINE_KB_QUERY:
            self.sparql = SPARQLWrapper(USE_ENDPOINT_URL)

    def predict(self, cands, cand_labels):
        pred = self.agent.predict(cands, cand_labels, batch_size=1, margin=2, silence=True)
        return pred

    def simple_answer(self, question, topic_entity):
        question_dict = {'qType': 'simple',
                        'topicKey': [topic_entity],
                        'qText': question,
                        'entities': [],
                        'rel_path': [],
                        'answers': []}
        data_vec = build_all_data([question_dict], self.local_kb, self.entity2id, self.entityType2id, self.relation2id, self.vocab2id)
        queries, raw_queries, query_mentions, memories, cand_labels, _, _, cand_rel_paths, cand_ids = data_vec
        queries, query_words, query_lengths, memories_vec = vectorize_data(queries, query_mentions, memories, \
                                            max_query_size=self.config['query_size'], \
                                            max_ans_type_bow_size=self.config['ans_type_bow_size'], \
                                            max_ans_path_bow_size=self.config['ans_path_bow_size'], \
                                            max_ans_path_size=self.config['ans_path_size'], \
                                            vocab2id=self.vocab2id, \
                                            fixed_size=True, \
                                            verbose=False)


        pred = self.predict([memories_vec, queries, query_words, raw_queries, query_mentions, query_lengths], cand_labels)
        if len(pred[0]) == 0:
            return [], [], []
        pred_ans = [cand_labels[0][pred[0][0][0]]]
        pred_ans_ids = [cand_ids[0][pred[0][0][0]]]
        pred_rel_paths = [cand_rel_paths[0][pred[0][0][0]]]
        return pred_ans, pred_ans_ids, pred_rel_paths

    def comparision_answer(self, question, topic_entity_1, topic_entity_2):
        question_dict = {'qType': 'comparison',
                        'topicKey': [topic_entity_1, topic_entity_2],
                        'qText': question,
                        'entities': [],
                        'rel_path': [],
                        'answers': []}
        data_vec = build_all_data([question_dict], self.local_kb, self.entity2id, self.entityType2id, self.relation2id, self.vocab2id)
        queries, raw_queries, query_mentions, memories, cand_labels, _, _, cand_rel_paths, cand_ids = data_vec
        queries, query_words, query_lengths, memories_vec = vectorize_data(queries, query_mentions, memories, \
                                            max_query_size=self.config['query_size'], \
                                            max_ans_type_bow_size=self.config['ans_type_bow_size'], \
                                            max_ans_path_bow_size=self.config['ans_path_bow_size'], \
                                            max_ans_path_size=self.config['ans_path_size'], \
                                            vocab2id=self.vocab2id, \
                                            fixed_size=True, \
                                            verbose=False)


        intermediate_pred = self.predict([memories_vec, queries, query_words, raw_queries, query_mentions, query_lengths], cand_labels)
        if len(intermediate_pred[0]) > 0:
            o1 = cand_labels[0][intermediate_pred[0][0][0]]
        else:
            return [topic_entity_2], [topic_entity_2], []

        if len(intermediate_pred[1]) > 0:
            o2 = cand_labels[1][intermediate_pred[1][0][0]]
        else:
            return [topic_entity_1], [topic_entity_1], []

        try:
            o1 = float(o1)
            o2 = float(o2)
        except:
            pass

        pred_rel_paths = [cand_rel_paths[0][intermediate_pred[0][0][0]], cand_rel_paths[1][intermediate_pred[1][0][0]]]
        is_more = self.is_more(question)
        if (is_more and o1 > o2) or (not is_more and o1 < o2):
            pred_ans = [topic_entity_1]
        else:
            pred_ans = [topic_entity_2]
        return pred_ans, pred_ans, pred_rel_paths

    def constraint_answer(self, question, topic_entity):
        question_dict = {'qType': 'constraint',
                'topicKey': [topic_entity],
                'qText': question,
                'entities': [],
                'rel_path': [],
                'answers': []}
        data_vec = build_all_data([question_dict], self.local_kb, self.entity2id, self.entityType2id, self.relation2id, self.vocab2id)
        queries, raw_queries, query_mentions, memories, cand_labels, _, _, cand_rel_paths, cand_ids = data_vec
        queries, query_words, query_lengths, memories_vec = vectorize_data(queries, query_mentions, memories, \
                                            max_query_size=self.config['query_size'], \
                                            max_ans_type_bow_size=self.config['ans_type_bow_size'], \
                                            max_ans_path_bow_size=self.config['ans_path_bow_size'], \
                                            max_ans_path_size=self.config['ans_path_size'], \
                                            vocab2id=self.vocab2id, \
                                            fixed_size=True, \
                                            verbose=False)


        pred = self.predict([memories_vec, queries, query_words, raw_queries, query_mentions, query_lengths], cand_labels)
        pred_ans = []
        pred_ans_ids = []
        pred_rel_paths = []
        for x in pred[0]:
            if x[1] + self.config['test_margin'][0] >= pred[0][0][1]:
                if not cand_labels[0][x[0]] in pred_ans:
                    pred_ans.append(cand_labels[0][x[0]])
                    pred_ans_ids.append(cand_ids[0][x[0]])
                    pred_rel_paths.append(cand_rel_paths[0][x[0]])
        # pred_ans = unique([cand_labels[0][x[0]] for x in pred[0] if x[1] + self.config['test_margin'][0] >= pred[0][0][1]])
        # pred_rel_paths = [cand_rel_paths[0][pred[0][0][0]]]
        return pred_ans, pred_ans_ids, pred_rel_paths

    def answer(self, question, question_type, topic_entities):
        '''Input:
        question: str
        question_type: str
        topic_entities: list
        Output:
        answer_list: list
        rel_path_list: list
        error_code: int, 0: success, -1: error
        error_msg: str
        '''
        if len(question) == 0:
            return [], -1, 'Error: question is empty.'

        question_type = question_type.lower()
        if question_type == 'simple':
            if len(topic_entities) >= 1:
                if not topic_entities[0] in self.local_kb:
                    self.update_local_kb(topic_entities[0], 'usda')

                answer_list, answer_id_list, rel_path_list = self.simple_answer(question, topic_entities[0])
                err_code = 0
                err_msg = ''
            else:
                answer_list = []
                answer_id_list = []
                rel_path_list = []
                err_code = -1
                err_msg = 'Error: the number of topic entities is supposed to be larger than one for simple questions.'
        elif question_type == 'comparison':
            if len(topic_entities) >= 2:
                if not topic_entities[0] in self.local_kb:
                    self.update_local_kb(topic_entities[0], 'usda')
                if not topic_entities[1] in self.local_kb:
                    self.update_local_kb(topic_entities[1], 'usda')

                answer_list, answer_id_list, rel_path_list = self.comparision_answer(question, topic_entities[0], topic_entities[1])
                err_code = 0
                err_msg = ''
            else:
                answer_list = []
                answer_id_list = []
                rel_path_list = []
                err_code = -1
                err_msg = 'Error: the number of topic entities is supposed to be larger than two for comparison questions.'
        elif question_type == 'constraint':
            if len(topic_entities) >= 1:
                if not topic_entities[0] in self.local_kb:
                    self.update_local_kb(topic_entities[0], 'recipe')

                answer_list, answer_id_list, rel_path_list = self.constraint_answer(question, topic_entities[0])
                err_code = 0
                err_msg = ''
            else:
                answer_list = []
                answer_id_list = []
                rel_path_list = []
                err_code = -1
                err_msg = 'Error: the number of topic entities is supposed to be larger than one for constraint questions.'
        else:
            return [], -1, 'Error: unknown question type: {}'.format(question_type)
        return answer_list, answer_id_list, rel_path_list, err_code, err_msg

    def update_local_kb(self, topic_entity, kb_name):
        if topic_entity in self.local_kb:
            return

        if ONLINE_KB_QUERY:
            graph = query_remote_kb(self.sparql, topic_entity, kb_name)
            if isinstance(graph, dict):
                self.local_kb.update(graph)
                with open(os.path.join(config['kb_dir'], 'kg.json'), 'a') as f_kb:
                    f_kb.write(json.dumps(graph) + '\n')

    @classmethod
    def from_pretrained(cls, config):
        kbqa = KBQA(config)
        return kbqa

    def is_more(self, text):
        text = text.split()
        if len(set(text).intersection(['more', 'higher', 'larger'])) > 0:
            return True
        else:
            return False
