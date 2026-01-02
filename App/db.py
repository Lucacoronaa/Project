import os
from dotenv import load_dotenv, find_dotenv
from sqlmodel import SQLModel, create_engine, Session, text
from datetime import datetime
from dateutil import parser

load_dotenv(find_dotenv())  # carica .env (anche risalendo le cartelle)

DATABASE_URL = os.getenv("DATABASE_URL")

print("database_URL LETTA", DATABASE_URL is not None)

engine = create_engine(DATABASE_URL, echo = False, pool_pre_ping = True)


descrizione = input("Descrizione: ").strip()
amount_row = input("Importo: ").strip().replace(",", ".")
subcat_raw = input("SuBcat ID: ").strip()
date_raw = input("Data/Ora: ").strip()

amount = float(amount_row)
subcategoryid = int(subcat_raw) if subcat_raw else None



datestate = None
if date_raw:
    datestate = parser.parse(date_raw)

# INSERT

with engine.begin() as conn:
        if datestate is None:
                row = conn.execute(text("""
                                        INSERT INTO Movimenti (descrizione, amount, subcategoryid)
                                        VALUES (:descrizione, :amount, :subcategoryid)
                                        RETURNING id, datestate, description, amount, subcategoryid;
                                        """), {"descrizione": descrizione,
                                                "amount": amount,
                                                "subcategoryid": subcategoryid},).fetchone()
        else:
            row = conn.execute(
            text("""
                INSERT INTO Movimenti (descrizione, amount, subcategoryid, datestate)
                VALUES ( :descrizione, :amount, :subcategoryid,:datestate)
                RETURNING id, descrizione, amount, subcategoryid,datestate;
                """),
            { "descrizione": descrizione, "amount": amount, "subcategoryid": subcategoryid, "datestate": datestate},
        ).fetchone()

print("✅ Inserito:")
print(dict(row._mapping))      

                









#PROVA PER VEDERE SE RIESCO A LEGGERE IL DB
"""
with engine.connect() as conn:
    # 1) Test connesione
    result = conn.execute(text("SELECT 1;")).fetchone()
    print("COnnessione al DB OK: ", result)

    # 2) Leggi la Tabella Movimenti
    rows = conn.execute(text(""""""
                            select m.id, m.descrizione, m.amount, mc.macro_category, sc.sub_category, mc.type, m.datestate 
                            from neondb.public.movimenti m
                            join neondb.public.sub_categories sc
                                on m.subcategoryid = sc.id
                            join neondb.public.macro_categories mc 
                                on sc.macroid = mc.id
                            """""")).fetchall()
    
    print(f"righe lette : {len(rows)}")

    for r in rows:
        print(dict(r._mapping))
"""