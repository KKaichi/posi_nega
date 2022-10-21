import pandas as pd
import csv

def positive_negative_dict_create():
    ###辞書データをデータフレームに読み込む
    # 全角文字を考慮してカラム名と値の位置ずれを制御
    pd.set_option("display.unicode.east_asian_width", True)
    #感情値辞書の読み込み
    positive_negative_dic_tmp = pd.read_csv("wago.121808.pn", names=['judge_type_word'])

    ###データフレームを区切り文字で展開
    positive_negative_dic_tmp_2 = positive_negative_dic_tmp['judge_type_word'].str.split('\t', expand=True)
    
    ### 感情値ポジ/ネガの不要部分を削除
    positive_negative_dic_tmp_2[0] = positive_negative_dic_tmp_2[0].str.replace(r'\（.*\）', '', regex=True)

    ### 用言部分の登録内容を確認
    df_temp = positive_negative_dic_tmp_2[1].str.split(" ", expand=True)

    ### 辞書データのスクリーニング
    positive_negative_dic_tmp_3 = pd.concat([df_temp, positive_negative_dic_tmp_2[0]], axis=1)
    positive_negative_dic_tmp_4 = positive_negative_dic_tmp_3[positive_negative_dic_tmp_3[3].isnull()]
    positive_negative_dic_tmp_5 = positive_negative_dic_tmp_4[0]
    positive_negative_dic_tmp_6 = positive_negative_dic_tmp_5.drop_duplicates(keep='first')
    positive_negative_dic_tmp_6.columns = ['word', 'judge']
  
    ###データフレームを dict 型に変換
    keys = positive_negative_dic_tmp_6['word'].tolist()
    values = positive_negative_dic_tmp_6['judge'].tolist()
    positive_negative_dic = dict(zip(keys, values))

    return positive_negative_dic
  
def dict_write_to_csv(dictionaly):
    with open('positive_negative_dict.csv', mode = 'w', encoding = 'utf-8') as dict_file:
      writer = csv.writer(dict_file)
      for key, value in dictionaly.items():
        if(value == 'ポジ'):
          writer.writerow([key, 1])
        elif(value =='ネガ'):
          writer.writerow([key, -1])

    return 0

def main():
  postive_negative_dict = positive_negative_dict_create()
  dict_write_to_csv(postive_negative_dict)

main()


    
