import os
import sys
import django
import copy
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBeta02.settings")
django.setup()

from restaurant_beta_02 import models

note = models.DataNoteBase.objects.all()
print(note)
note_list = [{1: '少辣', '组成': [1], 'max':0}, {2: '不要香菜', '组成': [2], 'max':1}, {4: '加麻', '组成': [4], 'max':2}, {8: '少味精', '组成':[8], 'max':3}, {16: '豆类过敏', '组成': [16], 'max':4}, {32: '大蒜过敏', '组成': [32], 'max':5}, {64: '不要姜蒜', '组成': [64], 'max':6}]
# note_list= [{1: '无特殊要求', '成分': [1], 'max': 0}, {2: '最低辣度', '成分': [2], 'max': 1}, {4: '少辣', '成分': [4], 'max': 2}, {8: '加辣', '成分': [8], 'max': 3}, {16: '加重辣', '成分': [16], 'max': 4}, {32: '尽量无花椒', '成分': [32], 'max': 5}, {64: '少麻', '成分': [64], 'max': 6}, {128: '加麻', '成分': [128], 'max': 7}, {256: '加重麻', '成分': [256], 'max': 8}, {512: '不要葱', '成分': [512], 'max': 9}, {1024: '不要香菜', '成分': [1024], 'max': 10}, {2048: '多小葱', '成分': [2048], 'max': 11}, {4096: '多香菜', '成分': [4096], 'max': 12}, {8192: '不要蒜', '成分': [8192], 'max': 13}, {16384: '不要姜', '成分': [16384], 'max': 14}, {32768: '不要味精', '成分': [32768], 'max': 15}, {65536: '少盐', '成分': [65536], 'max': 16}, {131072: '少糖', '成分': [131072], 'max': 17}, {262144: '少油', '成分': [262144], 'max': 18}, {524288: '煎炸类嫩些', '成分': [524288], 'max': 19}, {1048576: '豆类过敏', '成分': [1048576], 'max': 20}, {2097152: '面粉类过敏', '成分': [2097152], 'max': 21}, {4194304: '大米类过敏', '成分': [4194304], 'max': 22}, {8388608: '花生腰果过敏', '成分': [8388608], 'max': 23}, {16777216: '其他过敏', '成分': [16777216], 'max': 24}]

# note_dict = {}
# for n in note:
#     note_list.append({n.id: n.note_content, '成分': [n.id, ]})


# print(note_list)

t_start = time.time()

def main():
    list1 = note_list
    print(len(list1))

    list11_result = note_list
    list11_keys = []
    list11_result_new = []
    list11_keys_new = []

    list_result = []
    list_keys = []
    list_result_new = []
    list_keys_new = []

    for k in range(0, len(list1)):
        list22_result = []
        list22_keys = []
        list22_result_new = []
        list22_keys_new = []
        result = {}
        print('\n\n============================================')
        print('k:', k)
        print('============================================')
        print('len(list11_result):', len(list11_result))
        print('============================================')
        z = 0

        for j in range(0, len(list11_result)):

            # print('j:', j)

            for x in list22_result:
                list22_keys.append(list(x.keys())[0])

            y = list(list11_result[j].values())[2]
            # print('y:', y)

            z += 1
            print("\r j循环 %s" % (z), end="")


            for i in range(y+1, len(list1)):  # 两两相加

                print("\r 循环起点 %s" % (y+1), end="")
                if list(list1[i].keys())[0] not in list(list11_result[j].values())[1]:
                    new_list = copy.deepcopy(list(list11_result[j].values())[1])
                    if isinstance(new_list, list):
                        new_list.append(list(list1[i].keys())[0])
                    # print('new_list：', new_list)

                    result = {
                        list(list11_result[j].keys())[0] + list(list1[i].keys())[0]: list(list11_result[j].values())[
                                                                                         0] + ',' +
                                                                                     list(list1[i].values())[0],
                        '组成': new_list, 'max': list(list11_result[j].values())[2]}
                    # print(result)

                # ############### 确保result没有包含在上一轮得到的 list22_result的key中  ##############
                verify = list(list11_result[j].keys())[0] + list(list1[i].keys())[0]
                if verify not in list22_keys:
                    list22_result.append(result)
                # ############### 确保result没有包含在上一轮得到的 list22_result的key中  ##############

        # print('两两相加', list22_result)
        list11_result = list22_result
        list_result += list22_result
        # list22_result = []
    # print(list_result)

    # ############### 获得 list_key 列表  ##############
    for x in list_result:
        list_keys.append(list(x.keys())[0])
    # ############### 获得 list_key 列表  ##############

    # ############### 获得 不重复的 list_key_new 列表  ##############
    for x in range(0, len(list_keys)):
        # print(list(x.keys())[0])
        # print(list33_keys)
        if list_keys[x] not in list_keys_new:
            list_result_new.append(list_result[x])
            list_keys_new.append(list_keys[x])
    # ############### 获得 不重复的 list_key_new 列表  ##############

    list_keys.sort()
    list_keys_new.sort()
    print('list_keys: ', len(list_result), '个元素', list_keys)
    print('list_keys_new: ', len(list_result_new), '个元素', list_keys_new)
    print('=================================================================')
    print('list_result: ', len(list_result), '个元素', list_result)
    print('list_result_new: ', len(list_result_new), '个元素', list_result_new)

    # for r in list_result:
    #     print(list(r.values())[1])
    #     # print(list(r.keys())[0])
    #     # note_object = models.DataSpecialNote.objects.create(
    #     #     note_id=int(list(r.keys())[0]),
    #     #     note=list(r.values())[0],
    #     #     component=list(r.values())[1],)

    # print('就方法：', 2600)

    t_end = time.time()

    print(t_end - t_start)

main()


# def getList():
#     note = models.DataNoteBase.objects.all()
#     note_list = []
#     note_dict = {}
#     for n in note:
#         note_list.append({n.id: n.note_content, '成分': [n.id, ]})
#
#     print(note_list)
#
# getList()