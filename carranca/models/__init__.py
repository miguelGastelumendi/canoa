"""
 SQLAlchemy Models Initialization

mgd
Equipe da Canoa -- 2025.05.14
"""

# cSpell:ignore: sqlalchemy SQLA

from sqlalchemy.orm import declarative_base

# https://stackoverflow.com/questions/45259764/how-to-create-a-single-table-using-sqlalchemy-declarative-base
SQLABaseTable = declarative_base()


# eof
