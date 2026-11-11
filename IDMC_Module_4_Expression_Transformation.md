# Module 4 --- Expression Transformation in Informatica IDMC

> **Goal:** Learn to create row-level business logic in an IDMC mapping,
> especially `IIF`, NULL handling, data-type conversions, and action
> flags used in SCD Type 1 and Type 2 patterns.

## 1. What is an Expression transformation?

An **Expression transformation** evaluates expressions for each incoming
row. It can create new fields, standardize values, calculate metrics,
derive flags, and prepare data for downstream transformations.

Typical uses: - Calculate `NET_AMOUNT = QUANTITY * UNIT_PRICE`. -
Standardize text using trim/upper/lower functions. - Derive a status
such as `ACTIVE`, `INACTIVE`, or `UNKNOWN`. - Replace or handle missing
values. - Build a `RECORD_ACTION` field such as `INSERT`, `UPDATE`,
`NO_CHANGE`, or `EXPIRE`. - Prepare comparison values before a Lookup,
Filter, Router, or target.

An Expression normally does **not** decide which rows are discarded. It
calculates values. Use a **Filter** to remove rows, or a **Router** to
send rows down different paths.

## 2. Where it sits in a mapping

A common flow is:

`Source → Expression → Lookup → Expression → Filter/Router → Target`

Examples: - First Expression: trim source strings, convert types, derive
business keys. - Lookup: find the existing target row. - Second
Expression: compare source values with lookup values and derive
`RECORD_ACTION`. - Filter/Router: route inserts, updates, unchanged
records, and rejects.

You do not need every transformation in every mapping. Add only the
steps required by the business rule.

## 3. Ports: input, output, and variable concepts

Exact port options depend on the transformation editor and mapping mode,
but the concepts are:

-   **Input port:** receives a value from an upstream field.
-   **Output port:** exposes a calculated result to downstream
    transformations.
-   **Input/output port:** passes a value through and may also be used
    in an expression, where supported.
-   **Variable port:** stores an intermediate calculation for use in
    other expressions, where supported.

Example concept:

  Port     Example        Purpose
  -------- -------------- ------------------------------------
  Input    `UNIT_PRICE`   Source price
  Input    `QUANTITY`     Source quantity
  Output   `NET_AMOUNT`   `UNIT_PRICE * QUANTITY`
  Output   `PRICE_BAND`   Text classification based on price

Create a clearly named output field for each calculated value. Check the
output datatype and precision/scale, not only the expression text.

## 4. Expression syntax basics

Expressions use field names, operators, constants, and functions. In the
expression editor, select fields from the available field list when
possible; this helps avoid misspellings and invalid references.

Common operators: - Arithmetic: `+`, `-`, `*`, `/` - Comparison: `=`,
`<>`, `>`, `<`, `>=`, `<=` - Logical: `AND`, `OR`, `NOT` - Grouping:
parentheses `(...)`

Examples:

``` text
QUANTITY * UNIT_PRICE
SALARY + COMMISSION
DEPARTMENT_ID = 10
STATUS = 'ACTIVE'
( DEPARTMENT_ID = 10 OR DEPARTMENT_ID = 20 )
AND SALARY >= 3000
```

Use **single quotes** for string literals:

``` text
'ACTIVE'
'UNKNOWN'
```

Do not confuse a string literal with a field reference. `'STATUS'` is
the literal word STATUS; `STATUS` refers to a field.

### Precedence and parentheses

Even when operator precedence is understood, parentheses make business
logic easier to review and reduce mistakes.

Business rule: department is 10 or 20, and salary is at least 3000:

``` text
( DEPARTMENT_ID = 10 OR DEPARTMENT_ID = 20 )
AND SALARY >= 3000
```

## 5. `IIF` --- the essential conditional function

`IIF` evaluates a condition and returns one value if true and another if
false.

General pattern:

``` text
IIF(condition, value_if_true, value_if_false)
```

Example:

``` text
IIF(SALARY >= 5000, 'HIGH', 'STANDARD')
```

