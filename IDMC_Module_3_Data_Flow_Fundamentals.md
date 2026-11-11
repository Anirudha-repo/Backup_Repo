# IDMC Mastery Roadmap --- Module 3

## Data Flow Fundamentals: Transformation Types, Row Processing, and Execution Order

**Level:** Beginner to Intermediate\
**Prerequisites:** Modules 1 and 2

------------------------------------------------------------------------

## 1. Learning objectives

By the end of this module, you should be able to: - Explain how records
flow through an IDMC mapping. - Distinguish active and passive
transformations. - Distinguish connected and unconnected
transformations. - Understand row-level versus group-level processing. -
Choose a suitable transformation for a requirement. - Understand
transformation order and why it matters. - Debug unexpected row counts
and data-flow behavior.

> **Version note:** Transformation behavior and options can vary by IDMC
> release, mapping mode, connector, and runtime. Use the properties
> visible in your environment as the final authority.

------------------------------------------------------------------------

## 2. The core idea: transformations process data

A transformation is a component in a mapping that performs a defined
operation on incoming data.

Examples: - Expression calculates or derives fields. - Filter passes
only records meeting a condition. - Router sends records into configured
groups. - Lookup retrieves reference data. - Aggregator calculates
group-level results. - Sorter sorts records according to configured
keys. - Joiner combines data from two pipelines. - Rank selects top or
bottom records according to configured criteria.

A mapping is a pipeline of these components:

``` text
SOURCE → TRANSFORMATION A → TRANSFORMATION B → TARGET
```

Each component can affect field values, row counts, or the structure of
the output.

------------------------------------------------------------------------

## 3. Active versus passive transformations

This classification concerns whether a transformation can change the
number of rows passing through it.

### Passive transformation

A passive transformation does not change the number of input rows under
its normal operation. It can still change field values or add derived
fields.

Typical examples: - Expression - Sequence Generator (generates sequence
values but normally preserves row count)

### Active transformation

An active transformation can change the number of rows, such as by
filtering rows, combining rows, or producing a group-level result.

Typical examples: - Filter: can remove rows. - Router: can send rows to
different groups; a row may qualify for more than one group depending on
conditions and configuration. - Aggregator: can reduce many input rows
to fewer group-level rows. - Joiner: can change row counts depending on
join type and match cardinality. - Rank: can return a subset of rows
according to its configuration. - Union: combines input pipelines and
changes the total output count relative to each individual input.

### Important nuance

Do not memorize the classification from another Informatica product and
assume every label or behavior is identical in every IDMC mapping mode.
For interviews, explain the concept and verify the exact transformation
classification in the product version being discussed.

### Quick comparison

  ------------------------------------------------------------------------
  Transformation          Common classification    Why
  ----------------------- ------------------------ -----------------------
  Expression              Passive                  Derives values without
                                                   normally changing row
                                                   count

  Filter                  Active                   Removes rows that fail
                                                   the condition

  Router                  Active                   Routes rows into output
                                                   groups

  Aggregator              Active                   Can collapse rows into
                                                   group results

  Joiner                  Active                   Joins can change row
                                                   counts

  Rank                    Active                   Can limit output to
                                                   ranked rows

  Sorter                  Commonly treated as      Orders rows; normally
                          passive in classic       does not remove them
                          Informatica              
                          classifications, but     
                          verify IDMC-specific     
                          documentation/settings   

  Sequence Generator      Passive                  Adds sequence values
                                                   while preserving row
                                                   count

  Lookup                  Depends on product       Match behavior and
                          terminology and          configuration are the
                          implementation; it is    important points
                          commonly treated as a    
                          lookup/enrichment        
                          transformation rather    
                          than relying on this     
                          label alone              
  ------------------------------------------------------------------------

The safest operational habit is to understand each transformation's
behavior rather than relying only on the active/passive label.

------------------------------------------------------------------------

## 4. Connected versus unconnected transformations

This is a different classification from active versus passive.

### Connected transformation

A connected transformation is connected into the main mapping data flow.
Records flow through its ports via links.

Example:

``` text
SOURCE → EXPRESSION → ROUTER → TARGET
```

The Expression receives records through connected links and sends
outputs to the next component.

Common connected transformations include Expression, Filter, Router,
Aggregator, Joiner, Sorter, Rank, Union, and connected Lookup.

### Unconnected transformation

An unconnected transformation is not directly placed in the main
pipeline. It is invoked from another transformation using a supported
call mechanism.

The classic example is an **unconnected Lookup**, which is called from
an Expression using a `:LKP` expression.

Conceptually:

``` text
SOURCE → EXPRESSION ─────────────→ TARGET
             |
             └── :LKP(LKP_NAME, lookup_argument)
                       |
                       v
                UNCONNECTED LOOKUP
```

The diagram is conceptual: the unconnected Lookup is called by an
expression rather than receiving the main pipeline through normal links.

### Why use an unconnected Lookup?

-   To perform a lookup only when required by the expression.
-   To keep lookup logic reusable or separate from the main data flow
    where appropriate.
-   To retrieve a particular return value using a supported lookup call.

