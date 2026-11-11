# IDMC Mastery Roadmap --- Module 2

## Mapping Fundamentals: Sources, Transformations, Ports, Targets, Validation, and Execution

**Level:** Beginner\
**Prerequisite:** Module 1 --- IDMC Architecture and Fundamentals

=> ALWAYS DISABLE LOOKUP CACHE ENABLED BUTTON -> IN ADVANCE SECTION OF LOOKUP.....
------------------------------------------------------------------------

## 1. Module objectives

By the end of this module, you should be able to: - Explain what a
mapping does. - Create a mapping from source to target. - Configure
source and target objects. - Understand transformation ports and field
links. - Explain how metadata and datatypes affect a mapping. - Validate
and save a mapping. - Configure and run a mapping task. - Monitor a run
and verify the output. - Troubleshoot common mapping failures.

------------------------------------------------------------------------

## 2. What is a mapping?

A mapping is the design of a data flow. It defines: 1. Where the data
comes from. 2. Which transformations process it. 3. How data flows
between components. 4. Where the output goes.

A simple mapping:

``` text
SOURCE → EXPRESSION → TARGET
```

Example: read employee records from Oracle, calculate annual salary, and
write the records to Snowflake.

A mapping is a design object. Saving it does not by itself guarantee
that data has been processed.

------------------------------------------------------------------------

## 3. Source configuration

A source identifies the object from which the mapping reads data.

Typical source configuration includes: - Connection. - Source type and
object. - Selected fields. - Source filters or query options, where
supported. - Runtime-related settings supported by the connector.

### Source configuration checklist

1.  Select the correct connection.
2.  Choose the source object.
3.  Confirm the expected fields appear.
4.  Preview the source data if preview is available.
5.  Check datatypes and NULLs.
6.  Confirm that the source contains the expected rows.

Example source: `EMPLOYEE_MASTER(EMP_ID, EMP_NAME, SALARY, DEPT_ID)`

Do not confuse the source object's displayed metadata with proof that
the mapping will run successfully. Runtime connectivity and permissions
still matter.

------------------------------------------------------------------------

## 4. Target configuration

A target identifies where output records are written.

Typical target configuration includes: - Target connection. - Target
object or creation mode. - Target fields and mapping. - Write operation
or load behavior supported by the connector. - Matching keys for
update/upsert behavior, where applicable. - Error and reject behavior
supported by the task and connector.

### Target configuration checklist

1.  Select the intended target connection.
2.  Select an existing target or configure creation if supported.
3.  Verify the target schema and column names.
4.  Map each required output field to the correct target field.
5.  Check datatypes, precision, and scale.
6.  Configure the intended write operation.
7.  Verify permissions to create or write to the target.

**Important:** Runtime target creation is not available in exactly the
same way for every connector or target type. Confirm the options shown
by the actual IDMC target configuration. If the requirement is to create
a table at runtime, verify that the connector and task support the
required dynamic target behavior.

------------------------------------------------------------------------

## 5. Transformation ports

Ports are the fields that enter or leave a transformation.

Common port roles include: - **Input:** Receives a value from an
upstream component. - **Output:** Sends a value to a downstream
component. - **Input/Output:** Receives a value and makes it available
after processing, where supported. - **Variable:** Holds an intermediate
value within a transformation, where supported.

Exact port types and behavior depend on the transformation.

Example:

``` text
SOURCE.SALARY
      |
      v
EXPRESSION
  IN_SALARY
  OUT_ANNUAL_SALARY = IN_SALARY * 12
      |
      v
TARGET.ANNUAL_SALARY
```

The input port receives the salary. The output port provides the derived
annual salary.

### Port naming

Use meaningful names such as: - `IN_SALARY` - `OUT_ANNUAL_SALARY` -
`RECORD_ACTION` - `LKP_PRODUCT_ID`

Naming conventions are not mandatory syntax, but consistent names make
complex mappings easier to debug.

------------------------------------------------------------------------

## 6. Field mapping and links

A field link connects an output port to an input port or target field.

Example:

``` text
SOURCE.EMP_ID   ──────────> TARGET.EMP_ID
SOURCE.EMP_NAME ──────────> TARGET.EMP_NAME
```

If an Expression derives `ANNUAL_SALARY`, map its output port to the
target's `ANNUAL_SALARY` field.

