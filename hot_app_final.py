'''
README

1. 라이브러리 불러오기
2. 필요 함수 생성
3. 필요 변수 생성
4. Streamlit 화면 구성

<변수 변화>
변경전 : im_export를 pd.DataFrame한 뒤에 im_export에 넣었음
변경후 : im_export를 pd.DataFrame한 뒤에 im_export_df에 넣었음

변경전 : url이 api와 크롤링에서 변수 이름이 겹침
변경후 : url이 api, url_craw가 크롤링 url

변경전 : result가 api와 도시 기본정보에서 겹침
변경후 : result가 api, result_whether이 도시기본정보

변경전 : im_export가 날씨정보 가져올때 덮어씌워짐
변경후 : im_export_whether로 고침

<남은 과제>
1.sidebar의 라디오를 장소추천으로 하면 맨 위에 장소선택하는 셀렉트박스가 없어져야 하는데
함수를 안쓰고 하다보니 얘를 뒤로 넣으면 option값 전달이 안되서 어떻게 뒤로 옮길지 고민해봐야함

2. 이미지보고 장소 예측하는 부분 마무리

3. 장소현황과 장소추천 모두 지도 넣으면 좋을듯(사진 넣고, 작은글씨 위도경도랑 주소?)
https://zzsza.github.io/mlops/2021/02/07/python-streamlit-dashboard/

4. 메모장 기능있음

5. 깃에 올려서 배포하는법
https://zzsza.github.io/mlops/2021/02/07/python-streamlit-dashboard/

6. KT 통신데이터 이용한거다! 실시간 도시데이터 메뉴얼 참고하기

7. 남여비율 도넛차트에서 한글 깨져서 일단 영어로 다시 고치기

8. 셀렉트박스에 이름 바꾸기

9. 지도 탭에서 셀렉트박스 다시 선택해야지 지도 나옴

10. 크롤링한거 url 클릭하면 이동?

11. 깃허브 작업

12. wheat 우리한테 맞게 바꿔야함 템플릿도 너무 똑같으니까 변화주자(미리보기 사진도 교체)
'''


#####################1.라이브러리 불러오기#################################
import urllib.request 
import json 
import pandas as pd 
import xmltodict
import streamlit as st

# 크롤링
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import io
import matplotlib.pyplot as plt
import cv2
from tensorflow.keras.models import load_model, save_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import branca
# 비슷한 분위기 추천인데 다 필요할지는 의문
from datetime import datetime
import os

# 시각화
import plotly.express as px # 파이, 도넛차트
import plotly.graph_objects as go # gauge


# 웹 화면 넓이 설정
st.set_page_config(layout="wide")


from streamlit_echarts import st_echarts # echarts

####################2.필요 함수 생성#######################################
def geocoding(address):
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    location = geolocoder.geocode(address)
    lati = location.latitude
    long = location.longitude
    return lati, long

# location = '서울 중구 명동8길 27'
# lati,long =geocoding('서울 중구 명동8길 27')
# m = folium.Map(location=[lati,long], zoom_start=11)
# icon = folium.Icon(color="red")
# folium.Marker(location=[lati, long], popup="환자위치", tooltip="환자위치: "+location, icon=icon).add_to(m)

#####################3.필요 변수 생성####################################
# -------------관광 스팟 50개를 보여주는 형식----------------------------
hd = pd.read_excel('C:/Users/User/Downloads/서울시 주요 50장소 목록.xlsx')

# option 지정을 위해 selectbox만 여기서 설정
option = st.selectbox('Choice the place you want to know',
                     (hd['장소명']),index=0)

for i in range(50):
    if option == hd['장소명'][i]:
        location = hd['위치'][i]
        r_location = hd['장소명'][i]
        lati,long =geocoding(location)
        m = folium.Map(location=[lati,long], zoom_start=17)
        #icon = folium.Icon(color="red")
        #folium.Marker(location=[lati, long], popup="환자위치", tooltip="환자위치: "+location, icon=icon).add_to(m)

# api 인증키와 주소
key = '4e6e667978766f6b363273776b4548'
START = 1
END = 150
CHR = option
url = f'http://openapi.seoul.go.kr:8088/{key}/xml/citydata/{START}/{END}/{CHR}'

# 데이터 가져오기
url = urllib.parse.quote(url,safe=':/?-=.')
response = urllib.request.urlopen(url)
xml_parse = xmltodict.parse(response)
xml_dict = json.loads(json.dumps(xml_parse))
result = xml_dict['SeoulRtd.citydata']['CITYDATA']['LIVE_PPLTN_STTS']['LIVE_PPLTN_STTS']

