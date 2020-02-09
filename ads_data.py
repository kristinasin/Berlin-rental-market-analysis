from bs4 import BeautifulSoup as bs
import requests as rq
import time
import pandas as pd
from tqdm.notebook import tqdm
import numpy as np
import sqlite3
import argparse
from os import path


def get_data_by_page(page_num):
    if page_num == 1:
        url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten'
    else:
        url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten?pagenumber='+str(page_num)
    r = rq.get(url)
    r_html = r.text
    soup = bs(r_html, 'lxml')
    ad_data = soup.select('.border-top .result-list__listing--xl')
    kaltmiete = []
    s_metres = []
    n_rooms = []
    address = []
    ids = []
    for i in ad_data:
        pr_cr = i.select('.gutter-vertical-s .result-list-entry__primary-criterion .font-highlight')
        pr_cr = [cr.get_text() for cr in pr_cr]
        if len(pr_cr) == 3 and len(pr_cr[2].split(' ')[0])<4:
            addr=i.select('.result-list-entry__address .font-ellipsis')
            for ad_tag in addr:
                address.append(ad_tag.get_text())
            kaltmiete.append(pr_cr[0])
            s_metres.append(pr_cr[1])
            n_rooms.append(pr_cr[2].split(' ')[0])
            id_tag=i.attrs['data-id']
            ids.append(id_tag)
    ad_data_small = soup.select('.border-top .result-list__listing')
    for i in ad_data_small:
        pr_cr_sm = i.select('.gutter-vertical-s .result-list-entry__primary-criterion .font-highlight')
        pr_cr_sm = [cr.get_text() for cr in pr_cr_sm]
        if len(pr_cr_sm) == 3 and len(pr_cr_sm[2].split(' ')[0])<4:
            addr_sm = i.select('.result-list-entry__address .font-ellipsis')
            for ad_tag in addr_sm:
                address.append(ad_tag.get_text())
            kaltmiete.append(pr_cr_sm[0])
            s_metres.append(pr_cr_sm[1])
            n_rooms.append(pr_cr_sm[2].split(' ')[0])
            id_tag=i.attrs['data-id']
            ids.append(id_tag)
    return address, kaltmiete, s_metres, n_rooms, ids


def get_data_all_pages():
    address=[]
    kaltmiete=[]
    s_metres=[]
    n_rooms=[]
    ids=[]
    url='https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten'
    r = rq.get(url)
    r_html = r.text
    soup = bs(r_html, 'lxml')
    num_pages=int(str(soup.find_all("select", class_="select")).split('value="')[-1].split('"')[0])
    print('Total number of pages:', num_pages)
    for num in tqdm(range(1, num_pages+1)):
        time.sleep(1)
        n_data=get_data_by_page(num)
        address.extend(n_data[0])
        kaltmiete.extend(n_data[1])
        s_metres.extend(n_data[2])
        n_rooms.extend(n_data[3])
        ids.extend(n_data[4])
        
    return address, kaltmiete, s_metres, n_rooms, ids


def format_data(all_data_table):
    all_data_table['rooms']=all_data_table['rooms'].str.replace(',', '.')
    all_data_table['kaltmiete']=((all_data_table['kaltmiete'].str.replace(' €', '')).str.replace('.','')).str.replace(',','.')
    all_data_table['sq_m']=((all_data_table['sq_m'].str.replace(' m²', '')).str.replace('.','')).str.replace(',','.')
    all_data_table['rooms']=(pd.to_numeric(all_data_table['rooms'], errors='coerce')).astype('float32')
    all_data_table['kaltmiete']=(pd.to_numeric(all_data_table['kaltmiete'], errors='coerce')).astype('float32')
    all_data_table['sq_m']=(pd.to_numeric(all_data_table['sq_m'], errors='coerce')).astype('float32')
    full_data=all_data_table.dropna().reset_index(drop=True)
    full_data=full_data[full_data['kaltmiete']<20000]
    full_data=full_data[full_data['sq_m']<2000]
    return full_data


def sql_db(full_data, file_path, if_exists):
    con=sqlite3.connect(file_path, timeout=10)
    cur=con.cursor()
	
    if path.exists(file_path):
    	cur.execute("SELECT Count() FROM full_data")
    	n_ids=cur.fetchone()
    	print('Number of ads already in database:',n_ids[0])

    	cur.execute("SELECT id FROM full_data")
    	old_ids=cur.fetchall()
    	new_ids=[i for i in full_data['id'] if i not in [x[0] for x in old_ids]]
    	print('Number of new ads:',len(new_ids))

    	new_ads=full_data.loc[full_data['id'].isin(new_ids)]
    	new_ads.to_sql('full_data', con=con, if_exists=if_exists)
    	cur.execute("SELECT Count() FROM full_data")
    	n_ids=cur.fetchone()
    	print('Number of ads in updated database:',n_ids[0])
    else:
        full_data.to_sql('full_data', con=con, if_exists='replace')
        cur.execute("SELECT Count() FROM full_data")
        n_ids=cur.fetchone()
        print('Number of ads in database:',n_ids[0])
    con.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="specify the sql-database path", default='immobilienscout24.db')
    parser.add_argument("--if_exists", help="to replace or append values (append by default)", default='append')
    args = parser.parse_args()
    data=get_data_by_page(100)
    print('Total number of current ads:',len(data[0]))
    all_data_df=pd.DataFrame({'address':data[0], 'kaltmiete':data[1], 'sq_m':data[2], 'rooms':data[3], 'id':data[4]})
    full_data=format_data(all_data_df)
    full_data['district']=full_data['address'].apply(lambda x: x.split('(')[1].split(')')[0])
    sql_db(full_data, args.path, args.if_exists)


if __name__ == "__main__":
    main()


