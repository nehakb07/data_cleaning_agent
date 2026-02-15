import json
from app.services.llm_service import GroqService


class LLMPlanner:

    def __init__(self):
        self.llm = GroqService()

    def generate_plan(self, profile):

        system_prompt = """
You are an autonomous Data Quality Agent.

Analyze the dataset profile and perform:

1) Schema & Type Fix Analysis
2) Missing Value Treatment Analysis
3) Duplicate Analysis
4) Outlier Analysis

Return STRICT JSON in this format:

{
  "diagnosis": {
      "schema_issues": {},
      "missing_issues": {},
      "duplicate_issues": {},
      "outlier_issues": {}
  },
  "cleaning_plan": {
      "schema_fixes": {
          "column_name": {
            "action": "convert_to_numeric | convert_to_date | convert_to_boolean | convert_to_full_state_name | leave_as_is",   
              "reason": "..."
          }
      },
      "missing_value_plan": {
          "column_name": {
              "strategy": "mean | median | mode | drop | flag | leave_as_is",
              "reason": "..."
          }
      },
      "duplicate_plan": {
          "strategy": "exact | subset | leave_as_is",
          "keys": [],
          "reason": "..."
      },
      "outlier_plan": {
          "column_name": {
              "action": "cap | flag | leave_as_is",
              "method": "IQR",
              "reason": "..."
          }
      }
  }
}
"""

        user_prompt = json.dumps(profile)

        return self.llm.chat_json(system_prompt, user_prompt)
