# Employee Attendance Analyzer: Simpler Version:

import pandas as pd

class AttendanceAnalyzer:
    
    def create_attendance_df(self, rows):
        df = pd.DataFrame(rows, columns=["EmployeeID", "Department", "Date", "Attendance"])
        return df

    def compute_monthly_attendance_rate(self, df):
        data = df.copy()
        data["Month"] = data["Date"].str[:7]

        # Total days per employee per month
        total = data.groupby(["EmployeeID", "Month"]).size().reset_index(name="Total")

        # Present days only
        present = data[data["Attendance"] == "Present"].groupby(["EmployeeID", "Month"]).size().reset_index(name="Present")

        # Merge both results
        merged = total.merge(present, on=["EmployeeID", "Month"], how="left")
        merged["Present"] = merged["Present"].fillna(0)

        # Calculate rate
        merged["Attendance Rate"] = (merged["Present"] / merged["Total"]) * 100

        return merged[["EmployeeID", "Month", "Attendance Rate"]]

    def add_absence_flag(self, df):
        """
        Adds IsAbsent column: 1 if Absent, else 0.
        """
        data = df.copy()
        data["IsAbsent"] = data["Attendance"].apply(lambda x: 1 if x == "Absent" else 0)
        return data

    def high_absentees(self, df, threshold):
        """
        Returns employees whose Absent count > threshold.
        """
        abs_counts = df[df["Attendance"] == "Absent"].groupby("EmployeeID").size().reset_index(name="Absence Count")
        
        return abs_counts[abs_counts["Absence Count"] > threshold]

    def department_attendance_summary(self, df):
        """
        Returns Present / Absent / Leave count for each department.
        """
        summary = pd.crosstab(df["Department"], df["Attendance"]).reset_index()

        # Ensure all columns exist
        for col in ["Present", "Absent", "Leave"]:
            if col not in summary.columns:
                summary[col] = 0
        
        return summary[["Department", "Present", "Absent", "Leave"]]