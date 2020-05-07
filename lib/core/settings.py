# -*- coding:utf-8 -*-
import ipaddress
import random
import os


'''随机UA'''
UA = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
    'Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0'
]


'''公共函数'''
def gen_random_ip():
    """
    生成随机的点分十进制的IP字符串
    """
    while True:
        ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32 - 1))
        if ip.is_global:
            return ip.exploded


def gen_fake_header():
    """
    生成伪造请求头
    """
    ua = random.choice(UA)
    ip = gen_random_ip()
    headers = {
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': 'uname=ysy;id=1',
        'User-Agent': ua,
        'X-Forwarded-For': ip,
        'X-Real-IP': ip
    }
    return headers

# 是否启动多线程机制
BLIND_THREAD = False

# sql检测优先级
UNION_DETECTED = "union_query"
ERROR_DETECTED = "error_query"
BOOL_DETECTED = "bool_query"
TIME_DETECTED = "time_query"
STACK_DETECTED = "stack_query"

# 随机字符
RANDOM_NUMBER_MARKER = "[RANDNUM]"
RANDOM_STRING_MARKER = "[RANDSTR]"
XSS_MARKER = "yy78pq"
XSS_TAG_MARKER = "<ysy>"

# 布尔表达式
BOOLEAN_EXPRESSION_MARKER = "[BOOL_EXPRE]"

# json文件名
DETECTED_FILE_NAME = "data/detected-payloads.json"
BOUNDARIES_FILE_NAME = "data/boundaries.json"
BOOLEAN_FILE_NAME = "data/boolean-payloads.json"
ERROR_FILE_NAME = "data/error-payloads.json"
STACKED_FILE_NAME = "data/stacked-payloads.json"
TIME_FILE_NAME = "data/time-payloads.json"
UNION_FILE_NAME = "data/union.json"
DATA_FILE_NAME = "data/data-payloads.json"

# sqlite文件名
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SQLITE_FILE_NAME = DIR_PATH + "/cache.db"

# 日志文件目录
LOG_DIR_NAME = "logs"

# 报错信息
MYSQL_ERROR = [
    'SQL syntax.*?MySQL', 'Warning.*?\Wmysqli?_', 'MySQLSyntaxErrorException', 'valid MySQL result',
    'check the manual that (corresponds to|fits) your (MySQL|MariaDB) server version',"Unknown column '[^ ]+' in 'field list'",
    'MySqlClient\.','com\.mysql\.jdbc','Zend_Db_(Adapter|Statement)_Mysqli_Exception','MySqlException','SQLSTATE\[\d+\]: Syntax error or access violation'
]
MSSQL_ERROR = [
    '\[SQL Server\]','ODBC Driver \d+ for SQL Server','Driver.*? SQL[\-\_\ ]*Server','OLE DB.*? SQL Server',
    '\bSQL Server[^&lt;&quot;]+Driver','Warning.*?\W(mssql|sqlsrv)_',
    '\bSQL Server[^&lt;&quot;]+[0-9a-fA-F]{8}','System\.Data\.SqlClient\.SqlException'
]
ORACLE_ERROR = [
    'ORA-\d{5}', 'Oracle error', 'Oracle.*?Driver', 'Warning.*?\W(oci|ora)_','oracle\.jdbc'
]

