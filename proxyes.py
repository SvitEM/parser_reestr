import argparse
import asyncio
from typing import List, Any

import pandas as pd

import parser
import config


def load_data(file_name):
    df = pd.read_csv('test1000.csv')
    # post_df = pd.DataFrame()
    df['bday'] = pd.to_datetime(df['birthdate']).dt.strftime('%d-%m-%Y')
    df.dropna(axis=0, how='any', inplace=True)
    for col in ['last_name', 'first_name', 'mid_name']:
        df[col] = df[col].str.replace(r'(\w+) (\w+)', r'\1-\2', regex=True)
        df[col] = df[col].str.replace(' ', '')
    df['id'] = df['last_name'] + ' ' + df['first_name'] + ' ' + df['mid_name']
    # post_df = df.copy()
    post_df = df.drop(['last_name', 'first_name', 'mid_name', 'birthdate'], axis=1)
    post_df.head()
    return post_df


arg_parser = argparse.ArgumentParser(description='Process some integers.')
arg_parser.add_argument('--proxies', required=True,
                        help='proxies file name')
arg_parser.add_argument('--data', required=True,
                        help='data for parse')

arg_parser.add_argument('--type', choices=config.allowed_types,
                        help='data type', required=True)

args = arg_parser.parse_args()

proxies: List[str]
with open(args.proxies) as f:
    proxies = f.read().split('\n')

post_df = load_data(args.data)

data = {
    'ids': post_df.to_dict(orient="records"),
    'type': args.type
}

resp = asyncio.run(parser.get_paused_info(params=data, proxies=proxies))
print(resp)