im_export = pd.json_normalize(result)
im_export_df = pd.DataFrame(im_export)
im_export2 = im_export_df.loc[:,['AREA_CONGEST_LVL','MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE', 'PPLTN_RATE_20','PPLTN_RATE_30','PPLTN_RATE_40','RESNT_PPLTN_RATE','NON_RESNT_PPLTN_RATE','PPLTN_TIME']]

im_export2.columns=['붐빔 정도','남성 비율','여성 비율','20대','30대','40대','놀러 온 사람 비율','거주자 비율','업데이트 시간']

result5 = xml_dict['SeoulRtd.citydata']['CITYDATA']['ROAD_TRAFFIC_STTS']['ROAD_TRAFFIC_STTS']
im_export3 = pd.json_normalize(result5)
im_export3 = pd.DataFrame(im_export3)
im_export3['SPD'] = im_export3['SPD'].astype('float') # 도로 상황

# --------------도시 기본 정보-날씨 ------------------
result_whether = xml_dict['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']
im_export_whether = pd.json_normalize(result_whether)
im_export_whether = pd.DataFrame(im_export_whether)

# ---------------------- 크롤링 후 관련 기사 보여주기 -----------------------
query = option
url_craw = f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query={query}'
response = requests.get(url_craw)

dom = BeautifulSoup(response.text,'html.parser')

elements2 = dom.select('.list_news > .bx')

urls = []
for element in elements2:
    url_element = element.find('a', href=True)
    if url_element:
        url_craw = url_element['data-url']
        urls.append(url_craw)
titles = []
for element in elements2:
    title_element = element.find('a', {'class': 'news_tit'})['title']
    if title_element:
        title = title_element
        titles.append(title)

news = pd.DataFrame({'뉴스 제목':titles,'url':urls})


# -------------------------아이콘?


icon = ["https://img.icons8.com/doodle/48/000000/user-male--v1.png", "https://img.icons8.com/doodle/48/000000/user-female--v1.png", "https://search.pstatic.net/sunny/?src=https%3A%2F%2Fpreview.files.api.ogq.me%2Fv1%2Fpreview%2FIMAGE%2F8ee1c6b9%2F5d5bd9b6c1ee8%2F067680666.jpeg%3Fformat%3Dw1280_cc&type=sc960_832"]


# 비율 리스트
ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
ratios = [float(im_export2['남성 비율'])/100,float(im_export2['여성 비율'])/100,float(im_export2['놀러 온 사람 비율'])/100]
# 각 비율마다 진행률 업데이트
k = ['남성 비율','여성 비율','놀러 온 사람 비율']
i = 0

# 차트 편의성을 위한 im_export2 값들 변수에 할당
com = im_export2['붐빔 정도'][0]
man = float(im_export2['남성 비율'][0])
wom = float(im_export2['여성 비율'][0])
age_20 = float(im_export2['20대'][0])
age_30 = float(im_export2['30대'][0])
age_40 = float(im_export2['40대'][0])
age_etc = 100-age_20-age_30-age_40
trav = float(im_export2['놀러 온 사람 비율'][0])
update_time = im_export2['업데이트 시간'][0]


# ----------------------- guage chart--------------
# # hand의 여유,보통,붐빔,매우붐빔을 차트의 중간값으로 매핑
gauge_value = 0
if im_export2['붐빔 정도'][0] == "여유":
    gauge_value = 5
elif im_export2['붐빔 정도'][0] == "보통":
    gauge_value = 15
elif im_export2['붐빔 정도'][0] == "약간 붐빔":
    gauge_value = 25
else:
    gauge_value = 35

plot_bgcolor = "#ffffff"
quadrant_colors = [plot_bgcolor, "#F1BCAE", "#F5DDAD", "#E9E1D4", "#C9DECF"] # 13.떨어진 꽃잎
quadrant_text = ["","<b>매우붐빔</b>", "<b>붐빔</b>","<b>보통</b>","<b>여유</b>", ""]
n_quadrants = len(quadrant_colors) - 1

current_value = gauge_value
min_value = 0
max_value = 40
hand_length = np.sqrt(2) / 10
hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

fig_gauge = go.Figure(
    data=[
        go.Pie(
            values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
            rotation=90,
            hole=0.4,
            marker_colors=quadrant_colors,
            text=quadrant_text,
            textinfo="text",
            hoverinfo="skip"
        ),
    ],
    layout=go.Layout(
        showlegend=False,
        margin=dict(b=0,t=10,l=10,r=10),
        width=400,
        height=400,
        shapes=[
            go.layout.Shape(
                type="circle",
                x0=0.48, x1=0.52,
                y0=0.48, y1=0.52,
                fillcolor="#333",
                line_color="#333"
            ),
            go.layout.Shape(
                type="line",
                x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                line=dict(color="#333", width=4)
            )
        ]
    )
)


