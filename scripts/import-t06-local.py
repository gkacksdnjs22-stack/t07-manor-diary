"""Import a saved T06 snapshot into one verified LOCAL account, atomically.

Never connects to production. Abort on existing IDs or unexpected fields rather
than overwriting anything. Back up the whole local database before importing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument('--email', required=True)
parser.add_argument('--snapshot', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
files = [p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name != 'metadata.sqlite']
if len(files) != 1:
    raise RuntimeError('Expected exactly one isolated local diary database')
snapshot = json.loads(Path(args.snapshot).read_text(encoding='utf-8'))
tables = [('plans','plans'),('tasks','tasks'),('executions','executions'),
          ('reviews','reviews'),('plan_versions','planVersions'),('completions','completions')]
db = sqlite3.connect(files[0])
db.row_factory = sqlite3.Row
db.execute('PRAGMA foreign_keys=ON')
user = db.execute('SELECT id FROM users WHERE email=?',(args.email.strip().lower(),)).fetchone()
if not user:
    raise RuntimeError('The specified local account does not exist')
owner = user['id']
before = {table:[dict(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY id')] for table,_ in tables}
prepared = {}
for table,key in tables:
    columns = {row['name'] for row in db.execute(f'PRAGMA table_info({table})')}
    prepared[table] = []
    for original in snapshot[key]:
        row = {re.sub(r'(?<!^)([A-Z])',lambda m:'_'+m.group(1).lower(),k):v for k,v in original.items()}
        if table == 'plans':
            row['owner_id'] = owner
        if not set(row) <= columns:
            raise RuntimeError(f'Unexpected fields in {table}')
        if db.execute(f'SELECT 1 FROM {table} WHERE id=?',(row['id'],)).fetchone():
            raise RuntimeError(f'Existing ID in {table}; no data overwritten')
        if table in ['executions','completions']:
            row['request_key'] = owner+':'+row['request_key']
        prepared[table].append(row)
backup_dir = root/'outputs/t06-import'
backup_dir.mkdir(parents=True,exist_ok=True)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup = backup_dir/(stamp+'-local-before.sqlite')
with sqlite3.connect(backup) as target:
    db.backup(target)
with db:
    for table,_ in tables:
        for row in prepared[table]:
            names = list(row)
            sql = f'INSERT INTO {table} ('+','.join(names)+') VALUES ('+','.join('?' for _ in names)+')'
            db.execute(sql,[row[name] for name in names])
    if db.execute('PRAGMA foreign_key_check').fetchall():
        raise RuntimeError('Foreign key validation failed; rolled back')
    for table,_ in tables:
        for previous in before[table]:
            current = dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(previous['id'],)).fetchone())
            if current != previous:
                raise RuntimeError('Existing data changed; rolled back')
        for expected in prepared[table]:
            current = dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(expected['id'],)).fetchone())
            if any(current[k] != v for k,v in expected.items()):
                raise RuntimeError('Imported values differ; rolled back')
result = {'localOnly':True,'snapshotSha256':hashlib.sha256(Path(args.snapshot).read_bytes()).hexdigest(),
          'imported':{table:len(rows) for table,rows in prepared.items()},
          'existingRowsUnchanged':True,'foreignKeysValid':True,'backup':str(backup)}
(backup_dir/(stamp+'-result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
