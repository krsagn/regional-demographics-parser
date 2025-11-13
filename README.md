# regional-demographics-parser

This Python script processes two CSV datasets containing Australian Statistical Area information (SA2 and SA3) and age-grouped population counts.
The program validates, cleans, and analyses the data to produce three structured outputs summarising population distributions across states, SA3 regions, and SA2 areas.

> This project was originally developed as part of a university assignment (CITS1401 – Computational Thinking with Python, UWA).

---

## Input Files

The program reads **two CSV files** passed as arguments to the `main()` function:

1. **Areas File (csvfile_1)**  
   Contains relationships between:
   - State codes and names  
   - SA3 codes and names  
   - SA2 codes and names  

   The first row contains headings.  
   A sample file is provided: `SampleData_Areas.csv`.

2. **Populations File (csvfile_2)**  
   Contains population counts for each SA2 area broken down by age group.  
   The first row contains headings.  
   A sample file is provided: `SampleData_Populations.csv`.

The program must accept any valid file name (no assumptions about `.csv` extensions).

---

## Constraints

The implementation follows these constraints:

- **No external/internal modules**  
  External or internal modules (including `csv`, `math`, etc.) cannot be used.

- **No `input()` calls**  
  The program must never request user input.

- **No `print()` output except for graceful termination**  
  All normal results must be returned, not printed.

- **Graceful termination**  
  On invalid input or unrecoverable error, the program must:
  - print a short message
  - return zero / `None` / empty list / empty dictionary appropriately

---

## Outputs

### OP1: Largest Population by Age Group

A dictionary:

```
{
  'lower-upper': [
      largest_state_name,
      largest_sa3_name,
      largest_sa2_name
  ],
  ...
}
```

Where:

1. Keys are age groups like `'0-9'`, `'10-19'`, `'80-None'`.  
2. Values list the state, SA3, and SA2 with the largest population for that age group.  
3. Sorting ties are broken alphabetically (treating codes as strings).
  
### OP2: High-Population SA3 Areas (≥150000)

A nested dictionary:

```
{
  state_code: {
      sa3_code: [
          sa2_code_with_largest_pop,
          population_of_that_sa2,
          std_dev_across_age_groups
      ],
      ...
  },
  ...
}
```
Where:

1. Inner keys include only SA3 areas with total population ≥ 150000.  
   For each such SA3:
    - Identify the SA2 area with the largest population.
    - Compute the standard deviation of its age-group populations.
2. Sorting ties are broken by alphabetical ordering of area codes.
3. If no qualifying SA3 exists, the inner dictionary is empty.
  
### OP3: Most Similar SA2 Areas (Cosine Similarity)

A dictionary:

```
{
  sa3_name: [
      sa2_name_1,
      sa2_name_2,
      cosine_similarity
  ],
  ...
}
```

Where:

1. Only includes SA3 areas containing **15 or more** SA2 regions.
2. For each such SA3, find the pair of SA2 areas with the highest cosine similarity based on their age-group *percentage distributions*.
3. SA2 area names are alphabetically ordered in the pair.
4. Cosine similarity is rounded to four decimal places.

---

## Data Cleaning

Before calculations, the program:

- Ignores rows with missing values
- Ignores negative populations
- Removes all duplicated rows (and corresponding rows in the other file)
- Treats all strings case-insensitively
- Allows varying age group formats
- Does not assume column order

All numeric outputs are rounded **only at the end**, to 4 decimal places.

---

## Mathematical Methods Used

- **Cosine Similarity** for comparing SA2 demographic distributions
- **Sample Standard Deviation** across age groups for OP2 results

---

## Example Usage

```
OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')
```

Sample area and population CSV files are provided in the repository.

---

## Notes
*__Note:__ For demonstration purposes, a small test block was included at the bottom of the file using `pprint` and hard-coded filenames. This block is **not part of the `main()` function** and was used only to display the outputs while developing. The required function `main(csvfile_1, csvfile_2)` itself does not call `print()` and follows all project constraints.*