Common mistakes: - Mapping a source field to the wrong target column. -
Forgetting to map a required target field. - Connecting incompatible
datatypes. - Using the wrong output port. - Assuming similarly named
fields are automatically semantically equivalent. - Renaming a port
without updating downstream references.

Always check the field mappings after changing source or target
metadata.

------------------------------------------------------------------------

## 7. Metadata and datatypes

Metadata describes the structure of data, including: - Field names. -
Datatypes. - Precision and scale. - Nullability or related field
properties when available.

Examples: - `NUMBER(10,0)` --- numeric values with precision 10 and
scale 0. - `NUMBER(10,2)` --- numeric values with up to two decimal
places. - `VARCHAR(100)` --- text up to the configured length. - `DATE`
--- date values. - `TIMESTAMP_NTZ` --- timestamp without timezone
information in Snowflake.

Datatype mismatches can cause validation or runtime failures,
truncation, or unexpected conversions.

### Example

If a source price contains `65000.50`, mapping it to an integer target
field could lose the fractional part or cause a conversion issue
depending on configuration. Use compatible numeric definitions when the
decimal portion matters.

### Metadata changes

If the source or target schema changes, refresh or update metadata as
supported, then verify all downstream transformations and target
mappings.

------------------------------------------------------------------------

## 8. A first practical mapping

### Business requirement

Read employee data from a source and copy selected fields to a target.

Source: `EMPLOYEE_MASTER(EMP_ID, EMP_NAME, SALARY, DEPT_ID)`

Target: `EMPLOYEE_COPY(EMP_ID, EMP_NAME, SALARY, DEPT_ID)`

Mapping:

``` text
EMPLOYEE_MASTER
       |
       v
     TARGET
  EMPLOYEE_COPY
```

### Steps

1.  Open Data Integration.
2.  Create a new Mapping.
3.  Add the source and select the appropriate connection and table.
4.  Confirm the expected source fields.
5.  Add the target and select its connection and table, or configure
    supported target creation.
6.  Connect the source fields to the matching target fields.
7.  Validate the mapping.
8.  Save it with a meaningful name, such as `M_EMPLOYEE_COPY`.
9.  Create a mapping task for the mapping.
10. Choose the correct runtime environment and execution options.
11. Run the task.
12. Monitor the job.
13. Query the target to verify the result.

The exact screen layout and available settings can vary by IDMC version
and connector.

------------------------------------------------------------------------

## 9. Validation, execution, and data verification

These are separate stages.

### Validation

Checks the mapping design for issues detectable before execution. It
does not prove that source data is correct or that the target will
accept all rows.

### Execution

Runs the configured mapping task in the selected runtime environment.

### Data verification

Confirms that actual output matches the requirement.

Useful checks: - Compare source and target row counts. - Check a few
known keys. - Compare column values. - Check duplicates. - Check
rejected or failed rows. - Verify NULLs and datatype conversions.

Example SQL checks:

``` sql
SELECT COUNT(*) FROM EMPLOYEE_MASTER;
SELECT COUNT(*) FROM EMPLOYEE_COPY;
```

The counts should match for a simple one-to-one copy with no filtering,
rejected rows, or duplicate-expanding transformations. If they do not
match, inspect the mapping and job details rather than assuming the
counts must always match.

------------------------------------------------------------------------

## 10. Mapping tasks and execution settings

A mapping task configures how a mapping runs. Depending on the task and
environment, it may specify: - The mapping. - Runtime environment. -
Parameter values. - Source or target overrides. - Other connector- and
task-supported execution settings.

Before running: - Verify the selected mapping. - Verify the runtime. -
Check parameter values. - Confirm source and target configuration. -
Ensure the connection credentials and permissions are valid.

Run the task and then inspect the Monitor or job details.

------------------------------------------------------------------------

## 11. Common errors and debugging

### Mapping is invalid

Possible causes: - Missing required transformation ports. - Invalid
expression. - Incompatible datatypes. - Unconnected required
components. - Missing target mappings. - Incorrect transformation
configuration.

Approach: open the validation details and fix the reported component
first.

### Mapping validates but task fails

