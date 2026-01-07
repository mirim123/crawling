import pandas as pd
df=pd.read_csv('data/gangnamsis/gangnamsis_20260107_152005.csv')
#print(df.head())

'''
IQR = df['가격'].quantile(0.75) - df['가격'].quantile(0.25)
lower_bound = df['가격'].quantile(0.25) - (IQR * 1.5)
upper_bound = df['가격'].quantile(0.75) + (IQR *    1.5)
outliers = df[(df['가격'] < lower_bound) | (df['가격']  > upper_bound)]

#print(outliers.head())

clean_df = df[~df['시술종류'].isin(outliers['시술종류'])]
print(round(clean_df['가격'].mean()))
'''

# 지분주

df_inject=df[df['시술종류'].str.contains('주사', na=False)]
df_inject.to_csv('data/gangnamsis/data_pre/df_inject.csv', index=False)
print(f'주사 평균 금액: {df_inject.가격.mean()}')

df_face_inject=df_inject[df_inject['시술종류'].str.contains('윤곽|브이|페이스|얼굴|브이올렛|갸름|v|제로컷|조각')]
df_face_inject.to_csv('data/gangnamsis/data_pre/df_face_inject.csv', index=False)
print(f'얼굴주사 평점: {df_face_inject.평점.mean()}')

df_body_inject=df_inject[df_inject['시술종류'].str.contains('바디|체형|다리|허벅지|종아리|승마|팔뚝|팔|복부|엉덩이|복부지방|허리|옆구리')]
df_body_inject.to_csv('data/gangnamsis/data_pre/df_body_inject.csv', index=False)
print(f'바디주사 평점: {df_body_inject.평점.mean()}')


# 지방흡입
df_liposuction=df[df['시술종류'].str.contains('흡입|지방제거|지방흡입|추출', na=False)]
df_liposuction.to_csv('data/gangnamsis/data_pre/df_liposuction.csv', index=False)
print(f'지방흡입 평균 금액: {df_liposuction.가격.mean()}')


df_lipo_face=df_liposuction[df_liposuction['시술종류'].str.contains('얼굴|페이스|이중턱|심부볼')]
df_lipo_face.to_csv('data/gangnamsis/data_pre/df_lipo_face.csv', index=False)
print(f'지방흡입 얼굴 평균 금액: {df_lipo_face.가격.mean()}')


df_lipo_body=df_liposuction[df_liposuction['시술종류'].str.contains('바디|체형|다리|허벅지|종아리|승마|팔뚝|팔|복부|엉덩이|복부지방|허리|옆구리|가슴|전신|팻')]
df_lipo_body.to_csv('data/gangnamsis/data_pre/df_lipo_body.csv', index=False)
print(f'지방흡입 바디 평균 금액: {df_lipo_body.가격.mean()}')


# 지방이식
df_fat_graft=df[df['시술종류'].str.contains('지방이식|자가지방|지방이식술', na=False)]
df_fat_graft.to_csv('data/gangnamsis/data_pre/df_fat_graft.csv', index=False)
print(f'지방이식 평균 금액: {df_fat_graft.가격.mean()}')

df_fat_face=df_fat_graft[df_fat_graft['시술종류'].str.contains('얼굴|페이스')]
df_fat_face.to_csv('data/gangnamsis/data_pre/df_fat_face.csv', index=False)
print(f'지방이식 얼굴 평균 금액: {df_fat_face.가격.mean()}')

df_fat_body=df_fat_graft[df_fat_graft['시술종류'].str.contains('바디|체형|다리|허벅지|종아리|승마|팔뚝|팔|복부|엉덩이|복부지방|허리|옆구리|가슴|전신')]
df_fat_body.to_csv('data/gangnamsis/data_pre/df_fat_body.csv', index=False) 
print(f'지방이식 바디 평균 금액: {df_fat_body.가격.mean()}')


# 눈밑지방재배치
df_under_eye_fat=df[df['시술종류'].str.contains('눈밑지방재배치|눈밑지방이식|눈밑지방', na=False)]
df_under_eye_fat.to_csv('data/gangnamsis/data_pre/df_under_eye_fat.csv', index=False)   
print(f'눈밑지방재배치 평균 금액: {df_under_eye_fat.가격.mean()}')

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

df2=pd.read_csv('data/gangnamsis/gangnamsis_20260107_162847.csv')

# print(df2.head())