Meaning: - If salary is at least 5000, return `HIGH`. - Otherwise,
return `STANDARD`.

The returned branches should have compatible datatypes. For example, do
not return a number on one branch and an unrelated text value on the
other unless the expression language explicitly supports the conversion.

### Example A --- Pass/fail

``` text
IIF(SCORE >= 40, 'PASS', 'FAIL')
```

### Example B --- Discount

``` text
IIF(ORDER_AMOUNT >= 10000, ORDER_AMOUNT * 0.10, 0)
```

Output datatype should support the decimal result.

### Example C --- Status normalization

``` text
IIF(STATUS = 'A', 'ACTIVE', 'INACTIVE')
```

This assumes all non-`A` values should be inactive. If NULL, blank, or
unexpected statuses require separate handling, use a more explicit
expression.

## 6. Nested `IIF`

A nested `IIF` places one conditional expression inside another. Use it
when there are several mutually exclusive categories.

Example: price band

``` text
IIF(UNIT_PRICE >= 1000, 'PREMIUM',
    IIF(UNIT_PRICE >= 500, 'MID',
        'BUDGET'
    )
)
```

Evaluation order: 1. If price is at least 1000, return `PREMIUM`. 2.
Otherwise, if price is at least 500, return `MID`. 3. Otherwise, return
`BUDGET`.

The order matters. Put the most restrictive/highest threshold first. If
the `>= 500` test came first, a price of 1200 would return `MID`, never
reaching the premium test.

### Example --- Employee category

``` text
IIF(SALARY >= 10000, 'SENIOR',
    IIF(SALARY >= 5000, 'MID',
        IIF(SALARY >= 0, 'JUNIOR', 'INVALID')
    )
)
```

Keep deeply nested expressions readable with indentation. If the logic
becomes difficult to test, create intermediate output/variable ports or
split it across multiple Expression transformations.

## 7. Combining `IIF`, `AND`, `OR`, and `NOT`

Example: classify a product as eligible only when it is active and has
stock:

``` text
IIF(PRODUCT_STATUS = 'ACTIVE' AND STOCK_QTY > 0,
    'ELIGIBLE',
    'NOT_ELIGIBLE'
)
```

Example: allow products in either of two categories:

``` text
IIF((CATEGORY = 'ELECTRONICS' OR CATEGORY = 'HOME')
    AND PRODUCT_STATUS = 'ACTIVE',
    'IN_SCOPE',
    'OUT_OF_SCOPE'
)
```

Example: flag records that are not active:

``` text
IIF(NOT (PRODUCT_STATUS = 'ACTIVE'), 'CHECK', 'OK')
```

Use parentheses whenever AND/OR conditions are mixed. They make the
intended rule explicit.

## 8. NULL handling --- a critical topic

A NULL is not the same as zero, an empty string, or the text `'NULL'`.

-   `0` is a numeric value.
-   `''` is an empty string (depending on source and connector
    semantics).
-   `'NULL'` is four literal characters.
-   `NULL` means the value is missing/unknown.

Comparisons involving NULL often do not behave like ordinary true/false
comparisons. Avoid assuming that `FIELD = NULL` is a valid way to test
for a missing value. Use the NULL-checking function supported by the
IDMC expression editor, commonly `ISNULL(field)`, and verify the exact
function signature in your environment.

### Example --- Default a missing commission

Conceptual pattern:

``` text
IIF(ISNULL(COMMISSION), 0, COMMISSION)
```

This handles NULL commission values, but not necessarily blank text such
as `'   '`. For string fields, trim first or explicitly test for blank
values as appropriate to the source.

### Example --- Missing product status

``` text
IIF(ISNULL(PRODUCT_STATUS), 'UNKNOWN', PRODUCT_STATUS)
```

### Example --- NULL-safe comparison

For source-to-target comparisons, compare normalized values rather than
relying on ordinary equality when either side can be NULL.

For a text field, conceptually normalize both values:

``` text
IIF(ISNULL(SRC_PRODUCT_NAME), '<MISSING>', SRC_PRODUCT_NAME)
```