Possible causes: - Connection or authentication failure. - Secure
Agent/runtime unavailable. - Network or DNS issue. - Missing database
permissions. - Source or target object missing. - Target constraint
violation. - Datatype conversion failure.

Approach: inspect the job error and logs, then isolate the failing
stage.

### Mapping succeeds but output is wrong

Possible causes: - Wrong field mapping. - Incorrect business
condition. - Incorrect Lookup condition. - Unexpected NULL handling. -
Source duplicates. - Target operation not configured as intended.

Approach: preview intermediate outputs where available, inspect row
counts, and validate target values.

### Rows are missing

Check: - Source filter/query options. - Filter transformation
conditions. - Router group conditions. - Lookup match behavior. -
Reject/error details. - Target write behavior.

### Duplicate rows appear

Check: - Duplicate source keys. - Lookup returning multiple matches. -
Joiner conditions. - Repeated task execution against an append target. -
Missing target key or idempotency logic.

------------------------------------------------------------------------

## 12. Best practices

-   Use meaningful mapping and port names.
-   Preview source data before designing complex logic.
-   Confirm source and target metadata.
-   Validate after significant changes.
-   Keep mapping logic readable.
-   Check actual job errors before editing configuration.
-   Verify output data with SQL or a target preview.
-   Test unmatched records, NULLs, duplicates, and reruns.
-   Do not assume target creation, upsert, or connector behavior is
    identical across all target types.
-   Keep development/test targets separate from important production
    data.

------------------------------------------------------------------------

## 13. Interview questions and model answers

### Q1. What is a mapping?

A mapping defines the source-to-target data flow and the transformations
applied along the way.

### Q2. What is the difference between a source and a target?

A source provides input records; a target receives the mapping output.

### Q3. What are ports?

Ports are fields used to pass data into and out of transformations. The
available port roles depend on the transformation.

### Q4. What is field mapping?

Field mapping connects the correct output field to the intended input or
target field.

### Q5. What is metadata?

Metadata describes data structure, including field names, datatypes, and
numeric precision and scale.

### Q6. Does a valid mapping guarantee a successful run?

No. Runtime connectivity, permissions, source/target availability,
constraints, and data conversion can still cause failure.

### Q7. Does a successful run guarantee correct data?

No. Business logic or field mapping can be incorrect even when the job
succeeds. Verify the output.

### Q8. Why might source and target row counts differ?

Filtering, rejected rows, duplicate behavior, lookup or join logic, and
target write behavior can change the number of output records.

### Q9. What do you do when a mapping fails?

Inspect validation or job details, identify the failing component, check
connectivity and metadata, correct the root cause, and rerun a
controlled test.

### Q10. Why use a mapping task?

It configures the execution of a mapping, including runtime and other
supported run settings.

------------------------------------------------------------------------

## 14. Practical checklist

-   [ ] Create a mapping.
-   [ ] Configure a source connection and object.
-   [ ] Preview source fields and records.
-   [ ] Add a target.
-   [ ] Connect fields correctly.
-   [ ] Explain input and output ports.
-   [ ] Explain metadata and datatype compatibility.
-   [ ] Validate and save the mapping.
-   [ ] Create and run a mapping task.
-   [ ] Find the job status and error details.
-   [ ] Verify target row counts and values.
-   [ ] Explain the difference between validation, execution, and data
    verification.

## 15. Key takeaway

**Source → Transformations → Target** defines the data flow.

**Mapping → Mapping task → Run → Monitor → Verify output** defines the
basic development and execution lifecycle.

In Module 3, we will focus on data-flow fundamentals: active versus
passive transformations, connected versus unconnected transformations,
transformation ordering, and row-level versus aggregate processing.



Update Strategy Transformation in Informatica PowerCenter
In PowerCenter, the Update Strategy transformation is a special transformation that lets you define how target rows are updated — insert, update, or delete — based on matching criteria, without writing custom SQL or code.

What it is
The Update Strategy transformation is part of the Active Transformations in PowerCenter. It is designed to apply update rules to target data by comparing incoming source data with existing target data, and then performing the appropriate action (insert, update, or delete) according to the rules you define 
Informatica
Informatica
+1
.

It is often used for:

Uploading data into a target table while preserving existing records.

Merging data from multiple sources into a single target.

Conditional updates based on key fields or expressions.

