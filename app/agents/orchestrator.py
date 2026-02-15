from app.agents.profiler import DataProfiler
from app.agents.planner import LLMPlanner
from app.agents.executor import ExecutionEngine


class LLMDataCleaningAgent:

    def __init__(self):
        self.profiler = DataProfiler()
        self.planner = LLMPlanner()
        self.executor = ExecutionEngine()

    def run(self, df):

        profile = self.profiler.profile(df)

        plan = self.planner.generate_plan(profile)

        cleaning_plan = plan.get("cleaning_plan", {})

        schema_plan = cleaning_plan.get("schema_fixes", {})
        missing_plan = cleaning_plan.get("missing_value_plan", {})
        duplicate_plan = cleaning_plan.get("duplicate_plan", {})
        outlier_plan = cleaning_plan.get("outlier_plan", {})

        df = self.executor.apply_schema_fix(df, schema_plan)
        df = self.executor.apply_missing(df, missing_plan)
        df = self.executor.apply_duplicates(df, duplicate_plan)
        df = self.executor.apply_outliers(df, outlier_plan)

        return df, plan, self.executor.audit_log