and apply the same normalization to the target-side value, then compare
them. Choose a sentinel value that cannot be a legitimate business
value, or use explicit NULL-state checks. Do not casually use a common
value such as `0` or an empty string as a sentinel if it may be valid
data.

A robust comparison needs to distinguish: 1. both values are NULL →
unchanged; 2. exactly one value is NULL → changed; 3. both are non-NULL
and equal → unchanged; 4. both are non-NULL and different → changed.

Always test NULL behavior using representative data in your actual
mapping mode and connector combination.

## 9. String functions and standardization

Function names and argument support can vary by expression language and
connector. Confirm available functions in the IDMC expression editor.

Commonly used string operations include: - `TRIM(field)` --- remove
leading/trailing spaces. - `UPPER(field)` --- convert text to
uppercase. - `LOWER(field)` --- convert text to lowercase. -
`LENGTH(field)` --- get the string length, where supported. -
Concatenation --- use the concatenation operator/function supported by
the editor.

Examples:

``` text
UPPER(TRIM(CUSTOMER_NAME))
LOWER(TRIM(EMAIL))
```

A practical email cleanup output:

``` text
LOWER(TRIM(EMAIL))
```

This standardizes casing and surrounding whitespace. It does not
validate whether the email address is real or correctly formed.

## 10. Numeric functions, precision, and division

Common numeric operations:

``` text
QUANTITY * UNIT_PRICE
GROSS_AMOUNT - DISCOUNT_AMOUNT
```

Be careful with: - Integer vs decimal datatypes. - Precision and scale
of calculated output ports. - Division by zero. - Rounding rules. -
Numeric strings arriving from flat files.

Example: calculate an amount:

``` text
QUANTITY * UNIT_PRICE
```

Set the output port to a suitable decimal type/precision so that cents
are not lost.

Before dividing, ensure the denominator cannot be zero. One possible
conditional pattern is:

``` text
IIF(QUANTITY = 0, 0, TOTAL_AMOUNT / QUANTITY)
```

Use this only if returning zero for a zero quantity is the correct
business rule. Sometimes the better result is NULL, a reject, or a
separate error flag.

## 11. Date and datatype conversion

Source systems can deliver dates and numbers in different formats. A
flat-file date may arrive as text, while a database column may already
be typed as DATE/TIMESTAMP.

Rules: 1. Inspect the incoming datatype. 2. Use the conversion function
supported by the mapping's expression language. 3. Ensure the input
format matches the actual source format. 4. Decide how invalid values
should be handled. 5. Set the output datatype appropriately.

Do not copy a conversion function signature from a different Informatica
product or mapping mode without checking it in IDMC. Date parsing,
formatting, and casting support can differ by context.

## 12. Lookup-driven expressions

A Lookup can bring existing target attributes into the mapping. A
following Expression can compare incoming source values with the
looked-up values.

Example fields: - Source: `PRODUCT_ID`, `PRODUCT_NAME`, `CATEGORY`,
`UNIT_PRICE`, `STOCK_QTY`, `PRODUCT_STATUS` - Lookup output: existing
target values for the same product ID.

The Expression then derives an action: - No target match → `INSERT` -
Match and tracked attributes differ → `UPDATE` - Match and tracked
attributes are the same → `NO_CHANGE`

Important: use the Lookup's actual match indicator/output behavior for
your configured Lookup. Do not assume that a missing row always appears
as a particular numeric value. Configure and test the not-found behavior
explicitly.

## 13. SCD Type 1 --- derive `RECORD_ACTION`

**SCD Type 1** overwrites changed attribute values in the target. It
does not preserve previous versions of those attributes.

Assume: - Business key: `PRODUCT_ID` - Tracked attributes:
`PRODUCT_NAME`, `CATEGORY`, `UNIT_PRICE`, `STOCK_QTY`,
`PRODUCT_STATUS` - Lookup identifies whether the product exists.