How it works
Input ports – You define one or more input ports (source data) and optional target ports (existing data).

Update rules – You specify conditions for:

Insert: Add new rows when no match is found.

Update: Modify existing rows when a match is found.

Delete: Remove rows when a match is found but the target should no longer exist.

Key fields – One or more key fields (or expressions) are used to match source and target rows.

Execution – PowerCenter compares each source row with the target, applies the rules, and writes the result to the target table.

Configuration steps (PowerCenter 10.5) 
Informatica
Informatica
+1
Create the transformation

In the Developer Client, drag the Update Strategy transformation from the Active Transformations folder into your mapping.

Add input ports

Connect your source mapping to the transformation’s input ports.

Set update rules

In the transformation’s properties, define:

Key fields (primary key or unique identifier).

Update condition (e.g., “Update if key matches and column value differs”).

Insert condition (e.g., “Insert if no match”).

Delete condition (optional).

Test the mapping

Run a session to verify that updates and inserts occur as expected.

Optimize

Use indexes on key fields in the target table for better performance.

Consider using the Target Table property to specify the target table name.

Best practices 
Informatica
Informatica
+1
Use unique keys for matching to avoid ambiguous updates.

Test with sample data before running on production.

Combine with other transformations (e.g., Filter, Sort) to pre-process data.

Monitor performance — large datasets may require partitioning or parallel execution.

Example use case
If you have a target table Sales with columns CustomerID, ProductID, Quantity, and you want to:

Insert new CustomerID–ProductID combinations.

Update Quantity if the combination exists.

Delete rows where Quantity is negative.

You can configure the Update Strategy transformation with:

Key fields: CustomerID, ProductID.

Update rule: If Quantity differs, update.

Insert rule: If no match, insert.

Delete rule: If Quantity < 0, delete.


Update Strategy Transformation in Informatica PowerCenter
In PowerCenter, the Update Strategy transformation is a special transformation that lets you define how target rows are updated — insert, update, or delete — based on matching criteria, without writing custom SQL or code.

What it is
The Update Strategy transformation is part of the Active Transformations in PowerCenter. It is designed to apply update rules to target data by comparing incoming source data
with existing target data, and then performing the appropriate action (insert, update, or delete) according to the rules you define 

It is often used for:
Uploading data into a target table while preserving existing records.
Merging data from multiple sources into a single target.
Conditional updates based on key fields or expressions.

How it works
Input ports – You define one or more input ports (source data) and optional target ports (existing data).

Update rules – You specify conditions for:
Insert: Add new rows when no match is found.
Update: Modify existing rows when a match is found.
Delete: Remove rows when a match is found but the target should no longer exist.

Key fields – One or more key fields (or expressions) are used to match source and target rows.

Execution – PowerCenter compares each source row with the target, applies the rules, and writes the result to the target table.

Configuration steps (PowerCenter 10.5) 

- Create the transformation

In the Developer Client, drag the Update Strategy transformation from the Active Transformations folder into your mapping.

- Add input ports

Connect your source mapping to the transformation’s input ports.

- Set update rules

In the transformation’s properties, define:
Key fields (primary key or unique identifier).
Update condition (e.g., “Update if key matches and column value differs”).
Insert condition (e.g., “Insert if no match”).
Delete condition (optional).
Test the mapping
Run a session to verify that updates and inserts occur as expected.
Optimize
Use indexes on key fields in the target table for better performance.
Consider using the Target Table property to specify the target table name.

Best practices 
Use unique keys for matching to avoid ambiguous updates.
Test with sample data before running on production.
Combine with other transformations (e.g., Filter, Sort) to pre-process data.
Monitor performance — large datasets may require partitioning or parallel execution.

Example use case
If you have a target table Sales with columns CustomerID, ProductID, Quantity, and you want to:

Insert new CustomerID–ProductID combinations.
Update Quantity if the combination exists.
Delete rows where Quantity is negative.

You can configure the Update Strategy transformation with:
Key fields: CustomerID, ProductID.
Update rule: If Quantity differs, update.
Insert rule: If no match, insert.
Delete rule: If Quantity < 0, delete.

In short: The Update Strategy transformation is a powerful, rule-based way to manage insert/update/delete logic in PowerCenter 
without writing custom SQL, making it ideal for merge and upsert scenarios
