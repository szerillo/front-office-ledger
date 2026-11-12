import sqlite3, shutil, random, sys, os
seed, dst = int(sys.argv[1]), sys.argv[2]
shutil.copy('/tmp/v2/ledger_v2.sqlite', dst); os.chmod(dst, 0o644)
c = sqlite3.connect(dst); cols = [r[1] for r in c.execute('pragma table_info(sweep_tx)')]
rows = c.execute('select * from sweep_tx').fetchall(); random.Random(seed).shuffle(rows)
ddl = c.execute("select sql from sqlite_master where name='sweep_tx'").fetchone()[0]
c.execute('drop table main.sweep_tx'); c.execute(ddl); c.executemany(f'insert into sweep_tx values ({",".join("?"*len(cols))})', rows); c.commit()
print(seed, len(rows))
