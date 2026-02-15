from datetime import datetime
import numpy as np
import pandas as pd


class ExecutionEngine:

    def __init__(self):
        self.audit_log = []

    # ==========================================================
    # SCHEMA FIX
    # ==========================================================
    def apply_schema_fix(self, df, plan):

        for col, info in plan.items():

            if col not in df.columns:
                continue

            if not isinstance(info, dict):
                continue

            action = info.get("action", "").lower()

            # Save original values for comparison
            original_values = df[col].copy()

            # ---------------- NUMERIC ----------------
            if action == "convert_to_numeric":

                cleaned = (
                    df[col].astype(str)
                    .str.replace(r"[₹$]", "", regex=True)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df[col] = pd.to_numeric(cleaned, errors="coerce")

            # ---------------- DATE ----------------
            elif action == "convert_to_date":

                # Save original
                original_values = df[col].copy()

                # Step 1: Clean obvious junk
                cleaned = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r"[^\w\s:/\-.,]", "", regex=True)
                    .str.replace(r"\s+", " ", regex=True)
                )

                # Step 2: First attempt – automatic inference (very powerful)
                parsed = pd.to_datetime(
                    cleaned,
                    errors="coerce",
                    infer_datetime_format=True,
                    dayfirst=False
                )

                # Step 3: If still NaT, try common fallback formats
                if parsed.isna().any():

                    fallback_formats = [
                        "%m/%d/%Y",
                        "%d/%m/%Y",
                        "%m-%d-%Y",
                        "%d-%m-%Y",
                        "%B %d, %Y",
                        "%b %d, %Y",
                        "%d-%b-%y",
                        "%d-%b-%Y",
                        "%d-%B-%Y",
                        "%d-%B-%y",
                        "%d %b %Y",
                        "%d %B %Y",
                        "%Y-%m-%d",
                        "%Y/%m/%d"
                    ]

                    for fmt in fallback_formats:
                        mask = parsed.isna()
                        try:
                            parsed.loc[mask] = pd.to_datetime(
                                cleaned.loc[mask],
                                format=fmt,
                                errors="coerce"
                            )
                        except:
                            continue

                # Step 4: Assign parsed datetime
                df[col] = parsed

                # Step 5: Flag invalid dates
                df[col + "_invalid_flag"] = df[col].isna()

                # Step 6: Count rows changed
                changed_mask = (
                    original_values.astype(str).str.strip() !=
                    df[col].astype(str)
                )

                rows_changed = int(changed_mask.sum())

                self.audit_log.append({
                    "timestamp": str(datetime.now()),
                    "column": col,
                    "schema_action": action,
                    "rows_changed": rows_changed,
                    "invalid_dates": int(df[col].isna().sum())
                })

                continue


            # ---------------- BOOLEAN ----------------
            elif action == "convert_to_boolean":

                df[col] = df[col].astype(str).str.lower().map(
                    {
                        "yes": True,
                        "no": False,
                        "true": True,
                        "false": False,
                        "1": True,
                        "0": False
                    }
                )

            # ---------------- STATE FULL NAME ----------------
            elif action == "convert_to_full_state_name":

                cleaned = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .str.replace(r"[^A-Z]", "", regex=True)
                )

                cleaned.loc[
                    cleaned.isin(["NAN", "NONE", "NULL", ""])
                ] = np.nan

                state_map = {
                    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
                    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
                    "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
                    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
                    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
                    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
                    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
                    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
                    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
                    "NH": "New Hampshire", "NJ": "New Jersey",
                    "NM": "New Mexico", "NY": "New York",
                    "NC": "North Carolina", "ND": "North Dakota",
                    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
                    "PA": "Pennsylvania", "RI": "Rhode Island",
                    "SC": "South Carolina", "SD": "South Dakota",
                    "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
                    "VT": "Vermont", "VA": "Virginia",
                    "WA": "Washington", "WV": "West Virginia",
                    "WI": "Wisconsin", "WY": "Wyoming"
                }

                df[col] = cleaned.map(state_map)
                df[col + "_invalid_flag"] = df[col].isna()

            else:
                # leave_as_is or unknown action
                pass

            # -------- Count rows changed --------
            changed_mask = (
                original_values.astype(str).str.strip()
                != df[col].astype(str)
            )

            rows_changed = int(changed_mask.sum())

            self.audit_log.append({
                "timestamp": str(datetime.now()),
                "column": col,
                "schema_action": action,
                "rows_changed": rows_changed
            })

        return df

    # ==========================================================
    # MISSING VALUE HANDLING (Non-Destructive)
    # ==========================================================
    def apply_missing(self, df, plan):

        for col, info in plan.items():

            if col not in df.columns:
                continue

            strategy = ""

            if isinstance(info, dict):
                strategy = info.get("strategy", "")
            elif isinstance(info, str):
                strategy = info

            initial_missing = df[col].isna().sum()

            # Numeric
            if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())

            elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())

            # Categorical
            elif strategy == "mode":

                non_null = df[col].dropna()

                if not non_null.empty:

                    mode_value = non_null.mode()[0]
                    mode_count = (non_null == mode_value).sum()
                    dominance_ratio = mode_count / len(non_null)

                    # Only fill if dominance ≥ 90%
                    if dominance_ratio >= 0.90:
                        df[col] = df[col].fillna(mode_value)
                        imputation_applied = True
                    else:
                        imputation_applied = False
                else:
                    imputation_applied = False


            # Flag
            elif strategy == "flag":
                df[col + "_missing_flag"] = df[col].isna()
                df[col] = df[col].fillna("Missing")

            # Drop blocked
            elif strategy == "drop":
                pass

            remaining_missing = df[col].isna().sum()
            rows_fixed = int(initial_missing - remaining_missing)

            self.audit_log.append({
                "timestamp": str(datetime.now()),
                "column": col,
                "missing_strategy": strategy,
                "initial_missing": int(initial_missing),
                "remaining_missing": int(remaining_missing),
                "rows_fixed": rows_fixed,
                "mode_dominance_ratio": round(dominance_ratio, 3) if strategy == "mode" and not non_null.empty else None,
                "imputation_applied": imputation_applied if strategy == "mode" else None
            })

        return df

    # ==========================================================
    # DUPLICATES (Exact Full-Row Only)
    # ==========================================================
    def apply_duplicates(self, df, plan):

        before = len(df)

        df = df.drop_duplicates(
            subset=df.columns.tolist(),
            keep="first"
        )

        removed = before - len(df)

        self.audit_log.append({
            "timestamp": str(datetime.now()),
            "duplicate_strategy": "exact_match_all_columns_only",
            "rows_removed": int(removed),
            "columns_used": df.columns.tolist()
        })

        return df

    # ==========================================================
    # OUTLIERS (Flag Only, No Removal)
    # ==========================================================
    def apply_outliers(self, df, plan):

        for col, info in plan.items():

            if col not in df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(df[col]):
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            mask = (df[col] < lower) | (df[col] > upper)

            df[col + "_outlier_flag"] = mask

            self.audit_log.append({
                "timestamp": str(datetime.now()),
                "column": col,
                "rows_flagged": int(mask.sum()),
                "method": "IQR_flag_only",
                "lower_bound": float(lower),
                "upper_bound": float(upper)
            })

        return df
