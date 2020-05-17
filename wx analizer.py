# 微信好友信息爬取+数据可视化，在‘ 保护我方鲁班八号’朋友代码上优化
# encoding=utf-8
__author__ = 'wind'
__location__ = '上海'
__date__ = '2020-04-22'
from wxpy import *
import re
import jieba
import numpy
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import imageio
from wordcloud import WordCloud,ImageColorGenerator
from matplotlib.patches import Polygon
from matplotlib.colors import rgb2hex
from mpl_toolkits.basemap import Basemap
# 微信登录
def wx_login():
  try:
    #初始化机器人，扫码登录
    bot = Bot()
    #获取好友列表
    frinds = bot.friends()
    #wxpy.api.chats.chats.Chats对象是多个聊天对象的合集，
    # 可用于搜索或统计，可以搜索和统计的信息包括sex(性别)、province(省份)、city(城市)和signature(个性签名)等
    print(type(frinds))
    #输出好友列表
    for i in frinds:
      print(i)
  except Exception as e:
    print(e.args)
    wx_login()
  return frinds
# 数据可视化
#统计男女性别信息
def wx_friend_sex_infor(friends):
  sex_dict = {'male':0,'female':0,'other':0}
  for friend in friends:
    if friend.sex == 1:
      sex_dict['male'] += 1
    elif friend.sex == 2:
      sex_dict['female'] += 1
    else:
      print(friend,'性别未标记！')
      sex_dict['other'] += 1
  print(sex_dict)
  wx_show_sex_infor(sex_dict)
# pie(x, explode=None, labels=None,
#   colors=('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'),
#   autopct=None, pctdistance=0.6, shadow=False,
#   labeldistance=1.1, startangle=None, radius=None,
#   counterclock=True, wedgeprops=None, textprops=None,
#   center = (0, 0), frame = False )
# 参数说明
# x    (每一块)的比例，如果sum(x) > 1会使用sum(x)归一化
# labels (每一块)饼图外侧显示的说明文字
# explode (每一块)离开中心距离
# startangle 起始绘制角度,默认图是从x轴正方向逆时针画起,如设定=90则从y轴正方向画起
# shadow 是否阴影
# labeldistance label绘制位置,相对于半径的比例, 如<1则绘制在饼图内侧
# autopct 控制饼图内百分比设置,可以使用format字符串或者format function
#     '%1.1f'指小数点前后位数(没有用空格补齐)
# pctdistance 类似于labeldistance,指定autopct的位置刻度
# radius 控制饼图半径
# 返回值:
# 如果没有设置autopct,返回(patches, texts)
# 如果设置autopct,返回(patches, texts, autotexts)
def wx_show_sex_infor(data):
  labers = ['男性','女性','未标定']
  data = [data['male'],data['female'],data['other']]
  patches,l_text,p_text = plt.pie(data,data=data,labels=labers,autopct='%.2f',shadow=True)
  for t in l_text:
    t.set_fontproperties(matplotlib.font_manager.FontProperties(fname="C:\simfang.ttf"))#让labers可以用中文显示
  plt.savefig('sex.png')
  plt.show()
  plt.close()
def wx_friend_location_infor(friends):
  loction_dict = {'北京': 0, '上海': 0, '天津': 0, '重庆': 0,
           '河北': 0, '山西': 0, '吉林': 0, '辽宁': 0, '黑龙江': 0,
           '陕西': 0, '甘肃': 0, '青海': 0, '山东': 0, '福建': 0,
           '浙江': 0, '台湾': 0, '河南': 0, '湖北': 0, '湖南': 0,
           '江西': 0, '江苏': 0, '安徽': 0, '广东': 0, '海南': 0,
           '四川': 0, '贵州': 0, '云南': 0,
           '内蒙古': 0, '新疆': 0, '宁夏': 0, '广西': 0, '西藏': 0,
           '香港': 0, '澳门': 0}
  for friend in friends:
    if friend.province in loction_dict.keys():
      loction_dict[friend.province] += 1
  #转成JSON格式：
  loction_list = []
  for key,value in loction_dict.items():
    loction_list.append({'name':key,'sum':value})
  print(loction_list)
def wx_show_location_infor():
  pass
#显示好友个签信息
def wx_show_signature(friends):
  #统计好友签名
  for friend in friends:
    #对数据进行清洗，排除标点信息的干扰
    pattern = re.compile(r'[一-龥]+')
    filterdata = re.findall(pattern, friend.signature)
    with open('signature.txt', 'a', encoding='utf-8', newline='') as f:#'a'表示打开文件方式为追加（append)
     f.write('\n'.join(filterdata))#因为newline设定为'',如果用''.join则会让生成的文件有很多换行，所以用'\n\回车符
  f.close()
  # 读取文件数据
  with open('signature.txt', 'r', encoding='utf-8', newline='\n') as f:
    content = f.read()
  f.close()
  segment = jieba.lcut(content)
  words_df = pd.DataFrame({'segment':segment})
  #读取stopwords
  stopwords = pd.read_csv('stopwords.txt',index_col=False,quoting=3,sep=' ',names=['stopword'],encoding='gb18030')
  huiche=pd.Series(['\n'])
  finalstopword=stopwords.stopword.append(huiche)#停用词增加回车'\n'
  words_df = words_df[~words_df.segment.isin(finalstopword)]
  print(words_df)
  words_stat = words_df.groupby(by=['segment'])['segment'].agg({'计数': numpy.size})
  words_stat = words_stat.reset_index().sort_values(by=['计数'], ascending=False)
  #设置词云属性
  color_mask = imageio.imread('back.jpg')#此文件必须提前放有，不能为白板文件
  wordcloud = WordCloud(font_path='C:\simfang.ttf',    #设置字体可以显示中文
             background_color= 'white',  #背景颜色是白色
             max_words=100,        #设置词云显示的最大词数
             mask=color_mask,       #设置背景图片
             max_font_size=100,      #设置词云中字体的最大值
             random_state=22,
             width=800,height=600,margin=2,#设置图片默认大小
  )
  # 生成词云, 可以用generate输入全部文本,也可以我们计算好词频后使用generate_from_frequencies函数
  word_frequence = {x[0]: x[1] for x in words_stat.head(20).values}
  print(word_frequence)
  wordcloud.generate_from_frequencies(word_frequence)
  # 从背景图片生成颜色值
  image_colors = ImageColorGenerator(color_mask)
  plt.imshow(wordcloud)
  plt.axis("off")
  plt.show()
  plt.close()
  wordcloud.to_file('output.png')


if __name__ == '__main__':
  friends = wx_login()
  print('~~~~~~~~~~~~~~~~~~~~1~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
  wx_friend_sex_infor(friends)
  print('~~~~~~~~~~~~~~~~~~~~~2~~~~~~~~~~~~~~~~~~~~~~~~~~~')
  wx_friend_location_infor(friends)
  print('~~~~~~~~~~~~~~~~~~~~~~3~~~~~~~~~~~~~~~~~~~~~~~~~~')
  wx_show_signature(friends)
  print('~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~')
