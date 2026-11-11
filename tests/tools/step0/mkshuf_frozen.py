import sqlite3, shutil, random, sys
seed, dst = int(sys.argv[1]), sys.argv[2]
shutil.copy('/tmp/sbx/frozen/ledger_frozen.sqlite', dst)
c = sqlite3.connect(dst); cols = [r[1] for r in c.execute('pragma table_info(sweep_tx)')]
rows = c.execute('select * from sweep_tx').fetchall(); random.Random(seed).shuffle(rows)
ddl = c.execute("select sql from sqlite_master where name='sweep_tx'").fetchone()[0]
c.execute('drop table sweep_tx'); c.execute(ddl); c.executemany(f'insert into sweep_tx values ({",".join("?"*len(cols))})', rows); c.commit()
print(seed, len(rows))