### Trade-offs

-   The lookup call syntax and port requirements must be correct.
-   Repeated calls can have performance implications depending on
    caching and runtime behavior.
-   It may be harder to inspect than a connected Lookup.
-   A connected Lookup is often clearer when the mapping needs several
    lookup output fields or when lookup behavior is central to the
    pipeline.

Exact unconnected Lookup support and syntax should be checked against
the transformation options available in your IDMC environment.

------------------------------------------------------------------------

## 5. Row-level versus group-level processing

### Row-level processing

Processes each record individually.

Examples: - Expression: calculate tax for each transaction. - Filter:
decide whether each record passes. - Lookup: retrieve reference values
for each incoming record. - Router: evaluate each record against group
conditions. - Sequence Generator: assign sequence values to incoming
records.

Example:

``` text
IIF(SALARY >= 5000, 'HIGH', 'STANDARD')
```

This classifies each employee row independently.

### Group-level processing

Processes records as groups, usually using one or more grouping keys.

Example: an Aggregator groups transactions by department and calculates
total salary.

Input:

    DEPT_ID   SALARY
  --------- --------
         10     3000
         10     4000
         20     5000

Group by `DEPT_ID`, calculate `SUM(SALARY)`:

    DEPT_ID   TOTAL_SALARY
  --------- --------------
         10           7000
         20           5000

Three input rows became two output rows. This is a common example of a
transformation changing row count.

------------------------------------------------------------------------

## 6. Transformation ordering and why it matters

Transformations are not interchangeable. Their order changes both
performance and results.

### Example A: Filter before Aggregator

Requirement: total salary by department for employees earning at least
5,000.

``` text
SOURCE → FILTER(SALARY >= 5000) → AGGREGATOR → TARGET
```

Only eligible employees contribute to the total.

### Example B: Aggregator before Filter

``` text
SOURCE → AGGREGATOR → FILTER(TOTAL_SALARY >= 5000) → TARGET
```

This calculates totals first and then keeps departments whose total is
at least 5,000. It is a different business rule.

### Filter versus Router

-   Filter removes rows that do not meet its condition from its output.
-   Router directs rows to configured groups. Depending on group
    conditions and configuration, a row can qualify for multiple groups.
    Use mutually exclusive conditions if each row must go to only one
    group.

### Lookup placement

Place a Lookup before an Expression or Router when those components need
lookup output fields. If the lookup result is not needed for a record,
consider whether the lookup can be avoided, provided the design still
meets the requirement.

------------------------------------------------------------------------

## 7. Choose a transformation based on the requirement

  -------------------------------------------------------------------------
  Requirement             Likely transformation   Reason
  ----------------------- ----------------------- -------------------------
  Calculate a new column  Expression              Derives values

  Keep only qualifying    Filter                  Removes nonqualifying
  rows                                            rows

  Split records into      Router                  Sends records into groups
  categories                                      

  Enrich records with     Lookup                  Retrieves reference
  reference attributes                            values

  Combine rows from two   Union                   Combines pipeline outputs
  compatible pipelines                            

  Join two sources based  Joiner or supported     Combines related data
  on a condition          source-side join        

  Calculate               Aggregator              Group-level calculations
  totals/averages by key                          

  Sort records by one or  Sorter                  Establishes configured
  more keys                                       order

  Select top/bottom       Rank                    Ranking-based selection
  records                                         

  Generate sequence       Sequence Generator      Produces sequence values
  values                                          

  Remove duplicate rows   Sorter +                Exact approach depends on
  based on configured     Expression/Rank or      the requirement
  keys/logic              another supported       
                          deduplication design    

  Compare incoming rows   Lookup plus conditional Enables
  with existing target    logic, or supported     insert/update/no-change
  records                 target upsert/merge     decisions
                          pattern                 
  -------------------------------------------------------------------------

A transformation should be selected because of the requirement, not
because it is familiar.

------------------------------------------------------------------------

## 8. Practical scenarios

### Scenario 1: Salary classification

Requirement: mark employees earning at least 5,000 as HIGH.

Use Expression:

``` text
IIF(SALARY >= 5000, 'HIGH', 'STANDARD')
```

This changes a field value, not the number of rows.

### Scenario 2: Keep completed orders only

Use Filter:

``` text
ORDER_STATUS = 'Completed'
```

Rows with other statuses do not pass through the Filter output.

### Scenario 3: Separate insert and update candidates

Use an Expression to calculate `RECORD_ACTION`, then Router groups: -
`RECORD_ACTION = 'INSERT'` - `RECORD_ACTION = 'UPDATE'` - Optional
`RECORD_ACTION = 'NO_CHANGE'`

Ensure the action expression correctly handles missing lookup matches,
NULLs, and comparison of all relevant target columns.

### Scenario 4: Department salary totals

Use Aggregator grouped by `DEPT_ID`, with `SUM(SALARY)`.

### Scenario 5: Product enrichment

Use Lookup to retrieve category or price details from a reference table,
then map the lookup outputs to the target.

------------------------------------------------------------------------

## 9. Common misconceptions

