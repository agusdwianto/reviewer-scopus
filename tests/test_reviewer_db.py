import os
import tempfile
from reviewer_db import init_db, add_reviewer, list_reviewers, export_csv_bytes


def test_add_and_list_reviewers(tmp_path):
    db_file = str(tmp_path / 'test_reviewers.db')
    # init
    init_db(db_file)
    # add
    add_reviewer(db_file, name='Alice', email='alice@example.com', affiliation='Univ X', orcid='0000-0000-0000-0000', keywords='ai,ml')
    add_reviewer(db_file, name='Bob', email='bob@example.com')
    # list
    rows = list_reviewers(db_file)
    assert len(rows) == 2
    names = [r['name'] for r in rows]
    assert 'Alice' in names and 'Bob' in names


def test_export_csv_bytes(tmp_path):
    db_file = str(tmp_path / 'test_reviewers2.db')
    init_db(db_file)
    add_reviewer(db_file, name='Charlie', email='c@example.com')
    csvb = export_csv_bytes(db_file)
    assert isinstance(csvb, bytes)
    txt = csvb.decode('utf-8')
    assert 'Charlie' in txt
