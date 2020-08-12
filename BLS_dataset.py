# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 15:53:54 2020

@author: Johnny Tsai
"""

import pandas as pd
import json
import requests

def get_bls_data(series, start, end):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"seriesid": series,"startyear":"%d" % (start), "endyear":"%d" % (end)})
    p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    try:
        df = pd.DataFrame()
        for series in json_data['Results']['series']:
            df_initial = pd.DataFrame(series)
            series_col = df_initial['seriesID'][0]
            for i in range(0, len(df_initial) - 1):
                df_row = pd.DataFrame(df_initial['data'][i])
                df_row['seriesID'] = series_col
                if 'code' not in str(df_row['footnotes']): 
                    df_row['footnotes'] = ''
                else:
                    df_row['footnotes'] = str(df_row['footnotes']).split("'code': '",1)[1][:1]
                df = df.append(df_row, ignore_index=True)
        return df
    except:
        json_data['status'] == 'REQUEST_NOT_PROCESSED'
        print('BLS API has given the following Response:', json_data['status'])
        print('Reason:', json_data['message'])


start = 2000
end = 2020
series = ['pcu325199325199p','pcu3251803251806','pcu332618332618','pcu3149943149947','pcu325212325212p']

df = get_bls_data(series=series, start=start, end=end)
df['month'] = df['year'] + df['period'].str.replace('M','')
df['value'] = df['value'] + df['footnotes']

df = df.pivot(index='month', columns='seriesID', values='value')
df = df[['pcu325212325212p','pcu3251803251806', 'pcu3149943149947','pcu332618332618','pcu325199325199p']]

df.rename(columns=
     {'pcu325199325199p':'CHEMICALS_pcu325199325199p', 
      'pcu3251803251806':'CARBON_pcu3251803251806', 
      'pcu332618332618':'STEEL_pcu332618332618', 
      'pcu3149943149947':'CORD_pcu3149943149947', 
      'pcu325212325212p':'SYNRUB_pcu325212325212p'}, inplace=True)

#print(df.head())

writer = pd.ExcelWriter('bls.xlsx', engine='xlsxwriter', options={'strings_to_numbers': True})
df.to_excel(writer, sheet_name='Sheet1', index=True)
writer.save()
#---------------------------------------------------------------