###########################4.Streamlit 화면구성############################
# 레이아웃 구성하기
# st.set_page_config(layout="wide")
# img = load_img('/content/sea.jpg',target_size=(224,224,3))
# img = img_to_array(img)
# x_test = np.array(img)
# spot = model_res.predict(x_test.reshape(1,224,224,3))
# spot.argmax(axis=1)
# y_label[13]
# ---------------------------- y_label 정의 -------------------------------------
y_label = ['강남 MICE 관광특구', '동대문 관광특구', '명동 관광특구', '이태원 관광특구', '잠실 관광특구',
       '종로·청계 관광특구', '홍대 관광특구', '경복궁·서촌마을', '광화문·덕수궁', '창덕궁·종묘',
       '가산디지털단지역', '강남역', '건대입구역','잠실한강공원','잠실종합운동장','이촌한강공원','월드컵공원','서울숲공원','서울대공원','북서울꿈의숲','반포한강공원','망원한강공원',
 '뚝섬한강공원',',남산공원','국립중앙박물관·용산가족공원','인사동·익선동','영등포 타임스퀘어','여의도','압구정로데오거리','쌍문동 맛집거리','수유리 먹자골목','성수카페거리','가로수길',
 '북촌한옥마을','낙산공원·이화마을','노량진','DMC(디지털미디어시티)','고속터미널역','교대역','구로디지털단지역','서울역','선릉역','신도림역','신림역','신촌·이대역','역삼역','연신내역','용산역',
 '왕십리역','창동신경제중심지']
# 교대역(4장),동대문(9장),연신내역(6장), 창동 신경제(1장)
y = []
for i in range(0,50):
    if i == 38:
        k = [i]*4
        y.append(k)
    elif i == 1:
        k = [i]*9
        y.append(k)
    elif i == 46:
        k = [i]*6
        y.append(k)
    elif i == 49:
        k = [i]*1
        y.append(k)
    else:
        k = [i]*10
        y.append(k)
y_1 = []
for i in range(len(y)):
    for j in range(len(y[i])):
        y_1.append(y[i][j])
# -- -----------------------Sidebar--------------------------------------------
st.sidebar.title("🎡서울핫플🎡")
side = st.sidebar.radio("무엇을 보시겠습니까", ['장소현황', '장소추천'])

if side == '장소추천':
    image_file = st.file_uploader("가고싶은 분위기의 사진을 등록해주세요", type=['png', 'jpeg', 'jpg'])
    model = load_model('model_res.h5')
    col1, col2 = st.columns(2)
    #submit = st.button("예측하기")
    if image_file is not None:
        img = Image.open(image_file)
        with col1:
            st.image(img, caption='등록된 사진', use_column_width='always')
        # ts = datetime.timestamp(datetime.now())
        # imgpath = os.path.join('uploads', str(ts) + image_file.name)
        # outputpath = os.path.join('outputs', os.path.basename(imgpath))
        # with open(imgpath, mode="wb") as f:
        #     f.write(image_file.getbuffer())
            
        with col2:
            img = load_img(image_file, target_size=(224,224,3))
            img = img_to_array(img)
            x_test = np.array(img)
            spot = model.predict(x_test.reshape(1,224,224,3))
            spot = spot.argmax(axis=1)
            #st.write(y_label[spot[0]])
            for i in range(50):
                
                if y_label[spot[0]] == hd['장소명'][i]:
                    k = hd['장소명'][i]
                    link = f'서울핫플사진/{k}1.jpg'
            img2 = Image.open(link)
            st.image(img2,caption=f'예측결과: {y_label[spot[0]]}',use_column_width='always')
# 문장으로 장소 말해주기
# "추천드리는 장소는 '경복궁'입니다. 즐거운 여행되세요!"
    

###------------- Tab 생성------------------------------