1.  **Active/passive and connected/unconnected mean the same thing.**\
    False. Active/passive concerns row-count behavior;
    connected/unconnected concerns how the transformation participates
    in the mapping flow.

2.  **A passive transformation can never change data.**\
    False. Expression can derive or change field values while preserving
    the number of rows.

3.  **A Router always sends each row to exactly one group.**\
    Not necessarily. Group conditions can overlap; configure conditions
    carefully.

4.  **A Lookup always returns exactly one row.**\
    Not necessarily. Duplicate matches and lookup configuration matter.

5.  **Changing transformation order is harmless.**\
    False. Filter before aggregation can produce a different result from
    filtering after aggregation.

6.  **If the mapping succeeds, its logic must be correct.**\
    False. Verify the output against the requirement.

------------------------------------------------------------------------

## 10. Troubleshooting row counts

Track expected row counts at important points:

``` text
Source rows:             1000
After Filter:             600
After Lookup:             600 (if row-preserving match behavior)
After Aggregator:          25 (one row per group)
Target rows written:      600 or 25, depending on the pipeline
```

These are illustrative numbers, not a guaranteed behavior for every
Lookup or connector.

If counts differ unexpectedly, inspect: - Filter conditions. - Router
group overlap. - Lookup match and multiple-match behavior. - Join type
and key cardinality. - Aggregator group-by ports. - Rank
configuration. - Union input counts. - Target reject behavior and write
settings.

------------------------------------------------------------------------

## 11. Interview questions and model answers

### Q1. What is an active transformation?

A transformation that can change the number of rows flowing through it,
for example Filter or Aggregator.

### Q2. What is a passive transformation?

A transformation that normally preserves row count while potentially
changing field values, such as Expression.

### Q3. Active/passive versus connected/unconnected?

Active/passive describes row-count behavior; connected/unconnected
describes how a transformation participates in the mapping flow.

### Q4. What is a connected Lookup?

A Lookup connected directly into the main mapping data flow, with its
ports linked to upstream/downstream components.

### Q5. What is an unconnected Lookup?

A Lookup invoked through a supported expression call rather than placed
directly in the main data flow.

### Q6. Why can Aggregator reduce row count?

Because it can return one result per group instead of one output per
input record.

### Q7. Filter versus Router?

Filter passes qualifying rows through one output. Router directs rows to
configured groups, which can have overlapping conditions.

### Q8. Why does transformation order matter?

Because later transformations operate on the output of earlier ones, so
changing order can change the business result.

### Q9. How do you investigate unexpected row counts?

Check filters, router conditions, lookup cardinality, joins, aggregation
groups, rank settings, unions, and target rejects.

### Q10. How do you choose a transformation?

Start with the business requirement, identify whether it changes field
values, filters rows, groups rows, enriches data, joins streams, sorts,
ranks, or routes records, and select the component designed for that
operation.

------------------------------------------------------------------------

## 12. Practical exercises

Try to identify the transformation without looking at the answer.

1.  Calculate `NET_AMOUNT = QUANTITY * UNIT_PRICE`.\
    **Answer:** Expression.

2.  Retain only orders with `STATUS = 'Completed'`.\
    **Answer:** Filter.

3.  Send employees into separate groups based on department.\
    **Answer:** Router.

4.  Retrieve a department name using `DEPT_ID`.\
    **Answer:** Lookup.

5.  Calculate total sales by region.\
    **Answer:** Aggregator.

6.  Combine two compatible sales feeds into one stream.\
    **Answer:** Union.

7.  Join customers to orders based on `CUSTOMER_ID`.\
    **Answer:** Joiner or a supported source-side join.

8.  Keep the top five products by revenue.\
    **Answer:** Rank, configured for the required ranking behavior.

9.  Assign generated sequence values.\
    **Answer:** Sequence Generator.

10. Identify new products versus changed existing products.\
    **Answer:** Lookup plus Expression/Router logic, or a supported
    target upsert/merge pattern.

------------------------------------------------------------------------

## 13. Module 3 checklist

-   [ ] Explain active versus passive transformations.
-   [ ] Explain connected versus unconnected transformations.
-   [ ] Explain row-level versus group-level processing.
-   [ ] Choose an appropriate transformation for a requirement.
-   [ ] Explain why transformation order matters.
-   [ ] Explain Filter versus Router.
-   [ ] Understand how Lookup behavior can affect row counts.
-   [ ] Explain why Aggregator may reduce row counts.
-   [ ] Troubleshoot unexpected counts.
-   [ ] Answer the interview questions in your own words.

## 14. Key takeaway

Use these questions to guide your choice:

-   **Need to calculate or derive a value?** Expression.
-   **Need to discard rows?** Filter.
-   **Need multiple output groups?** Router.
-   **Need reference data?** Lookup.
-   **Need group-level totals?** Aggregator.
-   **Need to combine or join data streams?** Union or Joiner.
-   **Need ordered records?** Sorter.
-   **Need ranked records?** Rank.

Remember: **active/passive describes row-count behavior;
connected/unconnected describes how the transformation is invoked or
connected.** They are separate classifications.
