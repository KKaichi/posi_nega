import pandas as pd
import csv

def positive_negative_dict_create():
    ###辞書データをデータフレームに読み込む
    # カラム名と値の位置ずれを制御
    pd.set_option('display.unicode.east_asian_width', True)
    positive_negative_dic_tmp = pd.read_csv('pn.csv.m3.120408.trim', names=['word_pn_oth'])
    #positive_negative_dic_tmp = pd.read_csv('pn.csv.m3.120408.trim', names=['word_pn_oth'])

    ###データフレームを区切り文字で展開
    positive_negative_dic_tmp_2 = positive_negative_dic_tmp['word_pn_oth'].str.split('\t', expand=True)

    ###感情極性値のノイズを削除
    positive_negative_dic_tmp_3 = positive_negative_dic_tmp_2[(positive_negative_dic_tmp_2[1] == 'p') | (positive_negative_dic_tmp_2[1] == 'e') | (positive_negative_dic_tmp_2[1] == 'n')]

    ###感情極性値を数値に置換
    # 不要カラムの削除
    positive_negative_dic_tmp_4 = positive_negative_dic_tmp_3.drop(positive_negative_dic_tmp_3.columns[2], axis=1)
    positive_negative_dic_tmp_4[1] = positive_negative_dic_tmp_4[1].replace({'p':1, 'e':0, 'n':-1})

    ###データフレームを dict 型に変換
    keys = positive_negative_dic_tmp_4[0].tolist()
    values = positive_negative_dic_tmp_4[1].tolist()
    positive_negative_dic = dict(zip(keys, values))

    return positive_negative_dic

def dict_write_to_csv(dictionaly):
    with open('meishi_positive_negative_dict.csv', mode = 'w', encoding = 'utf-8') as dict_file:
      writer = csv.writer(dict_file)
      for key, value in dictionaly.items():
        writer.writerow([key, value])

    return 0

def main():
  postive_negative_dict = positive_negative_dict_create()
  dict_write_to_csv(postive_negative_dict)

main()
