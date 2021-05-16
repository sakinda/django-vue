import os
import sys
import django
import copy

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBeta02.settings")
django.setup()

from restaurant_beta_02 import models


note = models.DataNoteBase.objects.all()
print(note)
note_list = []
note_dict = {}
for n in note:
    # print(type(n.note_content))
    # note_dict[n.note_id] = n.note_content
    # note_dict['成分'] = [n.note_id, ]
    note_list.append({n.id: n.note_content, '成分': [n.id, ]})

# print(note_list)


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
        print('============================================')
        print('k:', k)
        print('============================================')
        list22_result = []
        list22_keys = []
        list22_result_new = []
        list22_keys_new = []
        result = {}

        for i in range(0, len(list1)):

            print('i:', i)
            # print('len(list11_result)', len(list11_result))
            # print('list1:', list1)
            # print('list11_result: ', list11_result)
            for x in list22_result:
                list22_keys.append(list(x.keys())[0])
            for j in range(0, len(list11_result)):  # 两两相加
                # if list(list11_result[i].keys())[0] < list(list1[j].keys())[0]:
                    # print('list(list1[j].keys()):', list(list1[j].keys()))
                    # new_list = []

                # print(list(list1[i].keys())[0])
                # print(list(list11_result[j].values())[1])
                #
                # print(list(list1[i].keys())[0] in list(list11_result[j].values())[1])
                if list(list1[i].keys())[0] not in list(list11_result[j].values())[1]:
                    new_list = copy.deepcopy(list(list11_result[j].values())[1])
                    if isinstance(new_list, list):
                        new_list.append(list(list1[i].keys())[0])
                    # print('new_list：', new_list)

                    result = {
                        list(list11_result[j].keys())[0] + list(list1[i].keys())[0]: list(list11_result[j].values())[
                                                                                         0] + ',' +
                                                                                     list(list1[i].values())[0],
                        '组成': new_list}
                    # print(result)

                    # ############### 确保result没有包含在上一轮得到的 list22_result的key中  ##############
                    verify = list(list11_result[j].keys())[0] + list(list1[i].keys())[0]
                    if verify not in list22_keys:
                        list22_result.append(result)
                    # ############### 确保result没有包含在上一轮得到的 list22_result的key中  ##############

                    # sak = sak + 1
                    # print(sak)
        # for x in list22_result:
        #     list22_keys.append(list(x.keys())[0])
        #
        # for x in range(0, len(list22_keys)):
        #     # print(list(x.keys())[0])
        #     # print(list33_keys)
        #     if list22_keys[x] not in list22_keys_new:
        #         list22_result_new.append(list22_result[x])
        #         list22_keys_new.append(list22_keys[x])

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
    print('list_keys: ', len(list_result), '个元素',  list_keys)
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

    print('就方法：', 2600)

    # for x in list_result_new:
    #     print(x)


main()

def copy_base_note():
    base_note = models.DataNoteBase.objects.all()
    for bn in base_note:
        print(bn.id)
        note_object = models.DataSpecialNote.objects.create(
            note_id=bn.id,
            note=bn.note_content,
            component=[bn.id, ])
#
# copy_base_note()