The following is **pseudocode** to illustrate the decision logic;
replace `LOOKUP_FOUND` with the actual not-found/match indicator exposed
by your IDMC Lookup:

``` text
IIF(NOT LOOKUP_FOUND, 'INSERT',
    IIF(
        SOURCE_NAME differs from TARGET_NAME
        OR SOURCE_CATEGORY differs from TARGET_CATEGORY
        OR SOURCE_PRICE differs from TARGET_PRICE
        OR SOURCE_STOCK differs from TARGET_STOCK
        OR SOURCE_STATUS differs from TARGET_STATUS,
        'UPDATE',
        'NO_CHANGE'
    )
)
```

The phrase `differs from` is explanatory, not literal IDMC syntax.
Implement each comparison with valid expressions and explicit NULL
handling.

### SCD Type 1 workflow

1.  Read the source records.
2.  Lookup target by `PRODUCT_ID`.
3.  Derive `RECORD_ACTION`.
4.  Route or filter by action.
5.  Insert new keys.
6.  Update existing keys when tracked attributes change.
7.  Ignore or audit unchanged records, according to requirements.

Do not update every matched row if the goal is to update only changed
records. A change flag can reduce unnecessary writes and make audit
results clearer.

### Practical test data

    Product ID Source state                               Expected action
  ------------ ------------------------------------------ -----------------
           101 Exists in target; price changed            `UPDATE`
           102 Exists; all tracked attributes unchanged   `NO_CHANGE`
           103 Exists; one tracked attribute changed      `UPDATE`
           104 Does not exist in target                   `INSERT`
           105 Does not exist in target                   `INSERT`

This matches the common practice pattern where IDs 101--103 are already
in `PRODUCT_MASTER` and source rows 104--105 are new. Actual output
depends on the data loaded and which attributes you track.

## 14. SCD Type 2 --- derive the action

**SCD Type 2** preserves history by expiring the current version and
inserting a new version when a tracked attribute changes. A typical
target has fields such as: - Business key: `PRODUCT_ID` -
Version/surrogate key (if used) - Tracked attributes -
`EFFECTIVE_START_DATE` - `EFFECTIVE_END_DATE` - `IS_CURRENT`

For a product key: - No current target version → insert the first
version. - Current version exists and tracked attributes are unchanged →
no change. - Current version exists and tracked attributes changed →
expire the old version and insert a new current version.

Conceptual action logic:

``` text
IIF(NO_CURRENT_MATCH, 'INSERT',
    IIF(TRACKED_ATTRIBUTES_CHANGED, 'EXPIRE_AND_INSERT', 'NO_CHANGE')
)
```

This is a business-logic illustration, not a literal complete
expression. Implement `NO_CURRENT_MATCH` using the configured Lookup's
actual match/current-row indicators, and implement
`TRACKED_ATTRIBUTES_CHANGED` with valid, NULL-safe comparisons.

### SCD Type 2 example

Before: \| PRODUCT_ID \| PRODUCT_NAME \| UNIT_PRICE \| IS_CURRENT \|
EFFECTIVE_END_DATE \| \|---:\|---\|---:\|---\|---\| \| 101 \| Wireless
Mouse \| 20.00 \| Y \| NULL \|

Incoming source: \| PRODUCT_ID \| PRODUCT_NAME \| UNIT_PRICE \|
\|---:\|---\|---:\| \| 101 \| Wireless Mouse \| 24.00 \|

Expected result after processing: \| PRODUCT_ID \| PRODUCT_NAME \|
UNIT_PRICE \| IS_CURRENT \| Version result \|
\|---:\|---\|---:\|---\|---\| \| 101 \| Wireless Mouse \| 20.00 \| N \|
Old version expired \| \| 101 \| Wireless Mouse \| 24.00 \| Y \| New
current version inserted \|

In practice, the target may use a separate surrogate key to distinguish
versions. The business key can repeat across historical rows.

### Important SCD Type 2 implementation note