elif side == '장소현황':
    # Tab 1 : 원래 기능, Tab 2 : 지도, Tab 3 : 장소추천

    # tabs 만들기
    tab1, tab2, tab3 = st.tabs(["장소 현황", "위치와 도로상황", "날씨와 뉴스"])

        # tab1 내용 구성
    with tab1:
        # 붐빔 정도 한줄평
        total = im_export_df['AREA_CONGEST_MSG'][0] # 데이터프레임에서 값만 추출
        st.write(total)
        
        col11, col12= st.columns(2)
        with col11:
            # 붐빔정도 gauge chart
            st.write("")
            st.write("")
            st.write("")
            st.write(fig_gauge)
            
            # 관람객 비율
            st.write(f"     이 중 여행객의 비율은 {trav} %이에요!")
            
            # 업데이트 시간
            st.write(f"     업데이트 시간 : {update_time}")
            
        with col12:
            # 남여 비율 파이차트
            fig_sex = px.pie(im_export2, values=[man, wom], names=['남자', '여자'],
                            color=['남자','여자'],
                            color_discrete_map={'남자':'#A3B6C5', '여자':'#EACACB'},#10.질감이 있는 브러시
                            width=350, height=350)
            #title='남녀 비율',
            fig_sex.update_traces(textposition='inside', textinfo='percent+label')
            #fig_sex.update_layout(showlegend=False)

            st.write(fig_sex)
            
            # 나이 비율 도넛 차트
            fig_age = px.pie(im_export2, values=[age_20, age_30, age_40, age_etc], names=['20대', '30대', '40대', '기타'],
                             color=['20대','30대','40대','기타'],
                            color_discrete_map={'20대':'#E1F1E7', '30대':'#B1D3C5', '40대':'#CFDD8E', '기타':'#E4BEB3'},
                            width=350, height=350) #title='연령대', 
            fig_age.update_traces(textposition='inside', textinfo='percent+label')
            #fig_age.update_layout(showlegend=False)

            st.write(fig_age)
            
    with tab2:
        
        # 도로 상황
        st.info('도로 상황')
        if im_export3['SPD'].mean() >= 25:
            st.write('도로 상황: 원활')
        elif im_export3['SPD'].mean() >= 15:
            st.write('도로 상황: 서행')
        else:
            st.write('도로 상황: 정체')
            
        #for idx, row in hospital_list[:5].iterrows():
        html = """<!DOCTYPE html>
        <html>
            <table style="height: 126px; width: 330px;"> <tbody> <tr>
                <td style="background-color: #2A799C;">
                <div style="color: #ffffff;text-align:center;">장소</div></td>
                <td style="width: 230px;background-color: #C5DCE7;">{}</td>""".format(r_location)+"""</tr>
                <tr><td style="background-color: #2A799C;">
                <div style="color: #ffffff;text-align:center;">장소</div></td>
                <td style="width: 230px;background-color: #C5DCE7;">{}</td>""".format(r_location)+"""</tr>
                <tr><td style="background-color: #2A799C;">
                    <div style="color: #ffffff;text-align:center;">거리</div></td>
                <td style="width: 230px;background-color: #C5DCE7;">{}</td>""".format(r_location)+""" </tr>
            </tbody> </table> </html> """
        iframe = branca.element.IFrame(html=html, width=350, height=150)
        popup_text = folium.Popup(iframe,parse_html=True)
        icon = folium.Icon(color="blue")
        folium.Marker(location=[lati,long],
                    popup=popup_text, tooltip=r_location, icon=icon).add_to(m)

        st_data = st_folium(m, width=1000)
        
        
    # tab3 내용 구성
    with tab3:
        # 도시 기본 정보 추출 - 날씨
        st.write("")
        st.info('현재 날씨')
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            col1.metric('기온',im_export_whether['TEMP'].astype(float),'°C')
        with col2:
            col2.metric('풍속',im_export_whether['WIND_SPD'].astype(float),' mph')
        with col3:
            col3.metric('습도',im_export_whether['HUMIDITY'].astype(float), ' %')
        with col4:
            st.markdown(im_export_whether['PCP_MSG'].values)

        # 관련 기사 크롤링
        st.write("")
        st.info('관련 기사')
        
        for i in range(len(news['뉴스 제목'])):
            txt='[{txt}]({link})'.format( txt = news['뉴스 제목'].iloc[i], link = news['url'].iloc[i])
            st.write(txt) 
        

    




# ------------------ tabs를 이용해서 장소와 크롤링을 나눠 볼까? -------------
#tab1, tab2 = st.tabs(['장소 정보','기사?'])


# # 버스 정보 갖고오기
# result = xml_dict['SeoulRtd.citydata']['CITYDATA']['BUS_STN_STTS']['BUS_STN_STTS']  # 데이터 부분 딕셔너리 키 확인 필요
# #주차장 정보 갖고오기
# result2 = xml_dict['SeoulRtd.citydata']['CITYDATA']['PRK_STTS']['PRK_STTS']
# #지하철 정보
# result3 = xml_dict['SeoulRtd.citydata']['CITYDATA']['SUB_STTS']
# #따릉이 정보
# result4 = xml_dict['SeoulRtd.citydata']['CITYDATA']['SBIKE_STTS']['SBIKE_STTS']
# #도로 길이 속도 정체
# result5 = xml_dict['SeoulRtd.citydata']['CITYDATA']['ROAD_TRAFFIC_STTS']['ROAD_TRAFFIC_STTS'] 
# # 노선수는 현재 에러
# # 데이터프레임으로 변환
# im_export = pd.json_normalize(result)
# im_export2 = pd.json_normalize(result2)
# im_export3 = pd.json_normalize(result3)
# im_export4 = pd.json_normalize(result4)
# im_export5 = pd.json_normalize(result5)


# --------------guage chart variable---------------


