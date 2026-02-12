class NoFeasibleSolutionError(Exception):
    """约束条件下无可行解"""
    pass

class InvalidConstraintError(Exception):
    """约束条件非法"""
    pass

class InvalidQuestionTypeNumber(Exception):
    """输入的题目数量不符合规范，因为不是正整数"""
    pass

class ConfigError(Exception):
    """配置文件不合法"""
    pass