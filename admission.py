import json
import re
import thulac
from laserembeddings import Laser
from sklearn.metrics.pairwise import cosine_similarity
import string

# dataset = ["zje", "浙江大学", "爱丁堡大学", "zhejiang", "aidingbao", "edinburgh",'证书','生物医学','生物信息学','师资','培养','学制','交流','研究生申请','奖学金','色弱','保研','科研','学费','专业','去向','毕业','就业','前景','就业方向','未来','住宿','宿舍']
class process_question:
    def __int__(self):
        pass
    #处理问题，按照标点符号进行拆分
    def split_question(self,text):
        questions = re.split(r'[？。！；，、]', str(text))
        # 去除可能的空格
        questions = [q.strip() for q in questions if q]
        # 过滤不包含数据集中任何一个词的字符串
        # questions = [q for q in questions if any(word in q for word in dataset)] #该部分最后使用相似度<0.5进行输出控制。
        return questions

    def has_nouns(self,text):
        thu = thulac.thulac()
        words_with_pos = thu.cut(text, text=True)
        for word_and_pos in words_with_pos:
            if isinstance(word_and_pos, tuple):
                word, pos = word_and_pos
                if 'n' in pos:  # 判断是否包含名词
                    return True
            else:
                if 'n' in word_and_pos:  # 处理没有词性信息的情况
                    return True
        return False


    def find_most_similar_questions(self,input_text, jsonl_file_path='/mnt/qwen_test/zheda_admission/dataset/admit_dataset.jsonl'):
        # 加载JSONL文件
        laser = Laser()
        data = []
        dataset1 = ['专业','生物信息学','生物医学','方向','医学','信息学','爱丁堡','报名','报考','录取']
        dataset2 = ['分','成绩','线','转专业','师资','队伍','教授','导师','老师',"教师",'人才','人力','培养','教学','教育','学术','授课','课程','上课','学习','学制','x+x','4+0','交换','海外','出国','留学','国际','美国','英国','澳','新加坡','香港','博士','硕士','毕业','研究生','申请','升学','考研','考博','硕博','直博','工作','职业','领域','奖励','补贴','就业','奖学金','荣誉','奖项','钱','资金','色弱','体检','色盲','近视','健康','身体','视力','科学研究','研究','费','保研','推免','科研','实验室','住宿费','学费','宿舍','住宿','开销']
        dataset3 = ['证书','毕业证','学位证','政策']
        with open(jsonl_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                data.append(json.loads(line))

        # 提取问题并生成它们的嵌入向量
        questions = [item['question'] for item in data]
        questions_embeddings = laser.embed_sentences(questions, lang='zh')

        # 为输入文本生成嵌入向量
        input_embeddings = laser.embed_sentences([input_text], lang='zh')

        # 计算输入文本与问题的余弦相似度
        similarities = cosine_similarity(input_embeddings, questions_embeddings)

        scores = similarities[0]

        # 创建一个包含问题、答案和相应相似度分数的列表
        question_answer_scores = list(zip(data, scores))

        modified_question_answer_scores = [
            (question, score + 3) if any(
                substring in question['question'] and substring in input_text for substring in dataset3)
            else (question, score + 2) if any(
                substring in question['question'] and substring in input_text for substring in dataset2)
            else (question, score + 1) if any(
                substring in question['question'] and substring in input_text for substring in dataset1)
            else (question, score)
            for question, score in question_answer_scores
        ]

        # 按相似度分数降序排序
        sorted_question_answer_scores = sorted(modified_question_answer_scores, key=lambda x: x[1], reverse=True)

        # 获取最相似的1个问题和答案
        most_similar = sorted_question_answer_scores[0]

        # 输出最相似的问题与答案
        # print(f"问题: {most_similar[0]['question']} (相似度分数: {most_similar[1]:.4f})")
        # print(f"答案: {most_similar[0]['answer']}")

        # 返回相似度分数，问题和答案
        return most_similar[1], most_similar[0]['question'], most_similar[0]['answer']


    # def answer_question(self,text):
    #     q = self.split_question(text)
    #     answer = '<br>您的问题是：' + text + '\n我将做出以下回答：\n<br><br>'
    #     temp_ans = answer
    #     count = 0
    #     for i, question in enumerate(q):
    #         score, qu, ans = self.find_most_similar_questions(question)
    #         print(score, qu, ans)
    #         if score >= 1:
    #             answer += f"{count + 1}. 关于问题——{question}\n<br><br>"
    #             answer += str(ans).replace('\n', '')
    #             answer += '\n<br><br>'
    #             count += 1
    #         else:
    #             decimal_part = score % 1
    #             # if self.has_nouns(question):
    #             #     print('合法输入')
    #             if decimal_part < 0.8 and decimal_part > 0.1:
    #                 continue
    #             else:
    #             # print(f"原始问题 {i}: {question}")
    #                 answer += f"{count + 1}. 关于问题——{question}\n<br><br>"
    #                 answer += str(ans).replace('\n','')
    #                 answer += '\n<br><br>'
    #                 count += 1
    #             # else:
    #             #     print('不合法输入')
    #     if answer == temp_ans:
    #         answer += '很抱歉！我无法回答您的问题，请换个方式重新输入一下，或者您也可以咨询相关工作人员，电话：0571-58572813\n<br><br>'
    #     answer += '（提醒：如果以上回答未能解决您的问题，首先向您表示抱歉，随后您可以拨打招生咨询电话0571-58572813，会有专业招生人员为您解答疑惑）'
    #     return answer

    def answer_question(self, text):
        q = self.split_question(text)
        answer = '您的问题是——' + text + '  \n我的回答是：  \n  \n'
        temp_ans = answer
        unique_answers = set()

        for i, question in enumerate(q):
            score, qu, ans = self.find_most_similar_questions(question)
            print(score, qu, ans)

            if score >= 1:
                # current_answer = str(ans).replace('\n', '')
                current_answer = str(ans)
                if current_answer not in unique_answers:
                    answer += current_answer + '  \n  \n'
                    unique_answers.add(current_answer)
            else:
                decimal_part = score % 1
                if decimal_part < 0.9 and decimal_part > 0.1:
                    continue
                else:
                    # current_answer = str(ans).replace('\n', '')
                    current_answer = str(ans)
                    if current_answer not in unique_answers:
                        answer += current_answer + '  \n  \n'
                        unique_answers.add(current_answer)

        if answer == temp_ans:
            answer += '很抱歉！我无法回答您的问题，请换个方式重新输入一下，或者您也可以咨询相关工作人员，电话：0571-58572813  \n  \n'

        answer += '（提醒：如果以上回答未能解决您的问题，首先向您表示抱歉，随后您可以拨打招生咨询电话0571-58572813，会有专业招生人员为您解答疑惑）'
        return answer

    def test_similarity(self,text):
        score = ''
        q = self.split_question(text)
        answer = '<br>您的问题是：' + text + '\n我将做出以下回答：\n<br><br>'
        temp_ans = answer
        count = 0
        for i, question in enumerate(q):
            score, qu, ans = self.find_most_similar_questions(question)
            print(score, qu, ans)
            decimal_part = score % 1
            if decimal_part < 0.58 and decimal_part > 0.1:
                continue
            else:
                # print(f"原始问题 {i}: {question}")
                answer += f"{count + 1}. 关于问题——{question}\n<br><br>"
                answer += str(ans).replace('\n', '')
                answer += '\n<br><br>'
                count += 1
        if answer == temp_ans:
            answer += '很抱歉！我无法回答您的问题，请换个方式重新输入一下，或者您也可以咨询相关工作人员，电话：0571-58572813\n<br><br>'
        answer += '（提醒：如果以上回答未能解决您的问题，首先向您表示抱歉，随后您可以拨打招生咨询电话0571-58572813，会有专业招生人员为您解答疑惑）'
        return score, text, answer

process = process_question()
# y = answer_question("我想知道，专业是什么样的？宿舍情况如何，宿舍需要花多少、还有生物信息学这个专业怎么样。")
y = process.answer_question("专业")
# y = answer_question('我想知道生物信息学这个专业和生物医学专业有什么区别？')
print(y)