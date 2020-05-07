import sys
sys.path.append("..")
from lib.utils.log import Log


log = Log("test.log")
log.debug("---测试开始----")
log.info("操作步骤")
log.warning("----测试结束----")
log.error("----测试错误----")