# DBMS 系统数据库
MSSQL_SYSTEM_DBS = ("Northwind", "master", "model", "msdb", "pubs", "tempdb", "Resource", "ReportServer", "ReportServerTempDB")
MYSQL_SYSTEM_DBS = ("information_schema", "mysql", "performance_schema", "sys")
PGSQL_SYSTEM_DBS = ("information_schema", "pg_catalog", "pg_toast", "pgagent")
ORACLE_SYSTEM_DBS = ("ADAMS", "ANONYMOUS", "APEX_030200", "APEX_PUBLIC_USER", "APPQOSSYS", "AURORA$ORB$UNAUTHENTICATED", "AWR_STAGE", "BI", "BLAKE", "CLARK", "CSMIG", "CTXSYS", "DBSNMP", "DEMO", "DIP", "DMSYS", "DSSYS", "EXFSYS", "FLOWS_%", "FLOWS_FILES", "HR", "IX", "JONES", "LBACSYS", "MDDATA", "MDSYS", "MGMT_VIEW", "OC", "OE", "OLAPSYS", "ORACLE_OCM", "ORDDATA", "ORDPLUGINS", "ORDSYS", "OUTLN", "OWBSYS", "PAPER", "PERFSTAT", "PM", "SCOTT", "SH", "SI_INFORMTN_SCHEMA", "SPATIAL_CSW_ADMIN_USR", "SPATIAL_WFS_ADMIN_USR", "SYS", "SYSMAN", "SYSTEM", "TRACESVR", "TSMSYS", "WK_TEST", "WKPROXY", "WKSYS", "WMSYS", "XDB", "XS$NULL")
SQLITE_SYSTEM_DBS = ("sqlite_master", "sqlite_temp_master")
ACCESS_SYSTEM_DBS = ("MSysAccessObjects", "MSysACEs", "MSysObjects", "MSysQueries", "MSysRelationships", "MSysAccessStorage", "MSysAccessXML", "MSysModules", "MSysModules2")
FIREBIRD_SYSTEM_DBS = ("RDB$BACKUP_HISTORY", "RDB$CHARACTER_SETS", "RDB$CHECK_CONSTRAINTS", "RDB$COLLATIONS", "RDB$DATABASE", "RDB$DEPENDENCIES", "RDB$EXCEPTIONS", "RDB$FIELDS", "RDB$FIELD_DIMENSIONS", " RDB$FILES", "RDB$FILTERS", "RDB$FORMATS", "RDB$FUNCTIONS", "RDB$FUNCTION_ARGUMENTS", "RDB$GENERATORS", "RDB$INDEX_SEGMENTS", "RDB$INDICES", "RDB$LOG_FILES", "RDB$PAGES", "RDB$PROCEDURES", "RDB$PROCEDURE_PARAMETERS", "RDB$REF_CONSTRAINTS", "RDB$RELATIONS", "RDB$RELATION_CONSTRAINTS", "RDB$RELATION_FIELDS", "RDB$ROLES", "RDB$SECURITY_CLASSES", "RDB$TRANSACTIONS", "RDB$TRIGGERS", "RDB$TRIGGER_MESSAGES", "RDB$TYPES", "RDB$USER_PRIVILEGES", "RDB$VIEW_RELATIONS")
MAXDB_SYSTEM_DBS = ("SYSINFO", "DOMAIN")
SYBASE_SYSTEM_DBS = ("master", "model", "sybsystemdb", "sybsystemprocs")
DB2_SYSTEM_DBS = ("NULLID", "SQLJ", "SYSCAT", "SYSFUN", "SYSIBM", "SYSIBMADM", "SYSIBMINTERNAL", "SYSIBMTS", "SYSPROC", "SYSPUBLIC", "SYSSTAT", "SYSTOOLS")
HSQLDB_SYSTEM_DBS = ("INFORMATION_SCHEMA", "SYSTEM_LOB")
H2_SYSTEM_DBS = ("INFORMATION_SCHEMA",)
INFORMIX_SYSTEM_DBS = ("sysmaster", "sysutils", "sysuser", "sysadmin")

# WAF探测payload
IPS_WAF_CHECK_PAYLOAD = "AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(\"XSS\")</script>',table_name FROM information_schema.tables WHERE 2>1--/**/; EXEC xp_cmdshell('cat ../../../etc/passwd')#"
WAF_ATTACK_VECTORS = (
    "search=<script>alert(1)</script>",
    "file=../../../../etc/passwd",
    "q=<invalid>foobar",
    "id=1 %s" % IPS_WAF_CHECK_PAYLOAD
)

# WAF指纹
WAF_FINGER_MARK = {
    # 360防火墙
    "360":
    {"header":"X-Powered-By-360WZB","status":"493","page":"wzws-waf-cgi"},
    # 云盾
    "yundun":
    {"header":"yundun","page":"errors.aliyun.com"},
    # 云锁
    "yunsuo":
    {"header":"yunsuo_session"},
    # 安全狗
    "dog":
    {"header":"waf 2.0"},
    # 腾讯云
    "tencent":
    {"page":"waf.tencent-cloud.com"},
    # 安全宝
    "anquanbao":
    {"header":"X-Powered-by-Anquanbao","status":"406"},
    # 百度云加速
    "baidu":
    {"header":"Yunjiasu-ngnix"},
    # 创宇盾
    "chuangyu":
    {"page":"365cyd.com"},
}