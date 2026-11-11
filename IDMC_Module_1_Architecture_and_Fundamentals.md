# IDMC Mastery Roadmap --- Module 1

## IDMC Architecture and Core Concepts

**Level:** Beginner\
**Goal:** Understand how IDMC components fit together before building
mappings.

## 1. What is IDMC?

Informatica Intelligent Data Management Cloud (IDMC) is a cloud-based
data management platform. This course focuses on **Cloud Data
Integration**, used to design and run pipelines that read source data,
transform it, and write it to targets.

Example: Oracle employee data + S3 sales files → IDMC mapping →
Snowflake reporting tables.

## 2. Cloud Data Integration

Cloud Data Integration lets you create data pipelines using sources,
transformations, and targets. A typical flow is:

``` text
Source → Lookup → Expression → Router → Target
```

A mapping defines the data flow and logic. It does not necessarily
execute merely because it is saved.

## 3. IDMC versus PowerCenter

  -----------------------------------------------------------------------
  Area                    IDMC                    PowerCenter
  ----------------------- ----------------------- -----------------------
  Platform                Cloud-based data        Traditionally deployed
                          management platform     data integration
                                                  platform

  Design                  Web-based interface     PowerCenter client
                                                  tools

  Runtime                 Secure Agent or         PowerCenter Integration
                          supported cloud runtime Service and associated
                                                  infrastructure

  Administration          IDMC organization and   PowerCenter domain and
                          services                repository
                                                  administration
  -----------------------------------------------------------------------

Do not assume that all features, connectors, or runtime options behave
identically across the products.

## 4. Core components

### Administrator

Used to configure and manage environment resources, such as connections,
Secure Agents, runtime environments, users, permissions, and service
settings.

### Data Integration

The main design area for this course. It is used to create and manage
mappings, mapping tasks, and related data integration assets.

### Secure Agent

Software that enables IDMC to communicate with systems and execute
supported integration work in agent-based environments. The exact
execution and data path depends on the connector and runtime
configuration.

**Connection versus Secure Agent:** A connection describes how to access
a system. A Secure Agent provides a runtime that can execute supported
work and reach systems requiring agent-based connectivity.

### Runtime environment

Identifies the environment used to execute a task. In an agent-based
setup, it may reference a Secure Agent group. Confirm the mapping task
uses the correct runtime.

### Connection

Stores configuration and authentication details needed to access a
source or target. Your connections include Oracle, Snowflake, Amazon S3,
and Flat File.

### Source

The object from which a mapping reads data: for example, an Oracle
table, Snowflake table, CSV file, or supported cloud object.

### Target

The destination where a mapping writes data: for example, an Oracle
table, Snowflake table, or supported file destination.

## 5. Main development objects

### Mapping

Defines the source, transformations, connections between components, and
target logic. It answers where data comes from, how it changes, how rows
are routed, and which fields reach the target.

### Mapping task

Configures execution of a mapping. Depending on the task and
environment, settings can include the mapping, runtime environment,
parameter values, and supported source or target overrides.

### Taskflow

Orchestrates tasks and supported steps into a larger process. Taskflows
are excluded from the current assessment practice, so we will run
mapping tasks directly.

### Schedule

Determines when a supported task runs automatically. Schedules are
excluded from our assessment practice; we will run tasks manually.

### Monitor

Used to inspect execution status and diagnostic details, such as
success/failure, start/end times, rows read or written, and available
error messages or logs.

## 6. Mapping lifecycle

1.  Create a mapping.
2.  Configure the source connection and object.
3.  Add and configure transformations.
4.  Configure the target and field mappings.
5.  Validate the mapping.
6.  Save the mapping.
7.  Create/configure a mapping task.
8.  Select the appropriate runtime and run settings.
9.  Run the task.
10. Monitor the job.
11. Validate the target output against expected results.

### Validation versus execution versus correctness

-   **Valid mapping:** Passes design-time validation.
-   **Successful run:** Execution completes successfully.
-   **Correct output:** The resulting data meets the business
    requirement.

A valid mapping can fail at runtime because of connectivity,
permissions, datatype conversion, constraints, or target configuration.
A successful run can still produce incorrect business results if the
logic is wrong.

## 7. Example of record flow

Source:

    EMP_ID EMP_NAME     DEPT_ID
  -------- ---------- ---------
       101 Anil              10
       102 Priya             20

A mapping could read these rows, use a Lookup to retrieve department
details, use an Expression to derive fields, use a Filter or Router to
control row flow, and write the result to a target.

