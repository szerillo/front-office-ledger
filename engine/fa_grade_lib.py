"""Shared FA/extension helpers: name normalization + $-per-win by season."""
import unicodedata

def norm(n):
    n = unicodedata.normalize('NFKD', n or "")
    n = ''.join(c for c in n if not unicodedata.combining(c))
    return ' '.join(n.lower().replace('.', '').replace('-', ' ').split())

DPW = {2006:4.2,2007:4.5,2008:4.7,2009:4.7,2010:5.0,2011:5.2,2012:5.5,2013:6.0,
       2014:6.5,2015:7.0,2016:7.7,2017:8.0,2018:8.2,2019:8.0,2020:8.0,2021:8.5,
       2022:8.5,2023:9.0,2024:9.3,2025:9.5,2026:9.7}
