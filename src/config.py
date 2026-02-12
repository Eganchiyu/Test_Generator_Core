from math import floor
from errors import *
import yaml


class Config:
    """
    配置解析类。

    负责：
    1. 读取 config.yaml 文件
    2. 校验题型数量与难度分布合法性
    3. 计算总题数
    4. 将难度比例转换为具体题目数量分配

    对外通过 property 提供结构化访问接口。
    """

    def __init__(self, config_path="config.yaml"):
        """
        初始化配置对象。

        功能：
        - 读取 YAML 配置文件
        - 校验题型数量合法性
        - 计算题目总数
        - 解析难度分布并进行比例归一化与整数分配

        :param config_path: 配置文件路径（默认当前目录下 config.yaml）
        :raises ConfigError: 当题型数量或难度比例不合法时抛出
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            print("[Config] 正在加载配置文件...")
            self.data = yaml.safe_load(f)

            try:
                print("[Config] 解析题目类型题数...")
                for qtype, num in self.type_limits.items():
                    print(f"         {qtype}类型总题数： {num} 题")

                # 计算题目总数
                total_questions = sum(
                    int(self.data["question_types"][i]["count"])
                    for i in range(len(self.data["question_types"]))
                )
                self.data["meta"] = {
                    "total_questions": total_questions
                }

                print("[Config] 解析题目难度分布...")
                for diff, num in self.bucket_constraints.items():
                    print(f"         {diff}⭐难度的总题数： {num} 题")

                print(f"[Config] 加载成功，配置文件总览：{self.data}")

            except InvalidConstraintError as e:
                print(f"[Config] 解析难度时发生错误 : {e}，请检查输入")
                raise ConfigError
            except InvalidQuestionTypeNumber as e:
                print(f"[Config] 解析难度时发生错误 : {e}，请检查输入")
                raise ConfigError

    @property
    def type_limits(self):
        """
        获取各题型数量限制。

        功能：
        - 校验每种题型的数量必须为非负整数
        - 将 YAML 中的结构转换为 {题型名称: 题目数量} 的字典

        :return: dict[str, int] 题型到数量的映射
        :raises InvalidQuestionTypeNumber: 若数量为负或非整数
        """
        for qtype in self.data["question_types"]:
            if qtype["count"] < 0 or int(qtype["count"]) - qtype["count"] != 0:
                raise InvalidQuestionTypeNumber("输入的题目数量不规范，因为不是正整数")

        return {t["name"]: int(t["count"]) for t in self.data["question_types"]}

    @property
    def difficulty_target(self):
        """
        获取目标平均难度。

        功能：
        - 从配置中读取目标难度
        - 限制在 1~6 区间
        - 转为整数

        :return: int 目标平均难度（1~6）
        """
        return max(1, min(6, int(self.data["difficulty"]["target_average"])))

    @property
    def total_questions(self):
        """
        获取总题数。

        功能：
        - 返回初始化阶段计算并存入 meta 中的题目总数

        :return: int 总题数
        """
        return self.data["meta"]["total_questions"]

    @property
    def bucket_constraints(self):
        """
        根据难度比例生成各难度档的题目数量分配。

        算法流程：
        1. 校验比例非负
        2. 若比例总和不为 1，则进行归一化
        3. 使用最大余数法进行整数分配：
           - 先对比例 × 总题数向下取整
           - 再按余数大小补齐差额

        :return: dict[str, int] 各难度档对应的题目数量
        :raises InvalidConstraintError: 若比例非法或总和为 0
        """
        constraints = self.data["difficulty"]["bucket_constraints"]
        total_number = int(self.total_questions)

        proportions = {}
        for star, p in constraints.items():
            val = float(p)
            if val < 0:
                raise InvalidConstraintError(f"难度系数分配不能为负数: {star}={val}")
            proportions[star] = val

        total_proportion = sum(proportions.values())

        if total_proportion <= 0:
            raise InvalidConstraintError("所有难度系数之和必须大于0，请检查配置文件。")

        # 若比例总和不为1则归一化
        if abs(total_proportion - 1.0) > 1e-6:
            for star in proportions:
                proportions[star] = proportions[star] / total_proportion

        distribution = {}
        remaining = {}

        for star_name, proportion in proportions.items():
            exact_value = proportion * total_number
            distribution[star_name] = int(floor(exact_value))
            remaining[star_name] = exact_value - distribution[star_name]

        diff = total_number - sum(distribution.values())
        stars_sorted_by_remainder = sorted(remaining, key=remaining.get, reverse=True)

        for i in range(diff):
            target_star = stars_sorted_by_remainder[i]
            distribution[target_star] += 1

        return distribution

    @property
    def dataset_path(self):
        return self.data["data"]["paths"]

    @property
    def max_per_type(self):
        return self.data["data"]["max_per_type"]

if __name__ == "__main__":
    config = Config()
    print(config.dataset_path)