An Expression does not itself expire and insert database rows. It only
derives values/flags. The mapping must implement the actual target
operations---for example, routing to an update/expire path and an insert
path, using an appropriate target strategy or separate processing flow
supported by your IDMC setup. Verify how the mapping handles multiple
output paths and target writes before implementing it.

## 15. Expression vs Filter vs Router

  -----------------------------------------------------------------------
  Requirement             Best fit                Why
  ----------------------- ----------------------- -----------------------
  Calculate `NET_AMOUNT`  Expression              Derives a value

  Label a row `HIGH` or   Expression with `IIF`   Adds a classification
  `LOW`                                           

  Drop rows with invalid  Filter                  Removes nonmatching
  status                                          rows

  Send inserts and        Router or separate      Branches records
  updates to different    conditional paths       
  targets                                         

  Compare source          Expression after Lookup Derives change action
  attributes to lookup                            
  values                                          

  Preserve historical     SCD Type 2 processing   Requires
  versions                design                  expire-and-insert
                                                  behavior, not just an
                                                  expression
  -----------------------------------------------------------------------

## 16. Common mistakes and debugging checklist

### Mistake 1: Wrong datatype

A numeric output may be defined as text, or a decimal result may be
assigned to an integer output.

**Fix:** Inspect input and output datatypes, precision, and scale.

### Mistake 2: Incompatible `IIF` branches

For example, returning a number in one branch and an incompatible string
in the other.

**Fix:** Return compatible datatypes and use explicit conversions when
appropriate.

### Mistake 3: Incorrect nested condition order

A broad condition is evaluated before a more specific one.

**Fix:** Put the highest/specific threshold first and test boundary
values.

### Mistake 4: NULLs treated like ordinary values

A direct comparison may not detect a change when one side is NULL.

**Fix:** Use explicit NULL-state logic and test all four cases: both
NULL, source NULL, target NULL, neither NULL.

### Mistake 5: Using `IIF` to remove rows

An `IIF` creates a value; it does not discard the row.

**Fix:** Use Filter for row elimination or Router for multiple branches.

### Mistake 6: Incorrect Lookup not-found assumption

The action expression assumes a particular default value for a missing
Lookup result.

**Fix:** Confirm the actual configured not-found behavior and test with
a key absent from the target.

### Mistake 7: Forgetting a tracked attribute

A change in an omitted attribute does not trigger the action.

**Fix:** Maintain an explicit list of tracked attributes and align it
with the SCD business requirement.

### Mistake 8: SCD Type 2 only updates the row

Overwriting the old row destroys the history you meant to preserve.

**Fix:** Expire the current row and insert a new version for a changed
business key.

### Mistake 9: Copying function syntax from another Informatica mode

Expression functions can vary by product/mapping context.

**Fix:** Use the function picker/help in your IDMC expression editor and
validate a small expression first.

## 17. Practice exercises

Try these before reading the answer key.

1.  Create `SALARY_BAND`: `HIGH` for salary \>= 8000, `MEDIUM` for
    salary \>= 4000, otherwise `LOW`.
2.  Create `PRODUCT_STATUS_NORM`: use `UNKNOWN` when status is NULL;
    otherwise preserve the status.
3.  Create `ELIGIBILITY`: `YES` only when status is `ACTIVE` and stock
    is greater than zero.
4.  Create `EMAIL_NORMALIZED` by trimming spaces and converting text to
    lowercase.
5.  Calculate `UNIT_TOTAL = UNIT_PRICE * STOCK_QTY`.
6.  Derive `RECORD_ACTION` for SCD1: new key → insert, changed tracked
    attribute → update, otherwise no change.
7.  Derive the conceptual SCD2 action: no current row → insert; changed
    current row → expire-and-insert; otherwise no change.
8.  Explain why an Expression cannot, by itself, remove a row or
    guarantee SCD2 history.

### Answer key

1.  Nested `IIF`:

``` text
IIF(SALARY >= 8000, 'HIGH',
    IIF(SALARY >= 4000, 'MEDIUM', 'LOW')
)
```

2.  NULL status:

``` text
IIF(ISNULL(PRODUCT_STATUS), 'UNKNOWN', PRODUCT_STATUS)
```

Confirm `ISNULL` availability/signature in the expression editor for
your mapping mode.

3.  Eligibility:

``` text
IIF(PRODUCT_STATUS = 'ACTIVE' AND STOCK_QTY > 0, 'YES', 'NO')
```

4.  Email normalization:

``` text
LOWER(TRIM(EMAIL))
```

5.  Unit total:

``` text
UNIT_PRICE * STOCK_QTY
```

Choose a decimal output datatype that can hold the result.

6.  SCD1 concept:

``` text
IIF(NO_TARGET_MATCH, 'INSERT',
    IIF(TRACKED_ATTRIBUTES_CHANGED, 'UPDATE', 'NO_CHANGE')
)
```

Replace placeholders with actual Lookup indicators and valid NULL-safe
comparisons.

7.  SCD2 concept:

``` text
IIF(NO_CURRENT_MATCH, 'INSERT',
    IIF(TRACKED_ATTRIBUTES_CHANGED, 'EXPIRE_AND_INSERT', 'NO_CHANGE')
)
```

8.  Expression calculates values for rows. Filter discards rows, Router
    branches them, and SCD2 needs target processing that expires an old
    version and inserts a new version.

## 18. Mock interview questions

1.  What is an Expression transformation in IDMC?
2.  What is the difference between an Expression and a Filter?
3.  Explain `IIF` with a business example.
4.  What is nested `IIF`, and why does condition order matter?
5.  How do you combine `AND` and `OR` safely?
6.  Why should NULL handling be explicit?
7.  How would you normalize an email field?
8.  How would you calculate a derived amount and avoid losing decimal
    precision?
9.  How does an Expression work with a Lookup for SCD Type 1?
10. What are the possible `RECORD_ACTION` values in an SCD1 flow?
11. How is SCD Type 2 different from SCD Type 1?
12. Why is `EXPIRE_AND_INSERT` a processing design rather than just an
    Expression?
13. What can cause an expression to fail validation?
14. How do you debug an expression that validates but produces
    unexpected values?
15. How do you test a NULL-safe source-to-target comparison?

## 19. Suggested testing matrix

For conditional logic, test boundaries and unusual values---not only
normal records.

  -----------------------------------------------------------------------
  Test case               Example                 What to verify
  ----------------------- ----------------------- -----------------------
  Below threshold         Salary 3999             Correct lower band

  At threshold            Salary 4000             Boundary is
                                                  inclusive/exclusive as
                                                  intended

  Above threshold         Salary 8000             Most specific band wins

  NULL input              NULL status             Expected default/action

  Blank input             `'   '`                 Whether
                                                  trimming/defaulting is
                                                  required

  Lookup miss             New product ID          Insert action

  Exact match             Same tracked values     No-change action

  One changed field       Price differs           Update or
                                                  expire-and-insert

  Source NULL, target     Missing incoming        Detected as a change if
  non-NULL                attribute               business rules say so

  Source non-NULL, target Previously missing      Detected as a change if
  NULL                    target attribute        business rules say so
  -----------------------------------------------------------------------

## 20. Module summary

-   Expression derives values; Filter removes rows; Router branches
    rows.
-   `IIF(condition, true_value, false_value)` is the core conditional
    pattern.
-   Nested `IIF` is useful for ordered categories, but condition order
    matters.
-   Parentheses make mixed `AND`/`OR` logic clear.
-   NULLs, datatypes, precision, and missing Lookup matches need
    deliberate handling.
-   For SCD1, update changed attributes in place.
-   For SCD2, preserve history by expiring the current version and
    inserting a new version.
-   An action flag such as `RECORD_ACTION` describes what should happen;
    target operations must still implement that action.
-   Always verify exact function names and signatures in the IDMC
    expression editor for your mapping mode.

**Next module:** Lookup Transformation --- connected vs unconnected
Lookup, lookup conditions, return values, caching, cache behavior,
dynamic lookup concepts where supported, and practical SCD patterns.
