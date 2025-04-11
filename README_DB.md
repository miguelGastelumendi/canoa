<!--
   /* cSpell:locale en pt-br
   /* cSpell:ignore tablename
   /* mgd 2025-04-07
-->
# — Canoa Database —

## PostgresSQL #


## Name Conventions ##

*Foreign Keys* ```<tablename>__[<key_name>__]<foreign_tablename>_fk```

 Examples:
    - ```sep__users_fk```  sep.users_id -> users.id
    - ```sep__ins_by__users_fk```  sep.ins_by -> users.id

