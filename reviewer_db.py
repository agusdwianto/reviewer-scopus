import sqlite3
from typing import List, Dict, Any
from pathlib import Path

REVIEWERS_TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS reviewers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    affiliation TEXT,
    orcid TEXT,
    keywords TEXT,
    created_at TEXT NOT NULL
);
'''


def get_conn(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn


def init_db(db_path: str):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.executescript(REVIEWERS_TABLE_SCHEMA)
    conn.commit()
    conn.close()


def add_reviewer(db_path: str, name: str, email: str, affiliation: str = None, orcid: str = None, keywords: str = None):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO reviewers (name,email,affiliation,orcid,keywords,created_at) VALUES (?,?,?,?,?,datetime("now"))',
        (name, email, affiliation, orcid, keywords)
    )
    conn.commit()
    cur.close()
    conn.close()


def list_reviewers(db_path: str) -> List[Dict[str, Any]]:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id, name, email, affiliation, orcid, keywords, created_at FROM reviewers ORDER BY id DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            'id': r[0],
            'name': r[1],
            'email': r[2],
            'affiliation': r[3],
            'orcid': r[4],
            'keywords': r[5],
            'created_at': r[6]
        }
        for r in rows
    ]


def export_csv_bytes(db_path: str) -> bytes:
    import io, csv
    rows = list_reviewers(db_path)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'name', 'email', 'affiliation', 'orcid', 'keywords', 'created_at'])
    for r in rows:
        writer.writerow([r['id'], r['name'], r['email'], r['affiliation'], r['orcid'], r['keywords'], r['created_at']])
    return output.getvalue().encode('utf-8')