-   **Expression:** Derives or modifies values.
-   **Filter:** Passes rows meeting a condition.
-   **Router:** Directs rows to configured groups.
-   **Lookup:** Retrieves reference data.
-   **Aggregator:** Calculates grouped results.

Each transformation will be studied in its own module.

## 8. Connectivity and troubleshooting

When a mapping fails, inspect the actual job error before changing
configuration.

### Connection checks

-   Correct connection selected?
-   Connection test successful?
-   Credentials and permissions valid?
-   Runtime able to reach the database, file location, or cloud service?

### Secure Agent checks

-   Is the expected runtime available?
-   Is the agent online?
-   Are required services running?
-   Are network, firewall, DNS, or authentication issues present?

### Mapping checks

-   Correct source object and available fields?
-   Correct transformation conditions?
-   Compatible datatypes, precision, and scale?
-   Correct target field mapping?
-   Correct target operation and matching key?

### Runtime checks

-   Did the task run on the intended runtime?
-   What do the job details and logs say?
-   How many rows were read, rejected, and written?
-   Did target constraints or schema cause the failure?

**Troubleshooting rule:** Use the actual error message. Avoid randomly
changing configuration.

## 9. Essential terminology

  -----------------------------------------------------------------------
  Term                                Meaning
  ----------------------------------- -----------------------------------
  IDMC                                Informatica Intelligent Data
                                      Management Cloud

  Cloud Data Integration              IDMC service for designing and
                                      running data integration pipelines

  Secure Agent                        Runtime software for supported
                                      integration work in agent-based
                                      environments

  Runtime environment                 Environment selected to execute a
                                      task

  Connection                          Configuration used to access a
                                      source or target

  Source                              Input data object

  Transformation                      Component that derives, filters,
                                      enriches, aggregates, or routes
                                      data

  Target                              Destination for output data

  Mapping                             Definition of the data flow and
                                      transformation logic

  Mapping task                        Execution configuration used to run
                                      a mapping

  Taskflow                            Orchestration of tasks and
                                      supported process steps

  Validation                          Design-time check of a mapping

  Monitoring                          Inspection of job status and
                                      execution details

  Metadata                            Descriptive information about
                                      objects and fields, such as names
                                      and datatypes

  Runtime error                       Error occurring during execution
                                      rather than design validation
  -----------------------------------------------------------------------

## 10. Interview questions and model answers

### Q1. What is IDMC?

IDMC is Informatica's cloud-based data management platform. Cloud Data
Integration is used to build and run pipelines across supported systems.

### Q2. What is a mapping?

A mapping defines the flow from source through transformations to
target, including the logic applied to data.

### Q3. What is a mapping task?

A mapping task configures execution of a mapping, including runtime and
other supported execution settings.

### Q4. Mapping versus taskflow?

A mapping defines data transformation and flow. A taskflow orchestrates
tasks and supported process steps.

### Q5. What is a Secure Agent?

It is runtime software used by IDMC to communicate with systems and
execute supported integration work in an agent-based environment.

### Q6. Is a connection the same as a Secure Agent?

No. A connection describes how to access a system; the Secure Agent
provides a runtime that can execute supported work and reach systems
requiring agent-based connectivity.

### Q7. Validation versus successful execution?

Validation checks the design. A successful run means execution
completed. Correct output must still be verified against the business
requirement.

### Q8. What do you check when a mapping fails?

Inspect job errors and logs, connections, permissions, runtime
availability, source metadata, expressions, target mapping, datatypes,
and target constraints.

### Q9. Can IDMC integrate Oracle, Snowflake, S3, and flat files?

Yes, when the relevant connectors, permissions, network access, and
runtime configuration are available and correct.

### Q10. Why monitor a mapping task?

Monitoring reveals execution status, processed-row information where
available, errors, and potential bottlenecks.

## 11. Practical checklist

Before moving to Module 2, make sure you can:

-   [ ] Explain IDMC and Cloud Data Integration.
-   [ ] Distinguish Administrator from Data Integration.
-   [ ] Explain the role of a Secure Agent.
-   [ ] Distinguish connection from runtime environment.
-   [ ] Explain source, transformation, and target.
-   [ ] Distinguish mapping, mapping task, and taskflow.
-   [ ] Explain validation versus execution versus correct output.
-   [ ] Find a task's run status and error details.
-   [ ] Describe the lifecycle from mapping creation to output
    validation.

## 12. Key takeaway

**Connect → Design mapping → Configure transformations → Configure
target → Validate → Configure mapping task → Run → Monitor → Validate
output**

For the current assessment, focus on direct mapping-task execution
without taskflows or schedules.
