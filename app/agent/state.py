from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.vlaue_info import ValueInfo


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list[any]
    description: str
    alias: list[str]

class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]

class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str

class DBInfoState(TypedDict):
    dialect: str #使用的数据库名称 不同数据库语法可能有区别
    version: str



class DataAgentState(TypedDict):
    query: str # 用户输入的查询
    keywords: list[str]

    retrieved_column_infos: list[ColumnInfo] #召回的字段信息
    retrieved_metric_infos: list[MetricInfo] #召回的指标信息
    retrieved_value_infos : list[ValueInfo]  #召回的字段取值信息

    table_infos: list[TableInfoState] # 表信息
    metric_infos: list[MetricInfoState] # 指标信息

    date_info: DateInfoState #日期信息
    db_info: DBInfoState # 数据库信息

    sql: str # sql

    error: str # 校验sql时出现的错误信息